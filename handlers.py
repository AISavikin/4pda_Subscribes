from bot import dp
from aiogram.dispatcher.filters import Text
from func import *
from aiogram.dispatcher.filters.state import State, StatesGroup


class ForPDAStates(StatesGroup):
    subscribe = State()
    unsubscribe = State()


handler_dict = create_data_dict()
kbrd_default = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add('Подписаться', 'Отписаться',
                                                                                'Статус подписки')

def setup_data(msg):
    subscribe_status = DataBase().read_one(msg.from_user.id)[1:]
    now_subscribes = {CATEGORIES[i]: subscribe_status[i] for i in range(len(handler_dict))}
    data = {'now_subscribes': now_subscribes}
    return data

def setup_keyboard(data):
    kbrd = types.InlineKeyboardMarkup()
    for i in data['now_subscribes']:
        if not data['now_subscribes'][i]:
            kbrd.add(handler_dict[i]['btn'])
    return kbrd


@dp.message_handler(commands='start', state='*')
async def start(msg: types.Message):
    user_id = msg.from_user.id
    if check_user(user_id):
        await msg.answer(f'Рад тебя видеть {msg.from_user.full_name}!', reply_markup=kbrd_default)
    else:
        await msg.answer(
            'Добро пожаловать в бот, для подписки на сайт 4PDA! Внизу есть кнопочки, нажимай, не стесняйся😁',
            reply_markup=kbrd_default)


@dp.message_handler(Text(equals='Подписаться'), state='*')
async def subscribe(msg: types.Message):
    check_user(msg.from_user.id)
    await ForPDAStates.subscribe.set()
    data = setup_data(msg)
    kbrd = setup_keyboard(data)
    if all(map(lambda x: data['now_subscribes'][x], data['now_subscribes'])):
        await msg.answer('Ты подписан на всё что можно', reply_markup=kbrd.add(
            types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')))
    else:
        await msg.answer('Выберите категорию', reply_markup=kbrd)


@dp.callback_query_handler(state=ForPDAStates.subscribe)
async def subscribe_call(call: types.CallbackQuery):
    data = setup_data(call)
    url = handler_dict[call.data]['url']
    item = get_item(url)
    DataBase().update(call.data, item, call.from_user.id)
    data = setup_data(call)
    kbrd = setup_keyboard(data)
    if all(map(lambda x: data['now_subscribes'][x], data['now_subscribes'])):
        await call.message.answer('Ты подписан на всё что можно', reply_markup=kbrd.add(
            types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')))
    else:
        await call.message.answer('Выберите категорию', reply_markup=kbrd)


