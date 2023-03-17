import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


import DataBase

link = 'https://www.microsoft.com/tr-tr/store/top-paid/games/xbox'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}


def fast_parse():
    data = requests.get(link, headers=headers).text
    soup = BeautifulSoup(data, 'html.parser')
    objects = soup.find('div', class_='f-wrap-items').findChildren('a')

    items_length = int(soup.find('p', class_='c-paragraph-3').text.split()[0].strip())
    skiped_items = 90

    while items_length > skiped_items:
        page = requests.get(
            f'https://www.microsoft.com/tr-tr/store/top-paid/games/xbox?s=store&skipitems={skiped_items}',
            headers=headers).text
        objects.extend(BeautifulSoup(page, 'html.parser').find('div', class_='f-wrap-items').findChildren('a'))
        skiped_items += 90

    while objects:
        for a in objects:
            game_id = eval(a.get('data-m'))['pid']
            objects.remove(a)
            if not DataBase.check_id(game_id):
                DataBase.insert_id(game_id, '')


def slow_parse():
    data = requests.get(link, headers=headers).text
    soup = BeautifulSoup(data, 'html.parser')
    objects = soup.find('ul', class_='row').findChildren('a')

    print(len(objects))

    items_length = int(soup.find('div', id='status-container-1').find_all('span')[-1].text.split()[0].strip())
    skiped_items = 90
    links = []

    print(items_length)

    while items_length > skiped_items:
        page = requests.get(
            f'https://www.microsoft.com/tr-tr/store/top-paid/games/xbox?s=store&skipitems={skiped_items}',
            headers=headers).text
        objects.extend(BeautifulSoup(page, 'html.parser').find('ul', class_='row').findChildren('a'))
        skiped_items += 90

    games = {}

    while objects:
        for a in objects:
            game_id = a.get('href').split('/')[-1]
            game_link = a.get('href')
            games[game_link] = game_id
            links.append(game_link)
            objects.remove(a)

    print(links)
    counter = len(links)
    for count, link_ in tqdm(enumerate(links)):
        try:
            print(f'{count}/{counter}')
            data = requests.get(link_, headers=headers).text
            soup = BeautifulSoup(data, 'html.parser')

            if not DataBase.check_id(games[link_]):
                print(link_)

                data_tr = requests.get(link_).text
                soup_tr = BeautifulSoup(data_tr, 'html.parser')

                try:
                    if soup_tr.find('div', class_='DescriptionModulesContainer-module__rowMargin___1QVBu').text.count('X|S'):
                        opt_series = 'Есть'
                    else:
                        opt_series = 'Нет'
                except:
                    opt_series = 'Нет'

                release_date = ''
                for i in soup_tr.find_all('h3', class_='typography-module__xdsBody1___2-8Fc'):
                    if i.text == 'Çıkış tarihi':
                        release_date = i.findNext('div', class_='typography-module__xdsBody2___1XDyq').text

                data2 = requests.get(link_.replace('tr-tr', 'ru-ru')).text

                soup3 = BeautifulSoup(data2, 'html.parser')
                try:
                    genre = soup3.find('div', {'class': 'typography-module__xdsSubTitle1___2twuH'}).findChild('span').text.split(' • ')[-1]
                except:
                    genre = ''
                print(genre)

                DataBase.insert_id(games[link_], genre, release_date, opt_series)

            for numb, a in enumerate(soup.find_all('a', class_='ProductCard-module__cardWrapper___32w0a')):
                try:
                    link_2 = a.get('href')
                    game_id = link_2.split('/')[-1]
                    if len(game_id) == 4:
                        game_id = link_2.split('/')[-2]
                    if not DataBase.check_id(game_id):
                        print(f'-{numb}', link_2)
                        data_tr = requests.get(link_2).text
                        soup_tr = BeautifulSoup(data_tr, 'html.parser')

                        try:
                            if soup_tr.find('div', class_='DescriptionModulesContainer-module__rowMargin___1QVBu').text.count('X|S'):
                                opt_series = 'Есть'
                            else:
                                opt_series = 'Нет'
                        except:
                            opt_series = 'Нет'

                        release_date = ''
                        for i in soup_tr.find_all('h3', class_='typography-module__xdsBody1___2-8Fc'):
                            if i.text == 'Çıkış tarihi':
                                release_date = i.findNext('div', class_='typography-module__xdsBody2___1XDyq').text

                        data2 = requests.get(link_2.replace('tr-TR', 'ru-ru')).text
                        soup3 = BeautifulSoup(data2, 'html.parser')
                        try:
                            genre = soup3.find('div', {'class': 'typography-module__xdsSubTitle1___2twuH'}).findChild(
                                'span').text.split(' • ')[-1]
                        except:
                            genre = ''
                        # print(genre)
                        DataBase.insert_id(game_id, genre, release_date, opt_series)
                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            print(e)
            continue
# /ru-ru/p/dakar-desert-rally-deluxe-edition/9n9zjhl09vh3?cid=msft_web_chart
# https://www.xbox.com/ru-ru/games/store/dakar-desert-rally-deluxe-edition/9n9zjhl09vh3?cid=msft_web_chart

