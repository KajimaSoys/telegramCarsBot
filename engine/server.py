import logging

#Импорт самого бота
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

#Импорт утилит для работы с текстом
import keyboards as kb

import ast
import db
import variables
from server_utils import States
from messages import MESSAGES
from utils import fetch_results, get_text, get_img
from statistics import mean


logging.basicConfig(level=logging.DEBUG)
API_TOKEN = variables.api_token

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(state='*', commands=['start'])
async def send_welcome(message: types.Message):
    users = db.handle_all('users', 'id')
    if not message.from_user.id in users:
        db.insert('users', {'id': message.from_user.id, 'username': message.from_user.username, 'is_admin': False,
                            'is_manager': False, 'wait_confirm': False})
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.START_STATE[0])
    await message.reply(MESSAGES['start'], reply=False, reply_markup=kb.greet_kb)

@dp.callback_query_handler(lambda c: c.data == 'start', state=States.all())
async def process_callback_start(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    await state.set_state(States.START_STATE[0])
    await call.message.answer(MESSAGES['start'], reply_markup=kb.greet_kb)
    await call.answer()


@dp.message_handler(state='*', commands=['accept'])
async def authorization_accept(message: types.Message):
    admins = db.handle_staff('users', 'is_admin')
    admin_list = []
    for admin in admins:
        admin_list.append(admin[0])
    if message.from_user.id in admin_list:
        argument = int(message.get_args())
        staff = db.handle_staff('users', 'wait_confirm')
        waiting_staff = []
        for user in staff:
            waiting_staff.append(user[0])
        if argument in waiting_staff:
            db.update_status('users', int(argument), 'True')
            db.update_confirm('users', 'id', int(argument), 'False')
            await message.reply('Теперь у пользователя есть права менеджера!', reply=False)
            await bot.send_message(argument, 'Поздравляю, Ваша заявка одобрена!')
        else:
            await message.reply('Неверный идентификатор', reply=False)
    else:
        await message.reply('У вас недостаточно прав!', reply=False)

@dp.message_handler(state='*', commands=['decline'])
async def authorization_decline(message: types.Message):
    admins = db.handle_staff('users', 'is_admin')
    admin_list = []
    for admin in admins:
        admin_list.append(admin[0])
    if message.from_user.id in admin_list:
        argument = int(message.get_args())
        staff = db.handle_staff('users', 'wait_confirm')
        waiting_staff = []
        for user in staff:
            waiting_staff.append(user[0])
        if argument in waiting_staff:
            db.update_status('users', int(argument), 'false')
            db.update_confirm('users', 'id', int(argument), 'false')
            await message.reply('Успешно отклонено!', reply=False)
            await bot.send_message(argument, 'К сожалению, Вашу заявку отклонили')
        else:
            await message.reply('Неверный идентификатор', reply=False)
    else:
        await message.reply('У вас недостаточно прав!', reply=False)

@dp.message_handler(state='*', commands=['register'])
async def user_register(message: types.Message):
    argument = message.get_args()
    if argument == variables.register:
        admins = db.handle_staff('users', 'is_admin')
        for admin in admins:
            print(admin)
            text = f'Поступила заявка на авторизацию в системе от пользователя\n' \
                   f'@{message.from_user.username}\n{message.from_user.id}!\n' \
                   f'Введите /accept {message.from_user.id} чтобы принять.\n' \
                   f'Введите /decline {message.from_user.id} чтобы отклонить.'
            await bot.send_message(admin[0], text)
        db.update_confirm('users', 'id', message.from_user.id, 'True')
        await message.reply('Ваша заявка будет рассмотрена в ближайшее время!', reply=False)
    else:
        await message.reply('Введен неверный код', reply=False)


@dp.message_handler(state=States.START_STATE, commands=['offer']) #, commands=['help']
async def send_offer(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.OFFER_STATE[0])

    text = MESSAGES['offer']
    await message.reply(text, reply=False, reply_markup=kb.offer_kb)

@dp.callback_query_handler(lambda c: c.data == 'offer', state=States.START_STATE)
async def process_callback_offer(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    await state.set_state(States.OFFER_STATE[0])
    await call.message.answer(MESSAGES['offer'], reply_markup=kb.offer_kb)
    await call.answer()

@dp.message_handler(state=States.OFFER_STATE, content_types=['photo', 'text'])
async def capture_offer(message: types.Message):
    managers = db.handle_staff('users', 'is_manager')
    for manager in managers:
        if message.photo:
            await bot.send_photo(manager[0], message.photo[0]['file_id'], caption=f'Поступила заявка от пользователя @{message.from_user.username}!\n{message.caption}')
        else:
            await bot.send_message(manager[0], f'Поступила заявка от пользователя @{message.from_user.username}!\n{message.text}')
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.START_STATE[0])
    await message.reply('Спасибо за заявку! С Вами свяжется специалист.', reply=False, reply_markup=kb.greet_kb)


@dp.message_handler(state=States.START_STATE, commands=['compare']) #, commands=['help']
async def send_compare(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.COMPARE_STATE[0])

    text = MESSAGES['compare']
    await message.reply(text, reply=False, reply_markup=kb.find_kb)

@dp.callback_query_handler(lambda c: c.data == 'compare', state=States.START_STATE)
async def process_callback_compare(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    await state.set_state(States.COMPARE_STATE[0])
    await call.message.answer(MESSAGES['compare'], reply_markup=kb.find_kb)
    await call.answer()

@dp.message_handler(state=States.COMPARE_STATE)
async def capture_compare(message: types.Message):
    results, count, count_message = fetch_results(message.text)
    if count == 0:
        await message.reply('По Вашему запросу ничего не найдено, попробуйте изменить запрос', reply=False, reply_markup=kb.find_kb)
    else:
        prices = []
        for result in results:
            prices.append(result['price_rub'])
        min_price = min(prices)
        max_price = max(prices)
        mean_price = mean(prices)
        text = f'Минимальная цена: {min_price} руб.\n' \
               f'Максимальаня цена: {max_price} руб.\n' \
               f'Средняя цена: {mean_price} руб.'
        await message.reply(text, reply=False, reply_markup=kb.find_kb)


@dp.message_handler(state=States.START_STATE, commands=['find']) #, commands=['help']
async def send_find(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.FIND_STATE[0])

    text = MESSAGES['find']
    await message.reply(text, reply=False, reply_markup=kb.find_kb)

@dp.callback_query_handler(lambda c: c.data == 'find', state=States.START_STATE)
async def process_callback_find(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    await state.set_state(States.FIND_STATE[0])
    await call.message.answer(MESSAGES['find'], reply_markup=kb.find_kb)
    await call.answer()

@dp.message_handler(state=States.FIND_STATE)
async def capture_find(message: types.Message):
    results, count, count_message = fetch_results(message.text)
    await message.reply(count_message, reply=False)

    if count == 0:
        await message.reply('Ищем еще?', reply=False, reply_markup=kb.find_kb)
    else:
        posts = []
        posts_part = []
        for item in results:
            temp_dict = {}
            temp_dict['display_name'] = get_text(item)
            temp_dict['image_url'] = get_img(item)
            if (results.index(item) + 1) % 10 == 0:
                posts_part.append(temp_dict)
                posts.append(posts_part)
                posts_part = []
            else:
                posts_part.append(temp_dict)
        posts.append(posts_part)
        if len(posts[-1]) == 0:
            posts.pop(-1)

        post_data = posts[0]

        db.delete_row('requests', 'user_id', str(message.from_user.id))
        db.insert('requests', {
            'user_id': str(message.from_user.id),
            'request': str(posts)
        })

        post_keyboard = kb.get_posts_keyboard(0, len(posts))

        post_data_len = len(post_data)-1
        for index, post in enumerate(post_data):
            if index == post_data_len:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=post.get("image_url"),
                    caption=post.get("display_name"),
                    reply_markup=post_keyboard
                )
            else:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=post.get("image_url"),
                    caption=post.get("display_name"),
                )


@dp.callback_query_handler(kb.posts_callback.filter(), state='*')
async def post_page_handler(query: types.CallbackQuery, callback_data: dict):
    page = int(callback_data.get("page"))

    posts = ast.literal_eval(db.select_request(str(query.from_user.id)))

    post_data = posts[page]
    keyboard = kb.get_posts_keyboard(page, len(posts))

    post_data_len = len(post_data) - 1
    for index, post in enumerate(post_data):
        if index == post_data_len:
            await bot.send_photo(
                chat_id=query.message.chat.id,
                photo=post.get("image_url"),
                caption=post.get("display_name"),
                reply_markup=keyboard
            )
        else:
            await bot.send_photo(
                chat_id=query.message.chat.id,
                photo=post.get("image_url"),
                caption=post.get("display_name"),
            )


@dp.message_handler(state=States.all(), commands=['help'])
async def send_help(message: types.Message):
    text = MESSAGES['help'].format(
        current_state=await dp.current_state(user=message.from_user.id).get_state(),
        states=States.all()
    )
    await message.reply(text, reply=False, reply_markup=kb.help_kb)

@dp.callback_query_handler(lambda c: c.data == 'help', state=States.all())
async def process_callback_help(call: types.CallbackQuery):
    text = MESSAGES['help'].format(
        current_state=await dp.current_state(user=call.from_user.id).get_state(),
        states=States.all()
    )
    await call.message.answer(text, reply_markup=kb.help_kb)
    await call.answer()


@dp.message_handler(state=States.START_STATE)
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)