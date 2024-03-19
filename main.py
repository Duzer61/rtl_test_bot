import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher

from config_data.config import config
from database.mongo_db import client
from handlers.handlers import router

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s'
)


async def main():
    logger.info('Starting bot')

    bot = Bot(token=config.tg_bot.token,
              parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def signal_handler(sig, frame):
    client.close()
    logger.info('Bot stopped.')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
