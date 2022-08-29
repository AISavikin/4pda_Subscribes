import asyncio
from data_base_class import DataBase
from aiogram import types
from bs4 import BeautifulSoup
import requests
from bot import bot

# название категорий
CATEGORIES = (
    'news_smartphones', 'news_notebook', 'news_pc', 'news_appliances',
    'news_audio', 'news_monitors', 'news_games',
    'reviews_smartphones', 'reviews_tablets', 'reviews_smart_watches',
    'reviews_accessories', 'reviews_notebooks', 'reviews_audio', 'all_news'
)

# URL категорий
URLS = (
    'https://4pda.to/tag/smartphones/', 'https://4pda.to/tag/laptops/', 'https://4pda.to/tag/pc/',
    'https://4pda.to/tag/appliances/', 'https://4pda.to/tag/audio/', 'https://4pda.to/tag/monitors/',
    'https://4pda.to/games/', 'https://4pda.to/reviews/smartphones/', 'https://4pda.to/reviews/tablets/',
    'https://4pda.to/reviews/smart-watches/', 'https://4pda.to/reviews/accessories/',
    'https://4pda.to/reviews/laptops/', 'https://4pda.to/reviews/audio/', 'https://4pda.to/'
)

# Человекочитаемые название категорий
NAMES = (
    'Новости/Смартфоны', 'Новости/Ноутбуки', 'Новости/ПК', 'Новости/Бытовая техника', 'Новости/Аудио',
    'Новости/Тв и мониторы', 'Новости/Игры', 'Обзоры/Смартфоны', 'Обзоры/Планшеты', 'Обзоры/Умные часы',
    'Обзоры/Аксессуары', 'Обзоры/Ноутбуки', 'Обзоры/Аудио', 'Все новости'
)


class ForPDA:
    """
    Класс для получения новостей с сайта и формирования индивидуальных пакетов новостей, для каждого пользователя.
    Создаётся и используется в функции send_news
    """
    def __init__(self):
        self.users_subscribe_status = self.get_users_subscribe_status()
        self.news = self.get_news()
        self.ids_news = {key: list(reversed([item for item in self.news[key]])) for key in self.news}
        self.users_news = self.collect_users_news()
        self.collect_users_news()

    @staticmethod
    def get_news():
        """
        Получает последние 3 новости с сайта 4pda.to в каждой категории, парсит и собирает в словарь.
        :return: dict {category:{news_id:(description, title, href, img)}
        """
        news = {}
        for cat in zip(CATEGORIES, URLS):
            html = requests.get(cat[1]).text
            soup = BeautifulSoup(html, features="html.parser")
            articles = soup.find_all('article', class_='post')
            data = {}
            for i in articles:
                try:
                    href = i.find('a').get('href')
                except:
                    continue
                item_id = i.get('itemid')
                title = i.find('a').get('title')
                img = i.find('img').get('src')
                try:
                    description = i.find('p').text
                    if description == '':
                        continue
                except:
                    continue
                data[item_id] = (description, title, href, img)
                if len(data) == 3:
                    break
            news[cat[0]] = data

        return news

    @staticmethod
    def get_users_subscribe_status():
        """
        Берет из базы данных информацию о статусе подписки для всех пользователей из базы данных.
        Если пользователь подписан на категорию, то в словарь помещается последний актуальный id новости
        из базы данных.
        :return: dict {user_id:{category:{id_news}}}
        """
        users = DataBase().read_all()
        users = {user[0]: get_subscribe_status(user[0]) for user in users}
        return users

    def collect_users_news(self):
        """
        Собирает пакет новостей для каждого конкретного пользователя
        """
        users_news = {
            user: {cat: [] for cat in self.users_subscribe_status[user] if self.users_subscribe_status[user][cat]} for
            user in self.users_subscribe_status}

        for user in users_news:
            for cat in users_news[user]:
                last_id = self.users_subscribe_status[user][cat]
                if last_id not in self.ids_news[cat]:
                    users_news[user][cat] = self.ids_news[cat]
                else:
                    users_news[user][cat] = [self.ids_news[cat][i] for i in range(len(self.ids_news[cat])) if
                                             i > self.ids_news[cat].index(last_id)]
        return users_news


# region


def create_handler_dict() -> dict:
    data = dict().fromkeys(CATEGORIES)
    for num, val in enumerate(data):
        data[val] = {}
        data[val]['url'] = URLS[num]
        data[val]['name'] = NAMES[num]
        data[val]['btn'] = types.InlineKeyboardButton(data[val]['name'], callback_data=val)
    return data


def get_subscribe_status(user_id):
    data_base_data = DataBase().read_one(user_id)[1:]
    subscribe_status = {CATEGORIES[i]: data_base_data[i] for i in range(len(CATEGORIES))}
    return subscribe_status


def check_user(user_id):
    if DataBase().read_one(user_id):
        return
    else:
        DataBase().insert(user_id)


def get_item(url):
    articles = BeautifulSoup(requests.get(url).text, features="html.parser").find_all('article', class_='post')
    if articles[0].find('p').text:
        return articles[0].get('itemid')
    else:
        return articles[1].get('itemid')


# endregion

async def send_news(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        fpda = ForPDA()
        users = [int(user) for user in fpda.users_subscribe_status]
        for user in users:
            for cat in fpda.users_news[user]:
                for post_id in fpda.users_news[user][cat]:
                    text = fpda.news[cat][post_id][0]
                    title = fpda.news[cat][post_id][1]
                    url = fpda.news[cat][post_id][2]
                    img = fpda.news[cat][post_id][3]
                    await bot.send_photo(user, img, parse_mode=types.ParseMode.HTML,
                                         caption=f'<b>{title}</b>\n\n{text}\n<a href="{url}">Перейти к новости на сайт 4PDA</a>')
                DataBase().update(cat, fpda.ids_news[cat][-1], user)


def main():
    pass

if __name__ == '__main__':
    main()
