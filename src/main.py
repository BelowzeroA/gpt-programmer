import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.filters.command import Command
from aiogram.types import Message, BotCommand

# from dotenv import load_dotenv

TOKEN = "6136054219:AAGn2QsPJOcPMOiL0X6j3fQBf191CQXI0xw"
# load_dotenv()

router = Router()
bot = Bot(token=TOKEN, parse_mode="HTML")


@router.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer('Привет!')


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
