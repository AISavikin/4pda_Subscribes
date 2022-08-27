import asyncio
from aiogram.utils import executor
import logging
from bot import dp
import handlers
from func import send_news

logging.basicConfig(level=logging.INFO)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_news(20), name='Отправка новостей')
    executor.start_polling(dp, skip_updates=True)
