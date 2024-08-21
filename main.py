import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from handlers import (aboutandedit, menuandme,
                      createandwatchtravel, watchandedittravel, editapi)
from database import Database

logging.basicConfig(level=logging.INFO)

bot = Bot(token="secret")

dp = Dispatcher()
dp.include_routers(aboutandedit.router,
                   menuandme.router,
                   createandwatchtravel.router,
                   watchandedittravel.router, editapi.router)

async def main():
    await Database().startapp()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())