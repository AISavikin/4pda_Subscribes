from bot import dp
from aiogram.dispatcher.filters import Text
from func import *
from aiogram.dispatcher.filters.state import State, StatesGroup


class ForPDAStates(StatesGroup):
    default = State()
    subscribe = State()
    unsubscribe = State()


handler_dict = create_handler_dict()
kbrd_default = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add('Подписаться', 'Отписаться',
                                                                                'Статус подписки')


def setup_keyboard(data, subscribe=True):
    kbrd = types.InlineKeyboardMarkup()
    if subscribe:
        btns = (handler_dict[i]['btn'] for i in data if not data[i])
    else:
        btns = (handler_dict[i]['btn'] for i in data if data[i])
    for btn in btns:
        kbrd.add(btn)
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
    data = get_subscribe_status(msg.from_user.id)
    kbrd = setup_keyboard(data)
    if all(map(lambda x: data[x], data)):
        await msg.answer('Ты подписан на всё что можно', reply_markup=kbrd.add(
            types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')))
    else:
        await msg.answer('Выберите категорию', reply_markup=kbrd)


@dp.callback_query_handler(state=ForPDAStates.subscribe)
async def subscribe_call(call: types.CallbackQuery):
    data = get_subscribe_status(call.from_user.id)
    url = handler_dict[call.data]['url']
    item = get_item(url)
    DataBase().update(call.data, item, call.from_user.id)
    data = get_subscribe_status(call.from_user.id)
    kbrd = setup_keyboard(data)
    if all(map(lambda x: data[x], data)):
        await ForPDAStates.default.set()
        await call.message.answer('Ты подписан на всё что можно', reply_markup=kbrd_default)
    else:
        await call.message.answer('Выберите категорию', reply_markup=kbrd)
    await call.answer()


@dp.message_handler(Text(equals='Отписаться'), state='*')
async def unsubscribe(msg: types.Message):
    check_user(msg.from_user.id)
    await ForPDAStates.unsubscribe.set()
    data = get_subscribe_status(msg.from_user.id)
    kbrd = setup_keyboard(data, False)
    if all(map(lambda x: not data[x], data)):
        await ForPDAStates.default.set()
        await msg.answer('Ты не на что не подписан.', reply_markup=kbrd_default)
    else:
        await msg.answer('Выберите категорию', reply_markup=kbrd)


@dp.callback_query_handler(state=ForPDAStates.unsubscribe)
async def unsubscribe_call(call: types.CallbackQuery):
    data = get_subscribe_status(call.from_user.id)
    DataBase().update(call.data, '', call.from_user.id)
    data = get_subscribe_status(call.from_user.id)
    kbrd = setup_keyboard(data, False)
    if all(map(lambda x: not data[x], data)):
        await ForPDAStates.default.set()
        await call.message.answer('Ты не на что не подписан.', reply_markup=kbrd_default)
    else:
        await call.message.answer('Выберите категорию', reply_markup=kbrd)
    await call.answer()


@dp.message_handler(Text(equals='Статус подписки'), state='*')
async def status(msg: types.Message):
    data = get_subscribe_status(msg.from_user.id)
    if all(map(lambda x: not data[x], data)):
        await msg.answer('Ты не на что не подписан', reply_markup=kbrd_default)
    else:
        subscribes = (handler_dict[i]['name'] for i in data if data[i])
        await msg.answer('Сейчас вы подписаны на категории:\n')
        await msg.answer(",\n".join(subscribes))
