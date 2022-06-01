import requests
from bs4 import BeautifulSoup
from datetime import datetime
import lxml

import sys
import time
from random import randrange

import json

import asyncio
import aiohttp

import fake_useragent
from fake_useragent import UserAgent

ua = UserAgent()
ua = ua.random


# headers = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
# }


# url = 'https://uk.trustpilot.com/categories/pet_store'

# with requests.Session() as session:
#     # s = requests.Session()
#     response = session.get(url=url, headers=headers)
#
# # запись СПАРСЕНОЙ инфы в ХТМЛ-файл
# with open('index.html', 'w', encoding='utf-8') as file:
#     file.write(response.text)

# поиск ЗНАЧЕНИЯ последней страницы ПАГИНАЦИИ

# soup = BeautifulSoup(response.text, 'lxml')




async def get_page_data(session, page):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": f'{ua}'  # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
                               # like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }


    url = f'https://uk.trustpilot.com/categories/pet_store?page={page}'

    print(f"start...")

    async with session.get(url=url, headers=headers) as response:

        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        lot_items = soup.find('div', class_='box_content').find_all('div', class_='post')

        #print(lot_items)

        for lot in lot_items:
            lot_data = lot.find_all('div')

            # !!! "lot_data[3]" на чинается с: "<div' class='title_holder>"
            lot_title = lot_data[3].find('a').text.strip()
            lot_href = lot_data[3].find('a').get('href')
            lot_user = lot_data[3].find('p', class_='mypostedon').find('a').text.strip()#get('href')
            #
            lot_price = lot_data[5].find('p').text.strip()
            lot_price = re.sub("\s\s+", " ", lot_price)

            # время через которое ИСТЕКАЕТ аукцион, лежит в теге:
            # !!! <p class="expiration_auction_p">10073</p>
            # ...это Юникс формат!!!
            lot_exp_sec = lot_data[5].find('p', class_='expiration_auction_p').text.strip()
            #lot_exp = datetime.fromtimestamp(int(lot_exp_sec))# - 3*60*60).strftime('%d %H:%M')
            lot_exp_sec = int(lot_exp_sec)

            # привожу ТЕКУЩЕЕ время к виду: 1639059381 (Юникс формат)
            time_now = DT.datetime.now()
            time_now_sec = int(time.mktime(time_now.timetuple()))

            #d_t = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            #d_t_now = datetime.strptime(d_t, '%d-%m-%Y %H:%M:%S')

            # суммарное кол-во секунд(время окончания):
            time_exp_sec = lot_exp_sec + time_now_sec

            # ДАТА и ВРЕМЯ завершения аукциона:
            time_exp = datetime.fromtimestamp(time_exp_sec)

            #print(lot_href)
            #print(time_exp)


            #break

            lots_data.append(
                {
                    "lot_title": lot_title,
                    "lot_href": lot_href
                }
            )
        print(f"Обработал страницу {page}")


async def gather_data():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": f'{ua}'
        # "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        # Chrome/96.0.4664.45 Safari/537.36"
    }

    url = 'https://uk.trustpilot.com/categories/pet_store'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)

        # поиск ЗНАЧЕНИЯ последней страницы ПАГИНАЦИИ
        soup = BeautifulSoup(await response.text(), 'lxml')

        # Пагинация заключена в теге: <span class='pages'>Страница 1 из 5</span>
        # Мне нужно достать "5".
        page_count = int(soup.find('a', {'name': 'pagination-button-last'}).text)#[-1])

        print(f'PAG.: {page_count}')

        tasks = []

        # for page in range(1, page_count + 1):
        for page in range(1, 2):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)
    print('777')


def main():
    asyncio.run(gather_data())
    finish_time = time.time() - start_time
    print(f"TIME: {finish_time}")
    cur_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    print(f"TIME_now: {cur_time}")


if __name__ == "__main__":
    # print(sys.version_info[0])
    # ЗАПЛАТКА!!! Блок выпадания ОШИБКИ под виндой...
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # asyncio.run(main())
    main()
