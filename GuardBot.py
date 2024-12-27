import logging
import asyncio
from datetime import timedelta, datetime
from aiogram import Bot, Dispatcher
from aiogram.types import (Message, ChatPermissions, BotCommand, User)
from aiogram.filters import CommandObject, Command

# Настройки
API_TOKEN = "7896663402:AAHG-HFOrkkJmLcLTSxM3go2dSBc2t2jjN0"
ADMIN_ID = 7205834174  # ID администратора для уведомлений
ADMIN_LIST = [ADMIN_ID]  # Инициируем список администраторов (можно добавлять вручную)

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def set_commands():
    """Устанавливаем меню команд для бота"""
    commands = [
        BotCommand(command="ban", description="Забанить пользователя"),
        BotCommand(command="unban", description="Разбанить пользователя"),
        BotCommand(command="mute", description="Замьютить пользователя"),
        BotCommand(command="unmute", description="Снять мут"),
        BotCommand(command="kick", description="Кикнуть пользователя"),
        BotCommand(command="setadmin", description="Установить администратора")
    ]
    await bot.set_my_commands(commands)

async def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_LIST

@dp.message(Command("setadmin"))
async def set_admin_command(message: Message, command: CommandObject):
    """Команда для установки администратора"""
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return

    try:
        args = command.args.split() if command.args else []
        if len(args) != 1:
            await message.reply("Используйте: /setadmin <ID пользователя>")
            return
        new_admin_id = int(args[0])
        if new_admin_id not in ADMIN_LIST:
            ADMIN_LIST.append(new_admin_id)
            await message.reply(f"Пользователь с ID {new_admin_id} теперь является администратором.")
        else:
            await message.reply(f"Пользователь с ID {new_admin_id} уже является администратором.")
    except ValueError:
        await message.reply("Введите корректный ID пользователя.")

@dp.message(Command("ban"))
async def ban_command(message: Message, command: CommandObject):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть использована в ответ на сообщение.")
        return
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    try:
        args = command.args.split(maxsplit=1) if command.args else []
        if len(args) != 1:
            await message.reply("Используйте: /ban <причина>")
            return
        reason = args[0]
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь @{message.reply_to_message.from_user.username} был забанен. Причина: {reason}")
    except Exception as e:
        await message.reply(f"Не удалось забанить пользователя. Ошибка: {e}")

@dp.message(Command("unban"))
async def unban_command(message: Message, command: CommandObject):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть использована в ответ на сообщение.")
        return
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    try:
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь @{message.reply_to_message.from_user.username} был разбанен.")
    except Exception as e:
        await message.reply(f"Не удалось разбанить пользователя. Ошибка: {e}")

@dp.message(Command("mute"))
async def mute_command(message: Message, command: CommandObject):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть использована в ответ на сообщение.")
        return
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    if message.chat.type != "supergroup":
        await message.reply("Команда /mute доступна только в супергруппах. Преобразуйте вашу группу в супергруппу.")
        return
    try:
        args = command.args.split() if command.args else []
        if len(args) != 2:
            await message.reply("Используйте: /mute <время (в минутах)> <причина>")
            return
        duration = int(args[0])
        reason = " ".join(args[1:])
        until_date = datetime.now() + timedelta(minutes=duration)
        permissions = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(
            message.chat.id, message.reply_to_message.from_user.id, permissions, until_date=until_date
        )
        await message.reply(f"Пользователь @{message.reply_to_message.from_user.username} был замьючен на {duration} минут. Причина: {reason}")
    except Exception as e:
        await message.reply(f"Не удалось замьютить пользователя. Ошибка: {e}")

@dp.message(Command("unmute"))
async def unmute_command(message: Message, command: CommandObject):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть использована в ответ на сообщение.")
        return
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    try:
        permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions)
        await message.reply(f"С пользователя @{message.reply_to_message.from_user.username} был снят мут.")
    except Exception as e:
        await message.reply(f"Не удалось снять мут. Ошибка: {e}")

@dp.message(Command("kick"))
async def kick_command(message: Message, command: CommandObject):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть использована в ответ на сообщение.")
        return
    if not await is_admin(message.from_user.id):
        await message.reply("У вас нет прав для использования этой команды.")
        return
    try:
        args = command.args.split(maxsplit=1) if command.args else []
        if len(args) != 1:
            await message.reply("Используйте: /kick <причина>")
            return
        reason = args[0]
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь @{message.reply_to_message.from_user.username} был кикнут. Причина: {reason}")
    except Exception as e:
        await message.reply(f"Не удалось кикнуть пользователя. Ошибка: {e}")

async def main():
    # Установка команд в меню бота
    await set_commands()

    # Удаляем старые вебхуки и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот успешно запущен и готов к работе!")
    await bot.send_message(chat_id=ADMIN_ID, text="Бот успешно запущен и работает!")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
