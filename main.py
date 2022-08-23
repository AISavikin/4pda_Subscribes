from aiogram.utils import executor
import logging
from bot import dp
import handlers



logging.basicConfig(level=logging.INFO)



if __name__ == '__main__':
    executor.start_polling(dp)