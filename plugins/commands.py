import imp
import os
from datetime import datetime,  timedelta
from time import time
import time as t
import pytz
import logging
import pyrogram
import random
import asyncio
from Script import script
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, RP_CHANNEL, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, START_IMAGE_URL
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
import re
import json
import base64
logger = logging.getLogger(__name__)

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("Week", 60 * 60 * 24 * 7),
    ("Day", 60 ** 2 * 24),
    ("hour", 60 ** 2),
    ("Min", 60),
    ("Sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else ""))
    return " | ".join(parts)

BATCH_FILES = {}

Stick = ["CAACAgUAAxkBAALSkWFrzXHCWiSe6KthcfSpStf3VFKvAALTAgAC4PFYV8SuvilphYwOIQQ", "CAACAgUAAxkBAALSjWFrzVpaU35rry9hNVJ-ikzQ-0nAAAJpBQACJAJgV4OBsbRyyhiVIQQ", "CAACAgUAAxkBAALSiWFrzUuO_ZLAC1lTW_0Opx4-8m0CAAL4BAAC4iNgV6UQKGHw-9nIIQQ", "CAACAgUAAxkBAALShWFrzSlyx75BpPDr6j28jQ3XIHtuAAIPBAACUrxZV8pAkWSn-llgIQQ", "CAACAgUAAxkBAALSfWFrzQeo-XDcIkNRwrPsIo1EvozfAAKqAwACC3ZhV5IVoSCActrZIQQ", "CAACAgUAAxkBAALSeWFrzPP7oqXJm8hhOBktpNO7oUJhAAKwAwAC-7lZV_E905v9J7kcIQQ", "CAACAgUAAxkBAALSdWFrzOB4wWTUBxjO_8DJvPXDmvYLAALXBAACUVtgVyYcCFkutVG3IQQ", "CAACAgUAAxkBAALScWFrzMKS3016FlITwLEI-Nlr9h_fAAKcAwACCSFhV8rHwH4346VYIQQ", "CAACAgUAAxkBAALSbWFrzK658Cw6yhTxOpJJLo9VOhtoAAJ-AwACf5tgVyDXkMXEVEkbIQQ", "CAACAgUAAxkBAALSaWFrzJwrl25mssz1h3Jkd9SC33I5AAKeAwACmOFYVxteE1qjKmAbIQQ", "CAACAgUAAxkBAALSZWFrzItxznpnWNKZb8ClDdCKSrknAALYAwAC9aVgV5ke2o8sr4eJIQQ", "CAACAgUAAxkBAALSWWFry_onO6WM8IzNFdatHO7I0NHpAALtAwACNvhhV9DJoVRnDoqXIQQ", "CAACAgUAAxkBAALSXWFrzF7i3HIbQjwcLgsxvroQCM37AAKQBAAC5oRgV487WnEkLJMhIQQ","CAACAgUAAxkBAALSYWFrzHP8kwaJ9HHL8BpS7EGzS-eFAAJnAwAC2C1gV8_sTGH4iWtuIQQ",]
Kumatti = ["CAACAgEAAxkBAAFcDUBhoZ7gPWvdhHSRD-TofdEG7tf95wAC2wEAAnuK0EWF9EMPRHczpCIE", "CAACAgEAAxkBAAFcDSZhoZ0XwWX2gN0gayGXtTaH9rtJagAC5QEAAmiv0EUaNsNeiq6UdiIE"]


@Client.on_message(filters.command("start") & (filters.private))
async def start(client, message):
    m = datetime.now()

    time = m.hour

    if time < 6:
        get="Gᴏᴏᴅ Mᴏʀɴɪɴɢ" 
    elif time < 12:
        get="Gᴏᴏᴅ Aғᴛᴇʀɴᴏᴏɴ"
    elif time < 17:
        get="Gᴏᴏᴅ Eᴠᴀɴɪɴɢ"
    elif time < 20: 
        get="Gᴏᴏᴅ Nɪɢʜᴛ"
    else:
        get="Gᴏᴏᴅ Nɪɢʜᴛ"

    if message.chat.type in ['group', 'supergroup']:
        fuc = await message.reply_sticker(sticker=random.choice(Kumatti))
        await asyncio.sleep(2)
        await message.delete()
        await fuc.delete()# 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('ᴄʟɪᴄᴋ ʜᴇʀᴇ ғᴏʀ ᴍᴏʀᴇ ʙᴜᴛᴛᴏɴs', callback_data='start'),
            #InlineKeyboardButton('ɢʀᴏᴜᴘ', callback_data='group')
            #],[
            #InlineKeyboardButton('ꜱᴏᴜʀᴄᴇ', callback_data='owner'),
            #InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='group')
            #],[
            #InlineKeyboardButton('ᴊᴏɪɴ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ', url='https://t.me/Mallubros')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        chat_id=message.from_user.id
        await message.delete(True)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=f"""<b>{get} {message.from_user.mention}
    
Sᴏʀʀʏ ɪ ᴏɴʟʏ ᴡᴏʀᴋ ᴏɴ <a href=https://t.me/cinimaadholokaam>CɪɴɪᴍᴀAᴅʜᴏʟᴏᴋᴀᴍ</a> Gʀᴏᴜᴘ. Nᴏ ᴏᴛʜᴇʀ ᴄᴏᴍᴍᴀɴᴅ ᴡɪʟʟ ᴡᴏʀᴋ ᴏɴ ᴛʜɪs ʙᴏᴛ ᴇxᴄᴇᴘᴛ <u>ᴘɪɴɢ</u>. ᴅᴏɴ’ᴛ ᴡᴀsᴛᴇ ʏᴏᴜʀ ᴛɪᴍᴇ</b>""",
            reply_to_message_id=message.from_user.id,
            reply_markup=reply_markup,
            #parse_mode='html'
        )
        return
        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=invite_link.invite_link),
                InlineKeyboardButton("ʀᴇᴀsᴏɴ ?", callback_data=f"whyjoin")
            ]
        ]

        if message.command[1] != "subscribe":
            kk, file_id = message.command[1].split("_", 1)
            pre = 'checksubp' if kk == 'filep' else 'checksub' 
            btn.append([InlineKeyboardButton(" ᴍᴇ ᴊᴏɪɴᴇᴅ ɪɴ ᴄʜᴀɴɴᴇʟ", callback_data=f"{pre}#{file_id}")])
        await message.delete(True)
        await client.send_message(
            chat_id=message.from_user.id,
            reply_to_message_id=message.message_id,
            text=f"""<b>⚠️ ᴘʟᴇᴀsᴇ ғᴏʟʟᴏᴡ ᴛʜɪs ʀᴜʟᴇs ⚠️
            
{message.from_user.mention} ആദ്യം【 <a href="https://t.me/CinimaAdholokam">ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ</a> 】എന്ന ബട്ടൺ ക്ലിക്ക് ചെയ്തു ചാനലിൽ  ജോയിൻ ചെയ്.. എന്നിട്ട് വീണ്ടു ബോട്ടിൽ വന്നിട്ട്【 <a href="https://t.me/Ca_filterbot">ᴍᴇ ᴊᴏɪɴᴇᴅ</a> 】എന്ന ബട്ടൺ ക്ലിക്ക് ചെയ്താൽ ഫയൽ കിട്ടുന്നതായിരിക്കും

Fɪʀsᴛ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ【 <a href="https://t.me/CinimaAdholokaam">ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ</a> 】ʙᴜᴛᴛᴏɴ ᴀɴᴅ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ. ᴛʜᴇɴ ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏ ᴛʜᴇ ʙᴏᴛ ᴄʟɪᴄᴋ ᴏɴ【 <a href="https://t.me/BhasiRobot">ᴍᴇ ᴊᴏɪɴᴇᴅ</a> 】ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇ...</b>""",
            reply_markup=InlineKeyboardMarkup(btn),
            #parse_mode=enums.ParseMode.HTML,
            parse_mode="html", 
            disable_web_page_preview=True
            )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:

        buttons = [[
        InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true') ] ,
      [
        InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about_menu'),
        InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')
    ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=START_IMAGE_URL if START_IMAGE_URL else random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup
           # parse_mode='html'
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Please wait")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()
        

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            filetype = msg.media
            file = getattr(msg, filetype)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"<code>{files.file_name}</code>"
    buttons = [
        [
            InlineKeyboardButton(f'🚸 ᴅᴇʟᴇᴛᴇ', callback_data="rpclose"),
            InlineKeyboardButton('💞 sʜᴀʀᴇ', url="https://t.me/share/url?url=**😱%20സിനിമ%20അധോലോകം%20😱%0A%0Aഏത്%20അർധരാത്രി%20ചോദിച്ചാലും%20പടം%20കിട്ടും,%20ലോകത്തിലെ%20ഒട്ടുമിക്ക%20ഭാഷകളിലുമുള്ള%20സിനിമകളുടെ%20കളക്ഷൻ..%20❤️%0A%0A👇%20GROUP%20LINK%20👇%0A@CinimaAdholokaam%0A@CinimaAdholokaam%0A@CinimaAdholokam**")
        ],
        [
            InlineKeyboardButton(f'🌿 Fɪʟᴇ sɪᴢᴇ【 {get_size(files.file_size)} 】🌿', callback_data="rpc")
        ]
        ]
    await message.delete(True)
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_to_message_id=message.from_user.id,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(buttons)
        )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings') & filters.user(ADMINS))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Filter Button',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Single' if settings["button"] else 'Double',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],[
                InlineKeyboardButton(
                    'Redirect To',
                    callback_data=f'setgs#redirect_to#{settings["redirect_to"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '👤 PM' if settings["redirect_to"] == "PM" else '📄 Chat',
                    callback_data=f'setgs#redirect_to#{settings["redirect_to"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bot PM',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["botpm"] else '❌ No',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'File Secure',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["file_secure"] else '❌ No',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Spell Check',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["spell_check"] else '❌ No',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode="html",
            reply_to_message_id=message.message_id
        )

@Client.on_message(filters.command(["report"]) | filters.regex("@admins") | filters.regex("@admin"))
async def caption(bot, message):
    rpt = message.text
    chat_id=message.from_user.id
    present = datetime.now(tz=pytz.timezone("Asia/Kolkata"))
    time = present.strftime("%I:%M:%S %p")
    date = present.strftime("%d-%B-%Y")
    day = present.strftime("%A")
    utc = present.strftime("%z")
    reply_to_message_id=message.from_user.id
    _rpt = rpt.replace("@admin", "").replace("/report", "")
    unixtime = int(datetime.utcnow().timestamp())

    # await message.delete(True)
    A = await message.reply_text("<b>Rᴇᴘᴏʀᴛ Sᴇɴᴅɪɴɢ ᴛᴏ ᴏᴡɴᴇʀ....\n\n▰▱▱▱</b>")
    await asyncio.sleep(0.5)
    B = await A.edit_text("<b>Rᴇᴘᴏʀᴛ Sᴇɴᴅɪɴɢ ᴛᴏ ᴄᴏ ᴀᴅᴍɪɴ's....\n\n▰▰▱▱</b>")
    await asyncio.sleep(0.5)
    C = await B.edit_text("<b>Rᴇᴘᴏʀᴛ Sᴇɴᴅɪɴɢ ᴛᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ....\n\n▰▰▰▱</b>")
    await asyncio.sleep(0.5)
    D = await C.edit_text("<b>Rᴇᴘᴏʀᴛ Sᴀᴠɪɴɢ ᴛᴏ Dᴀᴛᴀʙᴀsᴇ....\n\n▰▰▰▰</b>")
    E = await D.edit_text(f"""<b><i>✅ Report Send Successful ✅</i>
    
👤 Rᴇᴘᴏʀᴛᴇᴅ ᴜsᴇʀ : {message.from_user.mention}
🆔 Rᴇᴘᴏʀᴛᴇᴅ ᴜsᴇʀ ɪᴅ : <code>{message.from_user.id}</code>
📝 Rᴇᴘᴏʀᴛ ᴛʀᴀᴄᴋ ɪᴅ : #GT{message.message_id}

<i>💬 ʀᴇᴘᴏʀᴛ ᴛᴇxᴛ :</i> <code>{_rpt}</i>

⏲️ ʀᴇᴘᴏʀᴛ ᴛɪᴍᴇ : <code>{time}</code>
🗓️ ʀᴇᴘᴏʀᴛ ᴅᴀᴛᴇ : <code>{date}</code>
⛅ ʀᴇᴘᴏʀᴛ ᴅᴀʏ : <code>{day}</code></b>""")

    await E.forward(RP_CHANNEL)
    
@Client.on_message(filters.command("pong"))
async def ping(bot, message):
    start_time = t.time()
    await message.reply_text( text="Pong!")
    end_time = t.time()
    response_time = (end_time - start_time) * 1000
    await message.reply_text(text=f"Response time: {response_time:.0f} ms")    
    
@Client.on_message(filters.command("ping"))
async def ping_pong(bot, message):
   # start = time()
    first = datetime.now()
    second = datetime.now()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    #m_reply = await message.reply_text("Pinging...")
    #delta_ping = time() - start
    #ping = (current_time - uptime_sec).microseconds / 1000
   
    await message.delete(True)
    S = await message.reply_sticker(
    sticker=random.choice(Stick))
   
    m_reply = await message.reply_text("ᴡᴀɪᴛ...")
    #delta_ping = time() - start
    await asyncio.sleep(0.5)
    M = await m_reply.edit_text(
    #chat_id=message.chat.id
    text=f"<b>🏓 ᴘɪɴɢ :</b> <code>{(second - first).microseconds / 1000} ms</code>\n\n"
         f"<b>⏰ ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime}</code>")
    
    await asyncio.sleep(10)
    await S.delete()
    await M.delete()

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Successfully changed template for {title} to\n\n{template}")
    
@Client.on_message(filters.command("usend") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text
        command = ["/usend"]
        for cmd in command:
            if cmd in target_id:
                target_id = target_id.replace(cmd, "")
        success = False
        try:
            user = await bot.get_users(int(target_id))
            await message.reply_to_message.copy(int(user.id))
            success = True
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ :- <code>{e}</code></b>")
        if success:
            await message.reply_text(f"<b>Yᴏᴜʀ Mᴇssᴀɢᴇ Hᴀs Bᴇᴇɴ Sᴜᴄᴇssғᴜʟʟʏ Sᴇɴᴅ To {user.mention}.</b>")
        else:
            await message.reply_text("<b>Aɴ Eʀʀᴏʀ Oᴄᴄᴜʀʀᴇᴅ !</b>")
    else:
        await message.reply_text("<b>Cᴏᴍᴍᴀɴᴅ Iɴᴄᴏᴍᴘʟᴇᴛᴇ...</b>")
