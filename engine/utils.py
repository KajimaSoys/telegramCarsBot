from typing import List, NamedTuple, Optional
import db
import ast


def add_row(table, post):# -> Autoru_row:
    """Принимает на вход текст, спаршенный программой"""
    if table == 'autoru':
        inserted_row_id = db.insert(f'{table}',{
            'availability': post.availability,
            'color_hex': post.color_hex,
            'custom_cleared': post.custom_cleared,
            'license_plate': post.license_plate,
            'owners_number': post.owners_number,
            'pts': post.pts,
            'vin': post.vin,
            'vin_resolution': post.vin_resolution,
            'year': post.year,
            'price_rub': post.price_rub,
            'price_eur': post.price_eur,
            'price_usd': post.price_usd,
            'is_official': post.is_official,
            'seller_latitude': post.seller_latitude,
            'seller_longitude': post.seller_longitude,
            'region': post.region,
            'timezone': post.timezone,
            'mileage': post.mileage,
            'body_type': post.body_type,
            'doors_count': post.doors_count,
            'auto_class': post.auto_class,
            'conf_human_name': post.conf_human_name,
            'tech_human_name': post.tech_human_name,
            'trunk_volume_min': post.trunk_volume_min,
            'mark_info': post.mark_info,
            'mark_info_ru': post.mark_info_ru,
            'model_info': post.model_info,
            'model_info_ru': post.model_info_ru,
            'link_img': post.link_img,
            'link_post': post.link_post,
            'sale_id': post.sale_id,
            'search_string': post.search_string,
            'color_text': post.color_text
        })
    elif table =='avito':
        inserted_row_id = db.insert(f'{table}', {
            'year': post.year,
            'price_rub': post.price_rub,
            'description': post.description,
            'region': post.region,
            'mileage': post.mileage,
            'tech_human_name': post.tech_human_name,
            'mark_info': post.mark_info,
            'mark_info_ru': post.mark_info_ru,
            'model_info': post.model_info,
            'model_info_ru': post.model_info_ru,
            'link_img': post.link_img,
            'link_post': post.link_post,
            'sale_id': post.sale_id,
            'search_string': post.search_string})
    return True

def fetch_results(search_str):# -> Autoru_row:
    posts_autoru, count_autoru = db.select_find('autoru', search_str, 'mark_info model_info tech_human_name link_post link_img mileage region price_rub is_official year owners_number color_text'.split())
    posts_avito, count_avito = db.select_find('avito', search_str, 'mark_info model_info tech_human_name link_post link_img mileage region price_rub year'.split())
    count = count_avito + count_autoru
    posts = posts_avito + posts_autoru
    posts = sorted(posts, key=lambda d: d['sml'], reverse=True)
    if count > 50:
        count_message = f'Найдено {str(count)} объявлений. Для просмотра доступны первые 50 записей'
    elif count == 0:
        count_message = 'Не найдено ни одного объявления, попробуйте изменить посиковой запрос :c'
    else:
        count_message = f'Найдено {str(count)} объявлений.'
    return posts, count, count_message


def compare(search_str):# -> Autoru_row:
    posts_autoru, count_autoru = db.select_compare('autoru', search_str, ['price_rub'])
    posts_avito, count_avito = db.select_compare('avito', search_str, ['price_rub'])
    count = count_avito + count_autoru
    posts = posts_avito + posts_autoru
    posts = sorted(posts, key=lambda d: d['sml'], reverse=True)
    return posts, count


def get_text(item):
    if item['db'] == 'autoru':
        if item['owners_number'] == 0:
            car_status = f"Машина с салона\n"
        else:
            car_status = f"Пробег: {item['mileage']}\n" \
                         f"Количество владельцев: {str(item['owners_number'])}\n"

        text = f"{item['mark_info']} {item['model_info']}, {item['year']} года\n" \
               f"Тех. характеристики: {item['tech_human_name']}\n" \
               f"Цвет: {item['color_text']}\n" \
               f"{car_status}" \
               f"Регион: {item['region']}\n" \
               f"Стоимость: {item['price_rub']} рублей\n" \
               f"\nСсылка:\n{item['link_post']}"

    elif item['db'] == 'avito':
        if item['mileage'] == 0:
            car_status = f"Машина с салона\n"
        else:
            car_status = f"Пробег: {item['mileage']}\n"

        text = f"{item['mark_info']} {item['model_info']}, {item['year']} года\n" \
               f"Тех. характеристики: {item['tech_human_name']}\n" \
               f"{car_status}" \
               f"Регион: {item['region']}\n" \
               f"Стоимость: {item['price_rub']} рублей\n" \
               f"\nСсылка:\n{item['link_post']}"

    return text

def get_img(item):
    if item['db'] == 'autoru':
        img = ast.literal_eval(item['link_img'])[0][2:]
    elif item['db'] == 'avito':
        img = item['link_img'].replace('https', 'http') + '.jpg'

    return img