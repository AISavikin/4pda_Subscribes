import asyncio
from aiogram.utils import executor
import logging
from bot import dp
import handlers
from func import send_news

logging.basicConfig(level=logging.INFO)



if __name__ == '__main__':
    # Создаем задачу для проверки новостей
    loop = asyncio.get_event_loop()
    loop.create_task(send_news(2), name='Отправка новостей')
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
