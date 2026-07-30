from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Translation(object):

    START_TEXT = """🤣👋 Hello <b>{}</b> 
<blockquote>
I'm a Telegram URL Uploader Bot 
Send me a direct link and I'll upload it to Telegram  
as a file or video.
</blockquote>
<b>Use the help button to learn how to use me!</b>
"""

    

    HELP_TEXT = """
<b>How To Use This Bot</b> 🤔
<blockquote>
• Go to /settings and customize the bot as you like  
• Send me a custom thumbnail to save it permanently  
• Send link like this:  
  https://example.com/file.mp4 | New Name.mkv 
• Choose the desired upload option  
• Reply to any media with `/caption` + your text to set a caption
</blockquote>
"""
    
    ABOUT_TEXT = """
╭───────────────⍟
│ | 🤖 **Bot Name** : Urlupdate 45TSY
| 🚀 **Framework** : <a href="https://docs.pyrogram.org/">PyroBlock 2.7.5</a>
| 🖥 **Language** : <a href="https://www.python.org">Python 3.13.12</a>
| 📀 **Database** : <a href="https://cloud.mongodb.com">MongoDB</a>
| 📌 **Support** : <a href="https://t.me/KAKADAROTHKH01">Support</a>
| 👥 **Group** : <a href="https://t.me/Urlupdate20t">Group</a>
| 📢 **Channel** : <a href="https://t.me/Urlupdate45tsy">Channel</a>
| 👑 **Owner** : @KAKADAROTH
        """
START_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('🛠 Settings', callback_data='OpenSettings')
        ],[
            InlineKeyboardButton('🤝 Help', callback_data='help'),
            InlineKeyboardButton('ℹ️ About', callback_data='about')
        ],[
            InlineKeyboardButton('✖️ Close', callback_data='close')
        ]]
    )

    HELP_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('🛠 Settings', callback_data='OpenSettings')
        ],[
            InlineKeyboardButton('⬅️ Back', callback_data='home'),
            InlineKeyboardButton('ℹ️ About', callback_data='about')
        ],[
            InlineKeyboardButton('✖️ Close', callback_data='close')
        ]]
    )

    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('🛠 Settings', callback_data='OpenSettings')
        ],[
            InlineKeyboardButton('⬅️ Back', callback_data='home'),
            InlineKeyboardButton('🤝 Help', callback_data='help')
        ],[
            InlineKeyboardButton('✖️ Close', callback_data='close')
        ]]
)
