from bot import dp
from aiogram.dispatcher.filters import Text
from func import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class ForPDAStates(StatesGroup):
    subscribe = State()
    unsubscribe = State()


handler_dict = create_data_dict()
kbrd_default = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add('Подписаться', 'Отписаться',
                                                                                'Статус подписки')


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
async def subscribe(msg: types.Message, state: FSMContext):
    await ForPDAStates.subscribe.set()
    subscribe_status = DataBase().read_one(msg.from_user.id)[1:]
    now_subscribes = {CATEGORIES[i]: subscribe_status[i] for i in range(14)}
    data = {'now_subscribes': now_subscribes}
    await state.update_data(data=data)
    kbrd = types.InlineKeyboardMarkup()
    for i in now_subscribes:
        if not now_subscribes[i]:
            kbrd.add(handler_dict[i]['btn'])
    if all(map(lambda x: now_subscribes[x], now_subscribes)):
        await msg.answer('Ты подписан на всё что можно', reply_markup=kbrd.add(
            types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')))
    else:
        await msg.answer('Выберите категорию', reply_markup=kbrd)


@dp.callback_query_handler(state=ForPDAStates.subscribe)
async def subscribe_call(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data)
    data = await state.get_data()
    url = handler_dict[call.data]['url']
    kbrd = types.InlineKeyboardMarkup()
    item = get_item(url)
    DataBase().update(data['category'], item, call.from_user.id)
    now_subscribes = {CATEGORIES[i]: DataBase().read_one(call.from_user.id)[1:][i] for i in range(14)}
    data = {'now_subscribes': now_subscribes}
    await state.update_data(data=data)
    for i in data['now_subscribes']:
        if not data['now_subscribes'][i]:
            kbrd.add(handler_dict[i]['btn'])
    if all(map(lambda x: data['now_subscribes'][x], data['now_subscribes'])):
        await call.message.answer('Ты подписан на всё что можно', reply_markup=kbrd.add(
            types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')))
    else:
        await call.message.answer('Выберите категорию', reply_markup=kbrd)
    print(data)
