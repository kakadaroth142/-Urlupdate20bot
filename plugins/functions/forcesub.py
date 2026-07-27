import os
import asyncio
from plugins.config import Config
from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def normalize_channel(raw):
    """
    Accepts UPDATES_CHANNEL in any of these formats and returns something
    Pyrogram's get_chat / get_chat_member can use:
      - Full URL:      "https://t.me/Urlupdate20"
      - @username:      "@Urlupdate20"
      - Plain username: "Urlupdate20"
      - Numeric ID:      -1004476935797 or "Urlupdate20"
    """
    raw = str(raw).strip()

    if raw.startswith("https://t.me/") or raw.startswith("http://t.me/") or raw.startswith("t.me/"):
        raw = raw.split("t.me/", 1)[1]

    raw = raw.strip("/")

    if raw.startswith("@"):
        return raw

    # Numeric channel ID (can be negative for supergroups/channels)
    try:
        return int(raw)
    except ValueError:
        return raw  # plain username, e.g. "Urlupdate20"


async def handle_force_subscribe(bot, message):
    if not Config.UPDATES_CHANNEL:
        return  # No force-sub channel set — allow bot to be used freely
            

    channel = normalize_channel(Config.UPDATES_CHANNEL)

    try:
        # Generate the invite link dynamically instead of hardcoding it
        try:
            chat = await bot.get_chat(channel)
            if chat.username:
                invite_link_url = f"https://t.me/{chat.username}"
            else:
                invite_link_url = await bot.export_chat_invite_link(channel)
        except FloodWait as f:
            await asyncio.sleep(f.value)
            invite_link_url = await bot.export_chat_invite_link(channel)

        user = await bot.get_chat_member(channel, message.from_user.id)
        if user.status == "kicked":
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Sorry, you are banned from using this bot.",
                disable_web_page_preview=True,
            )
            return 400

    except UserNotParticipant:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Please join the Updates Channel to use this bot!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Join Channel", url=invite_link_url)],
                    [InlineKeyboardButton("Refresh", callback_data="refreshForceSub")],
                ]
            ),
        )
        return 400

    except ChatAdminRequired:
        print("FORCESUB ERROR: Bot is not an admin in the updates channel.")
        await bot.send_message(
            chat_id=message.from_user.id,
            text="The bot is not properly configured to check channel membership. Please contact the admin.",
            disable_web_page_preview=True,
        )
        return 400

    except PeerIdInvalid:
        print(f"FORCESUB ERROR: Invalid channel ID/username: {channel!r} (from Config.UPDATES_CHANNEL={Config.UPDATES_CHANNEL!r})")
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Updates channel is misconfigured. Please contact the admin.",
            disable_web_page_preview=True,
        )
        return 400

    except FloodWait as f:
        await asyncio.sleep(f.value)
        return await handle_force_subscribe(bot, message)

    except Exception as e:
        print(f"FORCESUB ERROR: {e}")
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"An unexpected error occurred: {e}",
            disable_web_page_preview=True,
        )
        return 400
