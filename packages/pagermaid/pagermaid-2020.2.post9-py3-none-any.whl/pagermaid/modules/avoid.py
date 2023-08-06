""" PagerMaid module for different ways to avoid users. """

from pagermaid import redis, log, redis_status
from pagermaid.listener import listener


@listener(outgoing=True, command="ghost",
          description="Toggles ghosting of chat, requires redis.",
          parameters="<true|false|status>")
async def ghost(context):
    """ Toggles ghosting of a user. """
    if not redis_status():
        await context.edit("Redis is offline, cannot operate.")
        return
    if len(context.parameter) != 1:
        await context.edit("Invalid argument.")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    if context.parameter[0] == "true":
        if context.chat_id == self_user_id:
            await context.edit("Unable to set flag on self.")
            return
        redis.set("ghosted.chat_id." + str(context.chat_id), "true")
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} added to ghosted chats.")
    elif context.parameter[0] == "false":
        if context.chat_id == self_user_id:
            await context.edit("Unable to set flag on self.")
            return
        redis.delete("ghosted.chat_id." + str(context.chat_id))
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} removed from ghosted chats.")
    elif context.parameter[0] == "status":
        if redis.get("ghosted.chat_id." + str(context.chat_id)):
            await context.edit("Current chat is ghosted.")
        else:
            await context.edit("Current chat is not ghosted.")
    else:
        await context.edit("Invalid argument.")


@listener(outgoing=True, command="deny",
          description="Toggles denying of chat, requires redis.",
          parameters="<true|false|status>")
async def deny(context):
    """ Toggles denying of a user. """
    if not redis_status():
        await context.edit("Redis is offline, cannot operate.")
        return
    if len(context.parameter) != 1:
        await context.edit("Invalid argument.")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    if context.parameter[0] == "true":
        if context.chat_id == self_user_id:
            await context.edit("Unable to set flag on self.")
            return
        redis.set("denied.chat_id." + str(context.chat_id), "true")
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} added to denied chats.")
    elif context.parameter[0] == "false":
        if context.chat_id == self_user_id:
            await context.edit("Unable to set flag on self.")
            return
        redis.delete("denied.chat_id." + str(context.chat_id))
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} removed from denied chats.")
    elif context.parameter[0] == "status":
        if redis.get("denied.chat_id." + str(context.chat_id)):
            await context.edit("Current chat is denied.")
        else:
            await context.edit("Current chat is not denied.")
    else:
        await context.edit("Invalid argument.")


@listener(incoming=True, ignore_edited=True)
async def set_read_acknowledgement(context):
    """ Event handler to infinitely read ghosted messages. """
    if not redis_status():
        return
    if redis.get("ghosted.chat_id." + str(context.chat_id)):
        await context.client.send_read_acknowledge(context.chat_id)


@listener(incoming=True, ignore_edited=True)
async def message_removal(context):
    """ Event handler to infinitely delete denied messages. """
    if not redis_status():
        return
    if redis.get("denied.chat_id." + str(context.chat_id)):
        await context.delete()
