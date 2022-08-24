from data_base_class import DataBase
from aiogram import types
from bs4 import BeautifulSoup
import requests

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
        self.urls = URLS
        self.row_data = self.get_row_data(self.urls)


    # @staticmethod
    # def get_item(url):
    #     articles = BeautifulSoup(requests.get(url).text, features="html.parser").find_all('article', class_='post')
    #     if articles[0].find('p').text:
    #         return articles[0].get('itemid')
    #     else:
    #         return articles[1].get('itemid')

    def get_row_data(self, urls):
        row_data = {}
        for url in urls:
            html = requests.get(url).text
            soup = BeautifulSoup(html, features="html.parser")
            articles = soup.find_all('article', class_='post')
            data = []
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
                data.append((description, title, href, item_id))
                if len(data) == 10:
                    break
            row_data[url] = data

        return row_data




def create_data_dict() -> dict:
    data = dict().fromkeys(CATEGORIES)
    for num, val in enumerate(data):
        data[val] = {}
        data[val]['url'] = URLS[num]
        data[val]['name'] = NAMES[num]
        data[val]['btn'] = types.InlineKeyboardButton(data[val]['name'], callback_data=val)
    return data


def check_user(user_id):
    if DataBase().read_one(user_id):
        return 'OK'
    else:
        DataBase().insert(user_id)

def get_item(url):
    articles = BeautifulSoup(requests.get(url).text, features="html.parser").find_all('article', class_='post')
    if articles[0].find('p').text:
        return articles[0].get('itemid')
    else:
        return articles[1].get('itemid')

def main():
    get_item(URLS[1])


if __name__ == '__main__':
    main()
