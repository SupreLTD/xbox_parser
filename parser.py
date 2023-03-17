import csv
import requests
from bs4 import BeautifulSoup

import DataBase

link = 'https://www.microsoft.com/tr-tr/store/top-paid/games/xbox'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}


def set_zero_last(numb):
    new_numb = ''
    for index, item in enumerate(str(numb)):
        if index + 1 == len(str(numb)):
            new_numb += '0'
        else:
            new_numb += item
    return new_numb


def currency_rate():
    s = requests.Session()
    ars_rub = s.get('https://www.exchangerates.org.uk/Argentine-Pesos-to-Russian-Roubles-currency-conversion-page.html',
                    headers=headers).text
    ars_rub = BeautifulSoup(ars_rub, 'html.parser').find('span', id='shd2b;').text.replace(',', '.')
    ars_rub = float(ars_rub) * 1.08

    try_rub = s.get('https://www.exchangerates.org.uk/Lira-to-Russian-Roubles-currency-conversion-page.html',
                    headers=headers).text
    try_rub = BeautifulSoup(try_rub, 'html.parser').find('span', id='shd2b;').text.replace(',', '.')
    try_rub = float(try_rub) * 1.08
    return round(ars_rub, 4), round(try_rub, 4)


def parse():
    arg_rub, try_rub = currency_rate()
    ids = []
    id_ = ''

    game_ids = list(DataBase.get_ids())
    while game_ids:
        for game in game_ids[:25]:
            id_ += game[0] + ','
            game_ids.remove(game)
        ids.append(id_)
        id_ = ''

    game_cards = {}
    counter = len(ids)
    count = 0
    for item in ids:
        count += 1
        print(f'{count}/{counter}')
        turk = requests.post(
            'https://storeedgefd.dsx.mp.microsoft.com/v8.0/sdk/products?market=tr&locale=ru-ru&deviceFamily=XBOX',
            json={'productIds': item}).json()
        arg = requests.post(
            'https://storeedgefd.dsx.mp.microsoft.com/v8.0/sdk/products?market=ar&locale=ru-ru&deviceFamily=XBOX',
            json={'productIds': item}).json()

        for turk_product, arg_product in zip(turk['Products'], arg['Products']):
            try:
                try:
                    turk_price = float(
                        turk_product['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData'][
                            'Price']['ListPrice']) * try_rub
                    if turk_price == 0:
                        turk_price = float(
                            turk_product['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData'][
                                'Price']['ListPrice']) * try_rub
                    try:
                        arg_price = float(
                            arg_product['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData'][
                                'Price']['ListPrice']) * arg_rub
                        if arg_price == 0:
                            arg_price = float(
                                arg_product['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData'][
                                    'Price']['ListPrice']) * arg_rub
                    except Exception as e:
                        arg_price = 100000.0
                except Exception as e:
                    try:
                        turk_price = float(
                            turk_product['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData'][
                                'Price']['ListPrice']) * try_rub
                    except Exception as e:
                        continue
                    try:
                        arg_price = float(
                            arg_product['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData'][
                                'Price']['ListPrice']) * arg_rub
                    except Exception as e:
                        arg_price = 100000.0

                if turk_price < arg_price:
                    country = 'Турция'
                    data = turk_product
                    price = turk_price
                    full_price = float(
                        data['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData']['Price'][
                            'MSRP']) * try_rub
                else:
                    country = 'Аргентина'
                    data = arg_product
                    price = arg_price
                    full_price = float(
                        data['DisplaySkuAvailabilities'][0]['Availabilities'][0]['OrderManagementData']['Price'][
                            'MSRP']) * arg_rub

                price = full_price if price == 0 else price

                if price == 0:
                    continue

                price, full_price = round(price), round(full_price)

                if price > full_price:
                    full_price = price

                product_ = False

                for action in data['DisplaySkuAvailabilities'][0]['Availabilities']:
                    if 'Gift' in action['Actions']:
                        product_ = True

                try:
                    game_pass = True if int(
                        turk_product['DisplaySkuAvailabilities'][0]['Availabilities'][1]['OrderManagementData'][
                            'Price']['ListPrice']) == 0 else False
                except Exception as e:
                    game_pass = False

                if not product_:
                    continue
                try:
                    genre = DataBase.get_genre(data['ProductId'])[0]
                except Exception as e:
                    genre = ''

                try:
                    release_date = DataBase.get_release_date(data['ProductId'])[0]
                except Exception as e:
                    release_date = ''

                try:
                    opt_series = DataBase.get_opt_series(data['ProductId'])[0]
                except Exception as e:
                    opt_series = ''

                image = ''
                description = data['LocalizedProperties'][0]['ProductDescription']
                developer_name = data['LocalizedProperties'][0]['DeveloperName']
                publisher_name = data['LocalizedProperties'][0]['PublisherName']
                for i in data['LocalizedProperties'][0]['Images']:
                    if i['ImagePurpose'] == 'BoxArt':
                        image = 'https:' + i['Uri']
                        break

                if not image:
                    for i in data['LocalizedProperties'][0]['Images']:
                        if i['ImagePurpose'] == 'BrandedKeyArt':
                            image = 'https:' + data['Uri']
                            break

                if not image:
                    image = 'https:' + data['LocalizedProperties'][0]['Images'][1]['Uri']

                title = data['LocalizedProperties'][0]['ProductTitle']
                print(data['ProductKind'], title)
                background = 'https:' + data['LocalizedProperties'][0]['Images'][0]['Uri']
                game_cards[title] = {'price': price,
                                     'full_price': full_price,
                                     'country': country,
                                     'description': description,
                                     'image': image,
                                     'genre': genre,
                                     'developer': developer_name,
                                     'publisher': publisher_name,
                                     'background': background,
                                     'gamepass': 'Да' if game_pass else 'Нет',
                                     'opt_series': opt_series,
                                     'release_date': release_date}

            except Exception as e:
                continue

    csvfile = open('data/box.csv', 'w', newline='', encoding='UTF-8')
    fieldnames = ['Корневая', 'Подкатегория 1', 'Название товара', 'Полное описание', 'Тег title',
                  'Мета-тег description', 'Размещение на сайте', 'Изображения', 'Цена продажи', 'Старая цена',
                  'Параметр: Регион активации', 'Цена закупки', 'Жанр', 'Версия', 'Разработчик',
                  'Издатель', 'Background', 'Game Pass', 'Оптимизация XBOX SERIES X|S', 'Дата релиза']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    for game in game_cards:
        title = game
        price = game_cards[game]['price']
        full_price = game_cards[game]['full_price']
        country = game_cards[game]['country']
        description = game_cards[game]['description']
        image = game_cards[game]['image']
        genre = game_cards[game]['genre']
        developer = game_cards[game]['developer']
        publisher = game_cards[game]['publisher']
        background = game_cards[game]['background']
        game_pass = game_cards[game]['gamepass']
        buy_price = int(round(price * 1.05 + 100))
        release_date = game_cards[game]['release_date']
        opt_series = game_cards[game]['opt_series']

        if not 'xbox' in title.lower():
            title = title + ' для Xbox'

        if 0 < price < 300:
            price = set_zero_last(int(round(price + 300)) + 100)

        elif 299 < price < 600:
            price = set_zero_last(int(round((price + 200) * 1.3)) + 100)

        elif 599 < price < 1000:
            price = set_zero_last(int(round((price + 150) * 1.5)) + 100)

        else:
            price = set_zero_last(int(round(price * 1.57)))

        if 0 < full_price < 300:
            full_price = set_zero_last(int(round(full_price + 300)) + 100)

        elif 299 < full_price < 600:
            full_price = set_zero_last(int(round((full_price + 200) * 1.3)) + 100)

        elif 599 < full_price < 1000:
            full_price = set_zero_last(int(round((full_price + 150) * 1.5)) + 100)

        else:
            full_price = set_zero_last(int(round((full_price * 1.57))))

        if int(price) < 750:
            price = 750

        if int(price) > int(full_price):
            full_price = int(price)

        try:
            price += 50
            full_price += 50
        except Exception as e:
            pass

        writer.writerow({'Корневая': 'Xbox', 'Подкатегория 1': 'Игры для Xbox', 'Название товара': title,
                         'Полное описание': description,
                         'Тег title': f'Купить игру {title} для Xbox за {price} на Korobok.Store',
                         'Мета-тег description': f'Игра для Xbox {title}. Купить в консольном дискаунтере Korobok.Store с быстрой цифровой доставкой!',
                         'Размещение на сайте': 'Каталог/Xbox/Игры для Xbox', 'Изображения': image,
                         'Цена продажи': price,
                         'Старая цена': full_price, 'Параметр: Регион активации': country,
                         'Цена закупки': buy_price, 'Жанр': genre, 'Версия': 'Xbox', 'Разработчик': developer,
                         'Издатель': publisher, 'Background': background, 'Game Pass': game_pass,
                         'Оптимизация XBOX SERIES X|S': opt_series, 'Дата релиза': release_date})

    csvfile.close()


