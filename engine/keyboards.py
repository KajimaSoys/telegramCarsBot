#Импорт утилит для работы с виртуальной клавиатурой
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
import db

inline_find_btn = InlineKeyboardButton('Поиск 🔎', callback_data='find')
inline_offer_btn = InlineKeyboardButton('Отправить заявку 📝', callback_data='offer')
inline_compare_btn = InlineKeyboardButton('Сравнить авто с другими 📈', callback_data='compare')
inline_help_btn = InlineKeyboardButton('Помогите! 👋', callback_data='help')
inline_home_btn = InlineKeyboardButton('Домой!', callback_data='start')
inline_stat_btn = InlineKeyboardButton('Статистика 📊', callback_data='stat')

def is_admin(user_id):
    admins = db.handle_staff('users', 'is_admin')
    admin_list = []
    for admin in admins:
        admin_list.append(admin[0])
    if user_id in admin_list:
        return True
    else:
        return False

def greet_kb(user_id):
    if is_admin(user_id):
        return InlineKeyboardMarkup(resize_keyboard=True).add(inline_find_btn).add(inline_compare_btn).add(inline_offer_btn).add(inline_stat_btn).add(inline_help_btn)
    else:
        return InlineKeyboardMarkup(resize_keyboard=True).add(inline_find_btn).add(inline_compare_btn).add(inline_offer_btn).add(inline_help_btn)

find_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_home_btn).add(inline_help_btn)
offer_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_home_btn).add(inline_help_btn)
help_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_home_btn)


posts_callback = CallbackData("Posts", "page")

def get_posts_keyboard(page: int, count: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    has_next_page = count > page + 1

    if page !=0:
        keyboard.add(
            InlineKeyboardButton(
                text="< Назад",
                callback_data=posts_callback.new(page=page - 1)
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=f"• {page + 1} •",
            callback_data="dont_click_me"
        )
    )

    if has_next_page:
        keyboard.add(
            InlineKeyboardButton(
                text="Вперёд >",
                callback_data=posts_callback.new(page=page + 1)
            )
        )

    keyboard.add(inline_home_btn)
    return keyboard