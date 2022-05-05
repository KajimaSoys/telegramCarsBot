import time

import requests #Библиотека для запроса
import ssl
from bs4 import BeautifulSoup
import re
from pytils import translit
from utils import add_row
import db

from fake_useragent import UserAgent
# import asyncio
# import aiohttp

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

from typing import List, NamedTuple, Optional
import random
from variables import *

CIPHERS = """ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SHA"""

class TlsAdapter(HTTPAdapter):

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(ciphers=CIPHERS, cert_reqs=ssl.CERT_REQUIRED, options=self.ssl_options)
        self.poolmanager = PoolManager(*pool_args, ssl_context=ctx, **pool_kwargs)

session = requests.session()
adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
session.mount("https://", adapter)

class Parsed_post(NamedTuple):
    sale_id: str
    mark_info: str
    mark_info_ru: str
    model_info: str
    model_info_ru: str
    year: int
    price_rub: int
    mileage: int
    tech_human_name: str
    region: str
    description: str
    link_post: str
    link_img: str
    search_string: str

# names = []
#
# async def get_page_data(session, link, sslcontext):
#     print(f'Собираю данные со страницы: {link}')
#     headers = {
#         'authority': 'www.avito.ru',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'Accept-encoding': 'gzip, deflate, br',
#         'Accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#         'Cookie': 'u=2ophjau7.1dm0jl9.1ty11d02mit00; _ym_uid=1620854801394168664; _ym_d=1637103598; buyer_laas_location=621540; auth=1; showedStoryIds=122-121-120-116-115-113-112-111-108-105-104-103-99-98-97-96-94-88-83-78-71; _gcl_au=1.1.425858945.1650305340; abp=1; _ym_isad=1; _gid=GA1.2.838819019.1651453850; f=5.32e32548b6f3e9784b5abdd419952845a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e94f9572e6986d0c624f9572e6986d0c624f9572e6986d0c62ba029cd346349f36c1e8912fd5a48d02c1e8912fd5a48d0246b8ae4e81acb9fa143114829cf33ca746b8ae4e81acb9fa46b8ae4e81acb9fae992ad2cc54b8aa8cad08e7e7eb412c8fa4d7ea84258c63d59c9621b2c0fa58f915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047fb0fb526bb39450a46b8ae4e81acb9fa34d62295fceb188dd99271d186dc1cd03de19da9ed218fe2d50b96489ab264edd50b96489ab264ed1a2a574992f83a9246b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335c03d3f0af72d633b5db6aace19274a12602c730c0109b9fbb4b423595c3d74038ecef446960d8bdd029aa4cecca288d6b2886f2ffe1daba12f65dca5b7a8f203146b8ae4e81acb9fa46b8ae4e81acb9fa02c68186b443a7ac7c629922cb33e2178ad73f69f517ac602da10fb74cac1eab2da10fb74cac1eabb8ad5716a08515fcc3bc1996b09f17c33778cee096b7b985bf37df0d1894b088; ft="Ip/7DLX1jpV8/V+p73xBhueqt/8fW1ttN2cYsp+xck5brvc5Xuk9GFW5T9+qVV1Zkm5IxaplJ85S0+6bGKkkY/yP8RcFuWxxPgy178hqPt010PMy5IEOqj3uuA43J1wP5EzG2cfKG5oGzazq+VYiUQ00kP8aSuCIgwKpjGFfbcVSglgKsQUlGbwcz3xqhCOW"; buyer_location_id=621540; buyer_popup_location=621540; v=1651510853; _ym_visorc=b; luri=rossiya; SEARCH_HISTORY_IDS=0%2C4%2C; _dc_gtm_UA-2546784-1=1; dfp_group=95; _ga=GA1.1.1180960058.1650305341; sx=H4sIAAAAAAAC%2F5zSS9LqNhAF4L14zED9UKt1d6OnMQZsY4zAt9h76k8VqXBnyQa%2BOt3n%2FO4MWiJEa63hkIwSp2RK9pA8BeNc9%2Bt39%2Bh%2BddDfX%2BHKFPbwdDveL2lbL0vP0%2FU1zaHvDl3pfoFYsGzAm%2FehM2wTe4XiQYMFCkKFHNSo4BMzfmQ9xWohhOG6PfKx8vIcdRmKodBWwPFLFgfvQ8dakLJgjhCzQU4UxArEGjFCtv4jb%2BsOxpoeTue1%2BTG7eDo%2Fpkj1PtqypW%2BZ%2FfvQSWY2pGo0VvHFi%2BZUAGOwKCQcP3Kyc9n38XhZErJ91OPWLv3Yhu0Ca7r7f8neqfD70GnMAW1IsVLJUGooEDKioECq6uAjvx55QQuL332Zl%2BF%2Br601NXCBOLQ5fGcGeR86XyWbWFlijBldgZAqikXMJKRRPnLtjQlPzrdxc%2FOz3nbM%2FLAjDk5F2%2FKVmQXfhy4KRsyGbQnowBRNtoijSuSCYK0fuU2%2BTqUm3o5jD6vs05kdXR50fPHZ2e9v2J9vpOm8M23u2DSt%2Fco6ttXoOK3%2FZxTu7%2Boy9jZn1fuNx76xTsak1jdu%2F530Di39kFSkRjY%2BWiIjtbBYLwG55CLF%2FrOGtmhZEfimY5vCJapcx3JS38a5968%2F7qef%2B3ORoIIYGYXYc43orKkxUYy2Fv3I%2B9TPW3re9qH1t%2BnF2Pv01HQrjvbhNX2vgX4ylypRPUshgsRMOWUMyWEFWzm4%2FJFNMDD7BDNO13J39lqvRzm1WWDQuh%2F%2F6My9338FAAD%2F%2F14Sh9UrBAAA; _ga_9E363E7BES=GS1.1.1651510922.4.1.1651511533.30',
#         'Upgrade-insecure-requests': '1',
#         'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
#         'sec-fetch-site': 'none',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-user': '?1',
#         'sec-fetch-dest': 'document',
#         'pragma': 'no-cache',
#         'cache-control': 'no-cache',
#     }
#
#     async with session.get(url=f'https://www.avito.ru{link}', headers=headers, ssl=sslcontext) as response:
#         response_text = await response.text()
#         with open('avito_page.html', 'w+', encoding='UTF-8') as file:
#             file.write(response_text)
#         soup = BeautifulSoup(response_text, features='html.parser')
#
#         name = soup.find('div', attrs={'class':'page-title-root-cK8oN.js-page-title'})
#         print(name)
#         names.append(name.get_text())
#     print(names)
#
#
# async def gather_links():
#     url = 'https://www.avito.ru/rossiya/avtomobili?p=1'
#     headers = {
#         'authority': 'www.avito.ru',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'Accept-encoding': 'gzip, deflate, br',
#         'Accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#         'Cookie': 'u=2ophjau7.1dm0jl9.1ty11d02mit00; _ym_uid=1620854801394168664; _ym_d=1637103598; buyer_laas_location=621540; auth=1; showedStoryIds=122-121-120-116-115-113-112-111-108-105-104-103-99-98-97-96-94-88-83-78-71; _gcl_au=1.1.425858945.1650305340; abp=1; _ym_isad=1; _gid=GA1.2.838819019.1651453850; f=5.32e32548b6f3e9784b5abdd419952845a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e94f9572e6986d0c624f9572e6986d0c624f9572e6986d0c62ba029cd346349f36c1e8912fd5a48d02c1e8912fd5a48d0246b8ae4e81acb9fa143114829cf33ca746b8ae4e81acb9fa46b8ae4e81acb9fae992ad2cc54b8aa8cad08e7e7eb412c8fa4d7ea84258c63d59c9621b2c0fa58f915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047fb0fb526bb39450a46b8ae4e81acb9fa34d62295fceb188dd99271d186dc1cd03de19da9ed218fe2d50b96489ab264edd50b96489ab264ed1a2a574992f83a9246b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335c03d3f0af72d633b5db6aace19274a12602c730c0109b9fbb4b423595c3d74038ecef446960d8bdd029aa4cecca288d6b2886f2ffe1daba12f65dca5b7a8f203146b8ae4e81acb9fa46b8ae4e81acb9fa02c68186b443a7ac7c629922cb33e2178ad73f69f517ac602da10fb74cac1eab2da10fb74cac1eabb8ad5716a08515fcc3bc1996b09f17c33778cee096b7b985bf37df0d1894b088; ft="Ip/7DLX1jpV8/V+p73xBhueqt/8fW1ttN2cYsp+xck5brvc5Xuk9GFW5T9+qVV1Zkm5IxaplJ85S0+6bGKkkY/yP8RcFuWxxPgy178hqPt010PMy5IEOqj3uuA43J1wP5EzG2cfKG5oGzazq+VYiUQ00kP8aSuCIgwKpjGFfbcVSglgKsQUlGbwcz3xqhCOW"; buyer_location_id=621540; buyer_popup_location=621540; v=1651510853; _ym_visorc=b; luri=rossiya; SEARCH_HISTORY_IDS=0%2C4%2C; _dc_gtm_UA-2546784-1=1; dfp_group=95; _ga=GA1.1.1180960058.1650305341; sx=H4sIAAAAAAAC%2F5zSS9LqNhAF4L14zED9UKt1d6OnMQZsY4zAt9h76k8VqXBnyQa%2BOt3n%2FO4MWiJEa63hkIwSp2RK9pA8BeNc9%2Bt39%2Bh%2BddDfX%2BHKFPbwdDveL2lbL0vP0%2FU1zaHvDl3pfoFYsGzAm%2FehM2wTe4XiQYMFCkKFHNSo4BMzfmQ9xWohhOG6PfKx8vIcdRmKodBWwPFLFgfvQ8dakLJgjhCzQU4UxArEGjFCtv4jb%2BsOxpoeTue1%2BTG7eDo%2Fpkj1PtqypW%2BZ%2FfvQSWY2pGo0VvHFi%2BZUAGOwKCQcP3Kyc9n38XhZErJ91OPWLv3Yhu0Ca7r7f8neqfD70GnMAW1IsVLJUGooEDKioECq6uAjvx55QQuL332Zl%2BF%2Br601NXCBOLQ5fGcGeR86XyWbWFlijBldgZAqikXMJKRRPnLtjQlPzrdxc%2FOz3nbM%2FLAjDk5F2%2FKVmQXfhy4KRsyGbQnowBRNtoijSuSCYK0fuU2%2BTqUm3o5jD6vs05kdXR50fPHZ2e9v2J9vpOm8M23u2DSt%2Fco6ttXoOK3%2FZxTu7%2Boy9jZn1fuNx76xTsak1jdu%2F530Di39kFSkRjY%2BWiIjtbBYLwG55CLF%2FrOGtmhZEfimY5vCJapcx3JS38a5968%2F7qef%2B3ORoIIYGYXYc43orKkxUYy2Fv3I%2B9TPW3re9qH1t%2BnF2Pv01HQrjvbhNX2vgX4ylypRPUshgsRMOWUMyWEFWzm4%2FJFNMDD7BDNO13J39lqvRzm1WWDQuh%2F%2F6My9338FAAD%2F%2F14Sh9UrBAAA; _ga_9E363E7BES=GS1.1.1651510922.4.1.1651511533.30',
#         'Upgrade-insecure-requests': '1',
#         'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
#         'sec-fetch-site': 'none',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-user': '?1',
#         'sec-fetch-dest': 'document',
#         'pragma': 'no-cache',
#         'cache-control': 'no-cache',
#     }
#
#     # response = session.request(method='GET', url=url, headers=headers)
#     # with open('avito_parse_test.html', 'w+', encoding='UTF-8') as file:
#     #     file.write(response.text)
#
#     FORCED_CIPHERS = (
#         'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
#         'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES'
#     )
#
#     sslcontext = ssl.create_default_context()
#
#     sslcontext.options |= ssl.OP_NO_TLSv1_2
#     sslcontext.set_ciphers(FORCED_CIPHERS)
#
#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector( limit=4)) as session:
#
#
#
#         response = await session.get(url=url, headers=headers, ssl=sslcontext)
#         soup = BeautifulSoup(await response.text(), features="html.parser")
#
#         links = []
#         with open('avito_parse_test.html', 'w+', encoding='UTF-8') as file:
#             file.write(await response.text())
#
#         items = soup.find_all('div', 'popular-rubricator-row-xX6S9')
#         print(len(items))
#
#         for item in soup.find_all('div', 'popular-rubricator-row-xX6S9'):
#             temp = item.find('a')
#             links.append(temp['href'])
#
#
#         tasks = []
#
#         for link in links:
#             task = asyncio.create_task(get_page_data(session, link, sslcontext))
#             tasks.append(task)
#
#         await  asyncio.gather(*tasks)
#         # for link in links
#
#
#
#     # links = []
#     # for item in soup.find_all('div', 'popular-rubricator-row-xX6S9'):
#     #     temp = item.find('a')
#     #     links.append(temp['href'])
#     #
#     # print(links)
#     return True


headers = {
    'authority': 'www.avito.ru',
    'Accept': '*/*',
    'Accept-encoding': 'gzip, deflate, br',
    'Accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'Cookie': 'u=2ophjau7.1dm0jl9.1ty11d02mit00; _ym_uid=1620854801394168664; _ym_d=1637103598; buyer_laas_location=621540; auth=1; showedStoryIds=122-121-120-116-115-113-112-111-108-105-104-103-99-98-97-96-94-88-83-78-71; _gcl_au=1.1.425858945.1650305340; abp=1; _ym_isad=1; _gid=GA1.2.838819019.1651453850; f=5.32e32548b6f3e9784b5abdd419952845a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e9a68643d4d8df96e94f9572e6986d0c624f9572e6986d0c624f9572e6986d0c62ba029cd346349f36c1e8912fd5a48d02c1e8912fd5a48d0246b8ae4e81acb9fa143114829cf33ca746b8ae4e81acb9fa46b8ae4e81acb9fae992ad2cc54b8aa8cad08e7e7eb412c8fa4d7ea84258c63d59c9621b2c0fa58f915ac1de0d034112ad09145d3e31a56946b8ae4e81acb9fae2415097439d4047fb0fb526bb39450a46b8ae4e81acb9fa34d62295fceb188dd99271d186dc1cd03de19da9ed218fe2d50b96489ab264edd50b96489ab264ed1a2a574992f83a9246b8ae4e81acb9fa38e6a683f47425a8352c31daf983fa077a7b6c33f74d335c03d3f0af72d633b5db6aace19274a12602c730c0109b9fbb4b423595c3d74038ecef446960d8bdd029aa4cecca288d6b2886f2ffe1daba12f65dca5b7a8f203146b8ae4e81acb9fa46b8ae4e81acb9fa02c68186b443a7ac7c629922cb33e2178ad73f69f517ac602da10fb74cac1eab2da10fb74cac1eabb8ad5716a08515fcc3bc1996b09f17c33778cee096b7b985bf37df0d1894b088; ft="Ip/7DLX1jpV8/V+p73xBhueqt/8fW1ttN2cYsp+xck5brvc5Xuk9GFW5T9+qVV1Zkm5IxaplJ85S0+6bGKkkY/yP8RcFuWxxPgy178hqPt010PMy5IEOqj3uuA43J1wP5EzG2cfKG5oGzazq+VYiUQ00kP8aSuCIgwKpjGFfbcVSglgKsQUlGbwcz3xqhCOW"; buyer_location_id=621540; buyer_popup_location=621540; v=1651510853; _ym_visorc=b; luri=rossiya; SEARCH_HISTORY_IDS=0%2C4%2C; _dc_gtm_UA-2546784-1=1; dfp_group=95; _ga=GA1.1.1180960058.1650305341; sx=H4sIAAAAAAAC%2F5zSS9LqNhAF4L14zED9UKt1d6OnMQZsY4zAt9h76k8VqXBnyQa%2BOt3n%2FO4MWiJEa63hkIwSp2RK9pA8BeNc9%2Bt39%2Bh%2BddDfX%2BHKFPbwdDveL2lbL0vP0%2FU1zaHvDl3pfoFYsGzAm%2FehM2wTe4XiQYMFCkKFHNSo4BMzfmQ9xWohhOG6PfKx8vIcdRmKodBWwPFLFgfvQ8dakLJgjhCzQU4UxArEGjFCtv4jb%2BsOxpoeTue1%2BTG7eDo%2Fpkj1PtqypW%2BZ%2FfvQSWY2pGo0VvHFi%2BZUAGOwKCQcP3Kyc9n38XhZErJ91OPWLv3Yhu0Ca7r7f8neqfD70GnMAW1IsVLJUGooEDKioECq6uAjvx55QQuL332Zl%2BF%2Br601NXCBOLQ5fGcGeR86XyWbWFlijBldgZAqikXMJKRRPnLtjQlPzrdxc%2FOz3nbM%2FLAjDk5F2%2FKVmQXfhy4KRsyGbQnowBRNtoijSuSCYK0fuU2%2BTqUm3o5jD6vs05kdXR50fPHZ2e9v2J9vpOm8M23u2DSt%2Fco6ttXoOK3%2FZxTu7%2Boy9jZn1fuNx76xTsak1jdu%2F530Di39kFSkRjY%2BWiIjtbBYLwG55CLF%2FrOGtmhZEfimY5vCJapcx3JS38a5968%2F7qef%2B3ORoIIYGYXYc43orKkxUYy2Fv3I%2B9TPW3re9qH1t%2BnF2Pv01HQrjvbhNX2vgX4ylypRPUshgsRMOWUMyWEFWzm4%2FJFNMDD7BDNO13J39lqvRzm1WWDQuh%2F%2F6My9338FAAD%2F%2F14Sh9UrBAAA; _ga_9E363E7BES=GS1.1.1651510922.4.1.1651511533.30',
    # 'Upgrade-insecure-requests': '1',
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    # 'sec-fetch-site': 'none',
    # 'sec-fetch-mode': 'navigate',
    # 'sec-fetch-user': '?1',
    # 'sec-fetch-dest': 'document',
    # 'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'connection': 'keep-alive',
}


def find_pages(link):
    response = session.request(method='GET', url=f'https://www.avito.ru{link}').text
    soup = BeautifulSoup(response, features='html.parser')
    try:
        pages = int(soup.find_all('span', 'pagination-item-JJq_j')[-2].text)
    except Exception as E:
        print(f'[Error] While parsing the {link}\n{E}')
        pages = 1
    finally:
        return pages


def try_repeat(func):
    def wrapper(*args, **kwargs):
        count = 20

        while count:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('Error:', e)
                count -= 1

    return wrapper


@try_repeat
def get_response(url):
    # user_agent_list = [
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    #     'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
    # ]
    #
    # user_agent = random.choice(user_agent_list)
    ua = UserAgent()
    headers['User-agent'] = ua.chrome

    session_id = random.random()
    super_proxy_url = ('http://%s-country-ru-session-%s:%s@zproxy.lum-superproxy.io:%d' %
                       (username, session_id, password, port))
    proxies = {
        "http": super_proxy_url,
        "https": super_proxy_url
    }

    session = requests.session()
    adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
    session.mount("https://", adapter)

    session.headers = headers
    # session.proxies = proxies
    session.headers.update(headers)
    # session.proxies.update(proxies)

    # i = session.get('http://ifconfig.co', timeout=11)
    # print(f"successfull - IP ---> ", end='')
    # zu = BeautifulSoup(i.text, 'html.parser')
    # testo = zu.findAll('p', text=True)[0].get_text()
    # print(testo)


    response = session.get(url).text
    soup = BeautifulSoup(response, features='html.parser')
    # with open('avito_page.html', 'w+', encoding='UTF-8') as file:
    #     file.write(response)
    if 'Доступ ограничен' in soup.find('title').text:
        raise Exception
    return soup

def get_data(link, page):
    url = f'https://www.avito.ru{link}&p={page}'
    time.sleep(2)
    try:
        soup = get_response(url)
        # print(f'responded {page}')
    except Exception as E:
        print(f'[Error] While parsing the {link}\n{E}')
        return True
    # print(f'responded2{page}')

    items = soup.find_all('div', attrs={'data-marker': 'item'})
    # print(items)

    for item in items:
        sale_id = item['id']

        try:
            description = item.find('meta', attrs={'itemprop': 'description'})
            description = description['content'].replace('\n', '').replace('\xa0', '')
            # print(description)
        except:
            description = 'No description'

        try:
            link_post = item.find('a', attrs={'itemprop': 'url'})
            link_post = f'https://avito.ru{link_post["href"]}'
        except:
            link_post = 'No link'

        try:
            link_img = item.find('img', attrs={'itemprop': 'image'})
            link_img = link_img['src']
        except:
            try:
                link_img = item.find('li', attrs={'class': 'photo-slider-list-item-h3A51'})
                link_img = link_img['data-marker'].replace('slider-image/image-', '')
            except:
                link_img = 'No img'

        try:
            title = item.find('h3', attrs={'itemprop': 'name'})
            title = title.text.split(',')
            year = int(title[1])

            mark_info = title[0].split(' ')[0]
            if mark_info in marks:
                mark_info_ru = marks[mark_info]
            else:
                mark_info_ru = translit.detranslify(mark_info)
            model_info = re.sub(r'\w+\ ', '', title[0])
            model_info_ru = translit.detranslify(model_info)
        except:
            title = 'No title'
        # print(title)
        try:
            price = item.find('meta', attrs={'itemprop': 'price'})
            price = price['content']
        except:
            price = 0

        try:
            tech = item.find('div', attrs={'data-marker': 'item-specific-params'})
            tech = tech.text.replace('\xa0', ' ')
            try:
                tech_list = tech.split(',')
                if 'км' in tech_list[0]:
                    mileage = int(tech_list[0].replace('км', '').replace(' ',''))
                    tech = tech.split('км, ')[1]#re.sub(r'\w+\, ', '', tech)
                elif 'км' in tech_list[1]:
                    mileage = int(tech_list[1].replace('км', '').replace(' ', ''))
                    tech = tech.split(',')
                    tech.pop(1)
                    tech = (', ').join(part for part in tech)
                else:
                    mileage = 0
            except:
                mileage = 0
        except:
            tech = 'No tech'

        try:
            region = item.find('span', attrs={'class': 'geo-address-fhHd0 text-text-LurtD text-size-s-BxGpL'})
            region = region.text
        except:
            region = 'No region'

        search_string = f'{mark_info} {mark_info_ru} {model_info} {model_info_ru} {region} {str(year)}'
        # print(search_string)
        if sale_id in current_posts:
            continue

        temp = Parsed_post(sale_id=sale_id,
                           mark_info=mark_info,
                           mark_info_ru=mark_info_ru,
                           model_info=model_info,
                           model_info_ru=model_info_ru,
                           year=year,
                           price_rub=price,
                           mileage=mileage,
                           tech_human_name=tech,
                           region=region,
                           description=description,
                           link_post=link_post,
                           link_img=link_img,
                           search_string=search_string)
        # print(temp)
        result = add_row('avito', temp)

    return True

def get_marks():
    url = 'https://www.avito.ru/rossiya/avtomobili?p=1'
    response = session.request(method='GET', url=url, headers=headers)
    # with open('avito_parse_test.html', 'w+', encoding='UTF-8') as file:
    #     file.write(response.text)

    soup = BeautifulSoup(response.text, features="html.parser")
    links = []

    for item in soup.find_all('div', 'popular-rubricator-row-xX6S9'):
        temp = item.find('a')
        links.append(temp['href'])

    for link in links:
        # if links.index(link) in [0,1,2]:
        #     continue

        pages = find_pages(link)
        for page in range(pages):
            get_data(link, page+1)
            if page == 35:
                break
            print(f'link avito.ru{link}&p={page+1} comleted')

    return True

current_posts = db.handle_all('avito', 'sale_id')

def main():

    # asyncio.run(gather_links())
    if get_marks():
        print('Successful parsing')
    db.delete_dupes(table='avito', column='sale_id')
    db.reindex()

if __name__ == '__main__':
    main()
