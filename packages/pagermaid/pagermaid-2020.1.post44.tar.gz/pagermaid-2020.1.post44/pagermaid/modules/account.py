""" This module contains utils to configure your account. """

from os import remove
from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.errors.rpcerrorlist import PhotoExtInvalidError, UsernameOccupiedError, AboutTooLongError, \
    FirstNameInvalidError, UsernameInvalidError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import DeletePhotosRequest, GetUserPhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto, MessageMediaPhoto, MessageEntityMentionName
from struct import error as StructError
from pagermaid import bot, log
from pagermaid.listener import listener


@listener(outgoing=True, command="username",
          description="sets the username.",
          parameters="<username>")
async def username(context):
    """ Reconfigure your username. """
    if len(context.parameter) > 1:
        await context.edit("Invalid argument.")
    if len(context.parameter) == 1:
        result = context.parameter[0]
    else:
        result = ""
    try:
        await bot(UpdateUsernameRequest(result))
    except UsernameOccupiedError:
        await context.edit("Username is taken.")
        return
    except UsernameInvalidError:
        await context.edit("Invalid username.")
        return
    await context.edit("Username have been updated.")
    if result == "":
        await log("Username has been unset.")
        return
    await log(f"Username has been set to `{result}`.")


@listener(outgoing=True, command="name",
          description="Alters the display name.",
          parameters="<first name> <last name>")
async def name(context):
    """ Updates your display name. """
    if len(context.parameter) == 2:
        first_name = context.parameter[0]
        last_name = context.parameter[1]
    elif len(context.parameter) == 1:
        first_name = context.parameter[0]
        last_name = " "
    else:
        await context.edit("Invalid argument.")
        return
    try:
        await bot(UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name))
    except FirstNameInvalidError:
        await context.edit("Invalid first name.")
        return
    await context.edit("Display name is successfully altered.")
    if last_name != " ":
        await log(f"Changed display name to `{first_name} {last_name}`.")
    else:
        await log(f"Changed display name to `{first_name}`.")


@listener(outgoing=True, command="pfp",
          description="Set attachment of message replied to as profile picture.")
async def pfp(context):
    """ Sets your profile picture. """
    reply = await context.get_reply_message()
    photo = None
    await context.edit("Setting profile picture . . .")
    if reply.media:
        if isinstance(reply.media, MessageMediaPhoto):
            photo = await bot.download_media(message=reply.photo)
        elif "image" in reply.media.document.mime_type.split('/'):
            photo = await bot.download_file(reply.media.document)
        else:
            await context.edit("Unable to parse attachment as image.")

    if photo:
        try:
            await bot(UploadProfilePhotoRequest(
                await bot.upload_file(photo)
            ))
            remove(photo)
            await context.edit("Profile picture has been updated.")
        except PhotoCropSizeSmallError:
            await context.edit("The image dimensions are smaller than minimum requirement.")
        except ImageProcessFailedError:
            await context.edit("An error occurred while the server is interpreting the command.")
        except PhotoExtInvalidError:
            await context.edit("Unable to parse attachment as image.")


@listener(outgoing=True, command="bio",
          description="Sets the biography to the string in the parameter.",
          parameters="<string>")
async def bio(context):
    """ Sets your bio. """
    try:
        await bot(UpdateProfileRequest(about=context.arguments))
    except AboutTooLongError:
        await context.edit("Provided string is too long.")
        return
    await context.edit("Bio has been altered successfully.")
    if context.arguments == "":
        await log("Bio has been unset.")
        return
    await log(f"Bio has been set to `{context.arguments}`.")


@listener(outgoing=True, command="rmpfp",
          description="Deletes defined amount of profile pictures.",
          parameters="<integer>")
async def rmpfp(context):
    """ Removes your profile picture. """
    group = context.text[8:]
    if group == 'all':
        limit = 0
    elif group.isdigit():
        limit = int(group)
    else:
        limit = 1

    pfp_list = await bot(GetUserPhotosRequest(
        user_id=context.from_id,
        offset=0,
        max_id=0,
        limit=limit))
    input_photos = []
    for sep in pfp_list.photos:
        input_photos.append(
            InputPhoto(
                id=sep.id,
                access_hash=sep.access_hash,
                file_reference=sep.file_reference
            )
        )
    await bot(DeletePhotosRequest(id=input_photos))
    await context.edit(f"`Removed {len(input_photos)} profile picture(s).`")


@listener(outgoing=True, command="profile",
          description="Shows user profile in a large message.",
          parameters="<username>")
async def profile(context):
    """ Queries profile of a user. """
    if len(context.parameter) > 1:
        await context.edit("Invalid argument.")
        return

    await context.edit("Generating user profile summary . . .")
    if context.reply_to_msg_id:
        user_id = await context.get_reply_message().from_id
        target_user = await context.client(GetFullUserRequest(user_id))
    else:
        if len(context.parameter) == 1:
            user = context.parameter[0]
            if user.isnumeric():
                user = int(user)
        else:
            user_object = await context.client.get_me()
            user = user_object.id
        if context.message.entities is not None:
            if isinstance(context.message.entities[0], MessageEntityMentionName):
                return await context.client(GetFullUserRequest(context.message.entities[0].user_id))
        try:
            user_object = await context.client.get_entity(user)
            target_user = await context.client(GetFullUserRequest(user_object.id))
        except (TypeError, ValueError, OverflowError, StructError) as exception:
            if str(exception).startswith("Cannot find any entity corresponding to"):
                await context.edit("The specified user does not exist.")
                return
            if str(exception).startswith("No user has"):
                await context.edit("The username specified does not exist.")
                return
            if str(exception).startswith("Could not find the input entity for") or isinstance(exception, StructError):
                await context.edit("The UserID specified does not correspond to a user.")
                return
            if isinstance(exception, OverflowError):
                await context.edit("The UserID specified have exceeded the integer limit.")
                return
            raise exception
    user_type = "Bot" if target_user.user.bot else "User"
    username_system = target_user.user.username if target_user.user.username is not None else (
        "This user have not yet defined their username.")
    first_name = target_user.user.first_name.replace("\u2060", "")
    last_name = target_user.user.last_name.replace("\u2060", "") if target_user.user.last_name is not None else (
        "This user did not define a last name."
    )
    biography = target_user.about if target_user.about is not None else "This user did not define a biography string."
    caption = f"**Profile:** \n" \
              f"Username: @{username_system} \n" \
              f"UserID: {target_user.user.id} \n" \
              f"First Name: {first_name} \n" \
              f"Last Name: {last_name} \n" \
              f"Biography: {biography} \n" \
              f"Common Groups: {target_user.common_chats_count} \n" \
              f"Verified: {target_user.user.verified} \n" \
              f"Restricted: {target_user.user.restricted} \n" \
              f"Type: {user_type} \n" \
              f"Permanent Link: [{first_name}](tg://user?id={target_user.user.id})"
    reply_to = context.message.reply_to_msg_id
    photo = await context.client.download_profile_photo(
        target_user.user.id,
        "./" + str(target_user.user.id) + ".jpg",
        download_big=True
    )
    if not reply_to:
        reply_to = None
    try:
        await context.client.send_file(
            context.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=reply_to
        )
        if not photo.startswith("http"):
            remove(photo)
        await context.delete()
        return
    except TypeError:
        await context.edit(caption)
    remove(photo)
