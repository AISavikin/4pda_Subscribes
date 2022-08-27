import asyncio
from data_base_class import DataBase
from aiogram import types
from bs4 import BeautifulSoup
import requests
from bot import bot

CATEGORIES = (
    'news_smartphones', 'news_notebook', 'news_pc', 'news_appliances',
    'news_audio', 'news_monitors', 'news_games',
    'reviews_smartphones', 'reviews_tablets', 'reviews_smart_watches',
    'reviews_accessories', 'reviews_notebooks', 'reviews_audio', 'all_news'
)

URLS = (
    'https://4pda.to/tag/smartphones/', 'https://4pda.to/tag/laptops/', 'https://4pda.to/tag/pc/',
    'https://4pda.to/tag/appliances/', 'https://4pda.to/tag/audio/', 'https://4pda.to/tag/monitors/',
    'https://4pda.to/games/', 'https://4pda.to/reviews/smartphones/', 'https://4pda.to/reviews/tablets/',
    'https://4pda.to/reviews/smart-watches/', 'https://4pda.to/reviews/accessories/',
    'https://4pda.to/reviews/laptops/', 'https://4pda.to/reviews/audio/', 'https://4pda.to/'
)

NAMES = (
    'Новости/Смартфоны', 'Новости/Ноутбуки', 'Новости/ПК', 'Новости/Бытовая техника', 'Новости/Аудио',
    'Новости/Тв и мониторы', 'Новости/Игры', 'Обзоры/Смартфоны', 'Обзоры/Планшеты', 'Обзоры/Умные часы',
    'Обзоры/Аксессуары', 'Обзоры/Ноутбуки', 'Обзоры/Аудио', 'Все новости'
)


class ForPDA:

    def __init__(self):
        self.users_subscribe_status = self.get_users_subscribe_status()
        self.news = self.get_news()
        self.ids_news = {key: list(reversed([item for item in self.news[key]])) for key in self.news}
        self.collect_users_news()

    def get_news(self):
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
                try:
                    description = i.find('p').text
                    if description == '':
                        continue
                except:
                    continue
                data[item_id] = (description, title, href)
                if len(data) == 3:
                    break
            news[cat[0]] = data

        return news

    def get_users_subscribe_status(self):
        users = DataBase().read_all()
        users = {user[0]: get_subscribe_status(user[0]) for user in users}
        return users

    def collect_users_news(self):
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
        self.users_news = users_news


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
        print('сработало')
        fpda = ForPDA()
        users = [int(user) for user in fpda.users_subscribe_status]
        for user in users:
            for cat in fpda.users_news[user]:
                for post_id in fpda.users_news[user][cat]:
                    title = fpda.news[cat][post_id][0]
                    text = fpda.news[cat][post_id][1]
                    url = fpda.news[cat][post_id][2]
                    await bot.send_message(user, url)
                DataBase().update(cat, fpda.ids_news[cat][-1], user)


def main():
    fpda = ForPDA()
    print(fpda.ids_news)


if __name__ == '__main__':
    main()
