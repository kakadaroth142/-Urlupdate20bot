import os
import re
import asyncio
import logging
import requests
import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, DOWNLOAD_FOLDER

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def is_direct_link(url):
    url = url.lower()
    return (
        ".mp4" in url
        or ".m3u8" in url
        or ".ts" in url
    )


async def download_video(url, quality="720"):
    try:

        if is_direct_link(url):

            filename = os.path.join(
                DOWNLOAD_FOLDER,
                "video.mp4"
            )

            r = requests.get(
                url,
                stream=True,
                timeout=60,
            )

            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024 * 512):
                    if chunk:
                        f.write(chunk)

            return {
                "ok": True,
                "title": "Direct Video",
                "file": filename,
            }

        opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(
                DOWNLOAD_FOLDER,
                "%(title)s.%(ext)s",
            ),
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

        loop = asyncio.get_event_loop()

        with yt_dlp.YoutubeDL(opts) as ydl:

            info = await loop.run_in_executor(
                None,
                lambda: ydl.extract_info(
                    url,
                    download=True,
                ),
            )

            filename = ydl.prepare_filename(info)

            if not filename.endswith(".mp4"):
                base = os.path.splitext(filename)[0]

                if os.path.exists(base + ".mp4"):
                    filename = base + ".mp4"

            return {
                "ok": True,
                "title": info.get(
                    "title",
                    "Video",
                ),
                "file": filename,
            }

    except Exception as e:

        logging.exception(e)

        return {
            "ok": False,
            "error": str(e),
        }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎬 <b>Video Downloader Bot</b>\n\n"
        "📥 Send me a video URL.\n\n"
        "✅ Supported:\n"
        "• YouTube\n"
        "• Facebook\n"
        "• TikTok\n"
        "• Instagram\n"
        "• Rumble\n"
        "• Direct MP4 / M3U8 / TS\n\n"
        "Use /help for more information."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>How to use</b>\n\n"
        "1. Send a video URL.\n"
        "2. Select the quality.\n"
        "3. Wait for download.\n"
        "4. The bot will upload the video automatically.\n",
        parse_mode="HTML",
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    url = update.message.text.strip()

    if not re.match(r"^https?://", url):
        await update.message.reply_text(
            "❌ Please send a valid URL."
        )
        return

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton(
                "480p ⚡",
                callback_data="480",
            ),
            InlineKeyboardButton(
                "720p ⭐",
                callback_data="720",
            ),
        ],
        [
            InlineKeyboardButton(
                "1080p 🎥",
                callback_data="1080",
            ),
        ],
    ]

    await update.message.reply_text(
        "📺 Choose video quality:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
    )


async def button_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    quality = query.data
    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text(
            "❌ URL not found.\nPlease send the link again."
        )
        return

    await query.edit_message_text(
        f"⏳ Downloading ({quality}p)..."
    )

    result = await download_video(url, quality)

    if not result["ok"]:
        await query.message.reply_text(
            f"❌ Download failed!\n\n{result['error']}"
        )
        return

    file_path = result["file"]
    title = result["title"]

    try:
        await query.message.reply_text(
            "📤 Uploading to Telegram..."
        )

        file_size = os.path.getsize(file_path)

        with open(file_path, "rb") as video:

            # Telegram video upload limit
            if file_size < 49 * 1024 * 1024:
                await query.message.reply_video(
                    video=video,
                    caption=title,
                    supports_streaming=True,
                )
            else:
                await query.message.reply_document(
                    document=video,
                    caption=title,
                )

        if os.path.exists(file_path):
            os.remove(file_path)

        await query.message.reply_text(
            "✅ Done!"
        )

    except Exception as e:

        if os.path.exists(file_path):
            os.remove(file_path)

        await query.message.reply_text(
            f"❌ Upload failed!\n\n{e}"
        )


def run_bot():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_cmd,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_callback,
        )
    )

    print("✅ Bot is running...")

    app.run_polling(
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    run_bot()