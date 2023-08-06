""" PagerMaid module to handle sticker collection. """

from urllib import request
from io import BytesIO
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
from PIL import Image
from math import floor
from pagermaid import bot
from pagermaid.listener import listener


@listener(outgoing=True, command="sticker",
          description="Collects image/sticker as sticker, specify emoji to set custom emoji.",
          parameters="<emoji>")
async def sticker(context):
    """ Fetches images/stickers and add them to your pack. """
    user = await bot.get_me()
    if not user.username:
        user.username = user.first_name
    message = await context.get_reply_message()
    custom_emoji = False
    animated = False
    emoji = ""
    await context.edit("Collecting sticker . . .")
    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            photo = BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split('/'):
            photo = BytesIO()
            await context.edit("Downloading image . . .")
            await bot.download_file(message.media.document, photo)
            if (DocumentAttributeFilename(file_name='sticker.webp') in
                    message.media.document.attributes):
                emoji = message.media.document.attributes[1].alt
                custom_emoji = True
        elif (DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in
              message.media.document.attributes):
            emoji = message.media.document.attributes[0].alt
            custom_emoji = True
            animated = True
            photo = 1
        else:
            await context.edit("`This file type is not supported.`")
            return
    else:
        await context.edit("`Please reply to a message with an image/sticker.`")
        return

    if photo:
        split_strings = context.text.split()
        if not custom_emoji:
            emoji = "👀"
        pack = 1
        if len(split_strings) == 3:
            pack = split_strings[2]
            emoji = split_strings[1]
        elif len(split_strings) == 2:
            if split_strings[1].isnumeric():
                pack = int(split_strings[1])
            else:
                emoji = split_strings[1]

        pack_name = f"pack_{user.id}_{user.username}_{pack}"
        pack_title = f"@{user.username}'s collection ({pack})"
        command = '/newpack'
        file = BytesIO()

        if not animated:
            await context.edit("Resizing image . . .")
            image = await resize_image(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            pack_name += "_animated"
            pack_title += " (animated)"
            command = '/newanimated'

        response = request.urlopen(
            request.Request(f'http://t.me/addstickers/{pack_name}'))
        http_response = response.read().decode("utf8").split('\n')

        if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in \
                http_response:
            async with bot.conversation('Stickers') as conversation:
                await conversation.send_message('/addsticker')
                await conversation.get_response()
                await bot.send_read_acknowledge(conversation.chat_id)
                await conversation.send_message(pack_name)
                chat_response = await conversation.get_response()
                while chat_response.text == "Whoa! That's probably enough stickers for one pack, give it a break. \
A pack can't have more than 120 stickers at the moment.":
                    pack += 1
                    pack_name = f"a{user.id}_by_{user.username}_{pack}"
                    pack_title = f"@{user.username}'s collection ({pack})"
                    await context.edit("Switching to pack " + str(pack) +
                                       " since previous pack is full . . .")
                    await conversation.send_message(pack_name)
                    chat_response = await conversation.get_response()
                    if chat_response.text == "Invalid pack selected.":
                        await add_sticker(conversation, command, pack_title, pack_name, animated, message,
                                          context, file, emoji)
                        await context.edit(
                            f"Sticker has been added to [this](t.me/addstickers/{pack_name}) alternative pack.",
                            parse_mode='md')
                        return
                await upload_sticker(animated, message, context, file, conversation)
                await conversation.get_response()
                await conversation.send_message(emoji)
                await bot.send_read_acknowledge(conversation.chat_id)
                await conversation.get_response()
                await conversation.send_message('/done')
                await conversation.get_response()
                await bot.send_read_acknowledge(conversation.chat_id)
        else:
            await context.edit("Pack does not exist, creating . . .")
            async with bot.conversation('Stickers') as conversation:
                await add_sticker(conversation, command, pack_title, pack_name, animated, message,
                                  context, file, emoji)

        await context.edit(
            f"Sticker has been added to [this](t.me/addstickers/{pack_name}) pack.",
            parse_mode='md')


async def add_sticker(conversation, command, pack_title, pack_name, animated, message, context, file, emoji):
    await conversation.send_message(command)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message(pack_title)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await upload_sticker(animated, message, context, file, conversation)
    await conversation.get_response()
    await conversation.send_message(emoji)
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message("/publish")
    if animated:
        await conversation.get_response()
        await conversation.send_message(f"<{pack_title}>")
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message("/skip")
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message(pack_name)
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)


async def upload_sticker(animated, message, context, file, conversation):
    if animated:
        await bot.forward_messages(
            'Stickers', [message.id], context.chat_id)
    else:
        file.seek(0)
        await context.edit("Uploading image . . .")
        await conversation.send_file(file, force_document=True)


async def resize_image(photo):
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        image.thumbnail(maxsize)

    return image
