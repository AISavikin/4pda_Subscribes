from bot import dp
from aiogram import types
from data_base_class import DataBase

@dp.message_handler(commands='start', state='*')
async def start(msg: types.Message):
    user_id = msg.from_user.id
    DataBase().insert(user_id)
    kbrd = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add('Подписаться', 'Отписаться',
                                                                            'Статус подписки')
    await msg.answer('Приветсиве', reply_markup=kbrd)

