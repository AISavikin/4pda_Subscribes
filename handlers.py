from bot import dp
from aiogram.dispatcher.filters import Text
from func import *
from aiogram.dispatcher.filters.state import State, StatesGroup


####


class ForPDAStates(StatesGroup):
    """
    Создаются состояния для бота
    """
    default = State()
    subscribe = State()
    unsubscribe = State()


# Создаем служебный словарь для обработчиков, подробнее в описании функции
handler_dict = create_handler_dict()
# создаем стандартную клавиатуру
kbrd_default = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add('Подписаться', 'Отписаться',
                                                                                'Статус подписки')


def setup_keyboard(data: dict, subscribe=True):
    """
    Функция для настройки инлайн клавиатуры
    :param data: Словарь со статусом подписок пользователей
    :param subscribe: По умолчанию создаёт клавиатуру для подписок, при subscribe=False, для отписок
    :return: types.InlineKeyboardMarkup, возвращает инлайн клавиатуру
    """
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
    """
    Выдает приветствие, и добавлет пользователя в базу данных, если его там нет
    """
    user_id = msg.from_user.id
    if check_user(user_id):
        await msg.answer(f'Рад тебя видеть {msg.from_user.full_name}!', reply_markup=kbrd_default)
    else:
        await msg.answer(
            'Добро пожаловать в бот, для подписки на сайт 4PDA! Внизу есть кнопочки, нажимай, не стесняйся😁',
            reply_markup=kbrd_default)


@dp.message_handler(Text(equals='Подписаться'), state='*')
async def subscribe(msg: types.Message):
    """
    Реагируют на сообщение с текстом "Подписаться", меняет состояние на "Subscribe", формирует инлайн клавиатуру,
    и отправляет её пользователю, если пользователя нет в базе данных, добавляет его.
    """
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
    """
    Реагирует на инлайн кнопку. Добавляет категорию для этого пользователя в базу данных
    """
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
    """
    Реагируют на сообщение с текстом "Отписаться", меняет состояние на "Unsubscribe", формирует инлайн клавиатуру,
    и отправляет её пользователю, если пользователя нет в базе данных, добавляет его.
    """
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
    """
    Реагирует на инлайн кнопку. Удаляет категорию для этого пользователя из базы данных
    """
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
    """
    Берет из базы данных статус подписки пользователя и отправляет сообщение с категориями, на которые он подписан
    """
    data = get_subscribe_status(msg.from_user.id)
    if all(map(lambda x: not data[x], data)):
        await msg.answer('Ты не на что не подписан', reply_markup=kbrd_default)
    else:
        subscribes = (handler_dict[i]['name'] for i in data if data[i])
        await msg.answer('Сейчас вы подписаны на категории:\n')
        await msg.answer(",\n".join(subscribes))


@dp.message_handler(state='*')
async def all_text(msg: types.Message):
    """
    Реагирует на любые сообщения, которые не прописаны в обработчике, отправляет стандартную клавиатуру, и меняет
    состояние на "Default"
    """
    check_user(msg.from_user.id)
    await ForPDAStates.default.set()
    await msg.answer(f'Рад тебя видеть {msg.from_user.full_name}!', reply_markup=kbrd_default)
