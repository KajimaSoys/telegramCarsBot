import requests #Библиотека для запроса
from typing import List, NamedTuple, Optional
from utils import add_row
import random
from variables import *
import db
import webcolors

class Parsed_post(NamedTuple):
    availability: str
    color_hex: str
    # description: str
    custom_cleared: bool
    license_plate: str
    owners_number: int
    pts: str
    vin: str
    vin_resolution: str
    year: int
    price_rub: int
    price_eur: int
    price_usd: int
    is_official: bool
    seller_latitude: float
    seller_longitude: float
    region: str
    timezone: str
    mileage: int
    body_type: str
    doors_count: int
    auto_class: str
    conf_human_name: str
    tech_human_name: str
    trunk_volume_min: int
    mark_info: str
    mark_info_ru: str
    model_info: str
    model_info_ru: str
    # lk_summary: str
    link_img: str
    link_post: str
    sale_id: str
    search_string: str
    color_text: str

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
    return closest_name

def try_repeat(func):
    def wrapper(*args, **kwargs):
        count = 20

        while count:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # print('Error:', e)
                count -= 1

    return wrapper

@try_repeat
def get_response(page):
    url = 'https://auto.ru/-/ajax/desktop/listing/'

    params = {
        'catalog_filter': 'all',  # [{"mark": "MAZDA"}],
        'section': "all",
        'category': "cars",
        'sort': "fresh_relevance_1-desc",
        'page': page
    }

    user_agent_list=[
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
    ]

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'content-type': 'application/json',
        'Cookie': '_csrf_token=1c0ed592ec162073ac34d79ce511f0e50d195f763abd8c24; autoru_sid=a%3Ag5e3b198b299o5jhpv6nlk0ro4daqbpf.fa3630dbc880ea80147c661111fb3270%7C1580931467355.604800.8HnYnADZ6dSuzP1gctE0Fw.cd59AHgDSjoJxSYHCHfDUoj-f2orbR5pKj6U0ddu1G4; autoruuid=g5e3b198b299o5jhpv6nlk0ro4daqbpf.fa3630dbc880ea80147c661111fb3270; suid=48a075680eac323f3f9ad5304157467a.bc50c5bde34519f174ccdba0bd791787; from_lifetime=1580933172327; from=yandex; X-Vertis-DC=myt; crookie=bp+bI7U7P7sm6q0mpUwAgWZrbzx3jePMKp8OPHqMwu9FdPseXCTs3bUqyAjp1fRRTDJ9Z5RZEdQLKToDLIpc7dWxb90=; cmtchd=MTU4MDkzMTQ3MjU0NQ==; yandexuid=1758388111580931457; bltsr=1; navigation_promo_seen-recalls=true',
        'Host': 'auto.ru',
        'origin': 'https://auto.ru',
        # 'Referer': 'https://auto.ru/ryazan/cars/mercedes/all/',
        'User-Agent': '',
        'x-client-app-version': '202002.03.092255',
        'x-client-date': '1580933207763',
        'x-csrf-token': '1c0ed592ec162073ac34d79ce511f0e50d195f763abd8c24',
        # 'x-page-request-id': '60142cd4f0c0edf51f96fd0134c6f02a',
        # 'x-requested-with': 'fetch'
    }

    user_agent = random.choice(user_agent_list)
    headers['User-Agent'] = user_agent
    # print(user_agent)

    session_id = random.random()
    super_proxy_url = ('http://%s-country-ru-session-%s:%s@zproxy.lum-superproxy.io:%d' %
                       (username, session_id, password, port))
    proxies = {
        "http": super_proxy_url,
        "https": super_proxy_url
    }

    response = requests.post(url, json=params, headers=headers, proxies=proxies)
    data = response.json()['offers']
    return data


def parsing() -> Parsed_post:
    current_posts = db.handle_all('autoru', 'sale_id')
    # print(current_posts)


    pages = 1  # Переменная для перехода по страницам
    while pages <= 99:  # Всего 99 страниц на сайте
        # Параметры запроса
        print(f'Current page is {pages}')

        try:
            data = get_response(pages)
        except KeyboardInterrupt:
            break
        except:
            print(f'Не удалось спарсить страницу №{pages}')
            pages += 1
            continue

        # with open('parse2.json', 'w', encoding='UTF-8') as file:
        #     file.write(str(data))

        i = 0  # Переменная для перехода по объявлениям
        while i <= len(data) - 1:  # len(data)-1 это количество пришедших объявлений
            search_sting = ''


            # Доступность объявления
            try:
                availability = str(data[i]['availability'])
            except:
                availability = 'Not availability'

            # Категория автомобиля
            try:
                category = str(data[i]['category'])
            except:
                category = 'Not category'

            # Цвет автомобиля
            try:
                color_hex = str(data[i]["color_hex"])
                color_rgb = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
                color_text = get_colour_name(color_rgb)
                try:
                    color_text = colors_list[color_text]
                    search_sting += color_text
                except:
                    pass
            except:
                color_hex = 'Not color'


            # Описание автомобиля
            # try:
            #     description = str(data[i]['description'])
            # except:
            #     description = 'Not description'

            # Растаможен ли автомобиль (возвращает True или False)
            try:
                custom_cleared = bool(data[i]['documents']['custom_cleared'])
            except:
                custom_cleared = False

            # Лицензия на автомобиль
            try:
                license_plate = str(data[i]['documents']['license_plate'])
            except:
                license_plate = 'Not license plate '

            # Колличество владельцев автомобиля
            try:
                owners_number = int(data[i]['documents']['owners_number'])
            except:
                owners_number = 0

            # PTS автомобиля
            try:
                pts = str(data[i]['documents']['pts'])
            except:
                pts = 'Not PTS'

            # VIN автомобиля
            try:
                vin = str(data[i]['documents']['vin'])
            except:
                vin = 'Not VIN'

            try:
                vin_resolution = str(data[i]['documents']['vin_resolution'])
            except:
                vin_resolution = 'Not vin resolution '

            # Год выпуска автомобиля
            try:
                year = int(data[i]['documents']['year'])
                search_sting += f' {str(year)}'
            except:
                year = 0

            # Цена в рублях, евро и долларах
            try:
                price_rub = int(data[i]['price_info']['RUR'])
            except:
                price_rub = 0

            try:
                price_eur = int(data[i]['price_info']['EUR'])
            except:
                price_eur = 0

            try:
                price_usd = int(data[i]['price_info']['USD'])
            except:
                price_usd = 0

            # С салона ли машина или нет
            try:
                is_official = bool(data[i]['salon']['is_official'])
                if is_official:
                    search_sting += ' с салона'
            except:
                is_official = False

            # Координаты места нахождения машины (возвращается долгота и широта)
            try:
                seller_latitude = float(data[i]['seller']['location']['coord']['latitude'])
                seller_longitude = float(data[i]['seller']['location']['coord']['longitude'])
            except:
                seller_latitude = 0
                seller_longitude = 0

            # Регион, в котором находится автомобиль
            try:
                region = str(data[i]['seller']['location']['region_info']['name'])
                search_sting += f' {region}'
            except:
                region = 'Not region'

            # Временная зона в которой находится автомобиль
            try:
                timezone = str(data[i]['seller']['location']['timezone_info']['abbr'])
            except:
                timezone = 'Not timezone'

            # Пробег автомобиля
            try:
                mileage = int(data[i]['state']['mileage'])
            except:
                mileage = 0

            # Картинки автомобиля
            # Возвращается несколько фото, мы их добавляем в словарь img_url
            img_url = []
            for img in data[i]['state']['image_urls']:
                img_url.append(img['sizes']['1200x900'])
            link_img = str(img_url)

            # Тип автомобиля
            try:
                body_type = str(data[i]['vehicle_info']['configuration']['body_type'])
            except:
                body_type = 'Not body_type auto'

            # Количество дверей у автомобиля
            try:
                doors_count = int(data[i]['vehicle_info']['configuration']['doors_count'])
            except:
                doors_count = 0

            # Класс автомобиля
            try:
                auto_class = str(data[i]['vehicle_info']['configuration']['auto_class'])
            except:
                auto_class = 'Not class auto'

            # Название автомобиля
            try:
                conf_human_name = str(data[i]['vehicle_info']['configuration']['human_name'])
                search_sting += f' {conf_human_name}'
            except:
                conf_human_name = 'Not name auto'

            # Объем багажника автомобиля
            try:
                trunk_volume_min = int(data[i]['vehicle_info']['configuration']['trunk_volume_min'])
            except:
                trunk_volume_min = 0

            # Марка автомобиля
            try:
                mark_info = str(data[i]['vehicle_info']['mark_info']['name'])
                search_sting += f' {mark_info}'
            except:
                mark_info = 'Not marka info'

            # Марка автомобиля на русском
            try:
                mark_info_ru = str(data[i]['vehicle_info']['mark_info']['ru_name'])
                search_sting += f' {mark_info_ru}'
            except:
                mark_info_ru = 'Not marka info'

            # Модель автомобиля
            try:
                model_info = str(data[i]['vehicle_info']['model_info']['name'])
                search_sting += f' {model_info}'
            except:
                model_info = 'Not model info'

            # Модель автомобиля на русском
            try:
                model_info_ru = str(data[i]['vehicle_info']['model_info']['ru_name'])
                search_sting += f' {model_info_ru}'
            except:
                model_info_ru = 'Not model info'

            # Технические характеристики
            try:
                tech_human_name = str(data[i]['vehicle_info']['tech_param']['human_name'])
                # search_sting += f' {tech_human_name}'
            except:
                tech_human_name = 'Not tech human name'

            # Информация об автомобиле
            # try:
            #     lk_summary = str(data[i]['lk_summary'])
            # except:
            #     lk_summary = 'Not ik summary'

            sale_id = str(data[i]['saleId'])

            link_post = f'https://auto.ru/cars/used/sale/{sale_id}/'

            i += 1

            if sale_id in current_posts:
                continue

            temp = Parsed_post(availability=availability,
                               color_hex=color_hex,
                               custom_cleared=custom_cleared,
                               license_plate=license_plate,
                               owners_number=owners_number,
                               pts=pts,
                               vin=vin,
                               vin_resolution=vin_resolution,
                               year=year,
                               price_rub=price_rub,
                               price_eur=price_eur,
                               price_usd=price_usd,
                               is_official=is_official,
                               seller_latitude=seller_latitude,
                               seller_longitude=seller_longitude,
                               region=region,
                               timezone=timezone,
                               mileage=mileage,
                               body_type=body_type,
                               doors_count=doors_count,
                               auto_class=auto_class,
                               conf_human_name=conf_human_name,
                               tech_human_name=tech_human_name,
                               trunk_volume_min=trunk_volume_min,
                               mark_info=mark_info,
                               mark_info_ru=mark_info_ru,
                               model_info=model_info,
                               model_info_ru=model_info_ru,
                               link_img=link_img,
                               link_post=link_post,
                               sale_id=sale_id,
                               search_string=search_sting,
                               color_text=color_text)

            result = add_row('autoru', temp)

        pages += 1

    return True

def main():
    if parsing():
        print('Successful parsing')
    db.delete_dupes(table='autoru', column='sale_id')
    db.reindex()

if __name__ == '__main__':
    main()
