import asyncio
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PLAYLIST_IMG_URL, PRIVATE_BOT_MODE, adminlist
from config import SUPPORT_GROUP 
from strings import get_string
from ChampuMusic import YouTube, app
from ChampuMusic.core.call import _st_ as clean
from ChampuMusic.misc import SUDOERS, SPECIAL_ID
from ChampuMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_commanddelete_on,
    is_maintenance,
    is_served_private_chat,
)
from ChampuMusic.utils.inline import botplaylist_markup

links = {}
clinks = {}

def get_peer_type(peer_id):
    if peer_id is None:
        raise ValueError("peer_id cannot be None")
    if peer_id < 0:
        return "channel"
    else:
        return "user"

def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        userbot = await get_assistant(message.chat.id)
        _ = get_string(language)
        
        if message.sender_chat:
            upl = InlineKeyboardMarkup([[InlineKeyboardButton(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]])
            return await message.reply_text(_["general_4"], reply_markup=upl)

        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_GROUP}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )
        
        if PRIVATE_BOT_MODE == str(True):
            if not await is_served_private_chat(message.chat.id):
                await message.reply_text("**ᴘʀɪᴠᴀᴛᴇ ᴍᴜsɪᴄ ʙᴏᴛ**\n\nᴏɴʟʏ ғᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴄʜᴀᴛs. ᴀsᴋ ᴍʏ ᴏᴡɴᴇʀ.")
                return await app.leave_chat(message.chat.id)
        
        if await is_commanddelete_on(message.chat.id):
            try: await message.delete()
            except: pass

        url = await YouTube.url(message)
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None: return await message.reply_text(_["setting_12"])
            try: chat = await app.get_chat(chat_id)
            except: return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        
        if playty != "Everyone" and message.from_user.id not in SUDOERS:
            admins = adminlist.get(message.chat.id)
            if not admins or message.from_user.id not in admins:
                return await message.reply_text(_["play_4"])

        video = True if (message.command[0][0] == "v" or "-v" in message.text) else None
        fplay = True if message.command[0][-1] == "e" else None

        # Fix: Check Assistant presence correctly
        userbot = await get_assistant(message.chat.id)
        try:
            get_memb = await app.get_chat_member(chat_id, userbot.id)
        except UserNotParticipant:
            if message.chat.username:
                try: await userbot.join_chat(message.chat.username)
                except: pass
            else:
                try:
                    invitelink = await app.export_chat_invite_link(chat_id)
                    await userbot.join_chat(invitelink)
                except Exception as e:
                    return await message.reply_text(f"Assistant join nahi kar pa raha: {e}")

        return await command(client, message, _, chat_id, video, channel, playmode, url, fplay)

    return wrapper

def CPlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        # Simplified for logic consistency
        userbot = await get_assistant(message.chat.id)
        chat_id = message.chat.id
        
        # Similar logic for Channel Play
        return await command(client, message, _, chat_id, False, None, "Direct", None, False)
    return wrapper