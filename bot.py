import requests
from bs4 import BeautifulSoup

import aiogram
from aiogram import types, Dispatcher
import logging
import asyncio

def content(filen):
    '''
    Функция возвращающая содержимое текстового файла в директории по названию
    :param filen: название файла
    :return: тестовое содержание файла
    '''
    try:
        with open(f'{filen}.txt', 'r', encoding="utf8") as file:
            data = file.read()
            file.close()
        return (data)
    except:
        return None

def get_news(obj: str, kol: int):
    '''
    Парсер новостей с Habr, отправляет гет запрос и с помощью BS4 получаем необходимые данные
    :param obj: часть ссылки, принимает либо 'news' либо 'all' (новости либо статьи)
    :param kol: колличество записей необходимых вернуть
    :return: словарь, включающий в себя: ссылку, заголовок, дату, и текст новости
    '''
    try:
        url = f'https://habr.com/ru/{obj}/'
        headers= {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.43 (KHTML, like Gecko) "
                          "Chrome/107.0.0.0 Safari/537.36 OPR/92.0.4561.21"
        }

        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        news = soup.find_all(class_="tm-articles-list__item")
        result = []

        for new in news:
            if kol>0:
                date_time = new.find(class_='tm-article-snippet__datetime-published').text
                first_string = new.find(class_='tm-article-snippet__title-link')
                adress = first_string.get("href").strip()
                tegs=[]
                snippet = new.find_all(class_="tm-article-snippet__hubs-item")
                for teg in snippet:
                    if teg.text.strip().split()[-1] == '*':
                        tegs.append(teg.text.strip()[:-2])
                    else:
                        tegs.append(teg.text.strip())
                main = new.find(class_="tm-article-body tm-article-snippet__lead")
                text = main.text.strip().split('\n')[0]
                print(date_time, '|', "https://habr.com" + adress, first_string.text.strip(), tegs, text)
                result.append({
                    'href': f"https://habr.com"+adress,
                    'header': first_string.text.strip(),
                    'date': date_time,
                    'tegs': tegs,
                    'text': text
                })
                kol -=1
        return result

    except:
        return []
async def bot():
    '''
    Тело бота
    '''
    bot = aiogram.Bot(token="5984477730:AAFol_qG8fVDk30yVAvWdMkqUsKiXSt2Qu4")
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['start', 'my'])
    async def start(message):
        '''
        Функция позволяющая выбрать тип информации - статьи или новости
        :param message: команда /start или /my
        :return: сообщение с выбором
        '''
        await bot.delete_message(message.chat.id, message.message_id)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        journal = types.InlineKeyboardButton('Статьи', callback_data='journ')
        news = types.InlineKeyboardButton('Новости', callback_data='new')
        keyboard.add(news, journal)
        await message.answer(content('start'), parse_mode='html', reply_markup=keyboard)

    @dp.callback_query_handler(lambda call: call.data in ['new', 'journ'])
    async def how_much(call):
        '''
        Выбор колличества статей
        :param call: new или journ - информация о том, что желает увидеть пользователь
        :return: статьи или новости
        '''
        if call.data == 'new':
            text = 'НОВОСТИ'
            obj = 'news'
        else:
            text = 'СТАТЬИ'
            obj = 'all'
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for i in ['1', '3', '5', '10', '15', '20']:
            if i == '1':
                end = 'ь'
            elif i == '3':
                end = 'и'
            else: end = 'ей'
            keyboard.add(types.InlineKeyboardButton(f'{i} запис{end}', callback_data=f'{obj} {i}'))

        await call.message.edit_text(f"<b>{text}</b>\nСколько последних записей ты хотел бы посмотреть?",
                                     parse_mode='html', reply_markup=keyboard)

    @dp.callback_query_handler(lambda call: call.data.split()[0] in ['news', 'all'])
    async def give_news(call):
        '''
        Функция отправляет все новости по заданным параметрам пользователем
        :param call: информация о параметрах формата "ТИП кол-во"
        :return: статьи
        '''
        print(call.data.split())
        news = get_news(call.data.split()[0], int(call.data.split()[1]))
        for new in news:
            tegs=''
            for i in new['tegs']:
                tegs = tegs + ' ' + i
            href = new['href']
            text=f"<i>{new['date']}</i>\n<b><a href='{href}'>{new['header']}</a></b>\n<i>{tegs}</i>\n\n{new['text']}"
            print(text)
            await bot.send_message(call.message.chat.id, text=text, parse_mode='html')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(bot())