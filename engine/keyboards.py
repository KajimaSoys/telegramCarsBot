#Импорт утилит для работы с виртуальной клавиатурой
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


inline_find_btn = InlineKeyboardButton('Поиск 🔎', callback_data='find')
inline_offer_btn = InlineKeyboardButton('Отправить заявку 📝', callback_data='offer')
inline_compare_btn = InlineKeyboardButton('Сравнить авто с другими 📈', callback_data='compare')
inline_help_btn = InlineKeyboardButton('Помогите! 👋', callback_data='help')

inline_home_btn = InlineKeyboardButton('Домой!', callback_data='start')
# inline_home_btn_from_help = InlineKeyboardMarkup('Мне это не помогло, но спасибо!', callback_data='start')


# button_hi = KeyboardButton('Привет...')
# button_help = KeyboardButton('Помогите! 👋')

greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_find_btn).add(inline_compare_btn).add(inline_offer_btn).add(inline_help_btn)
find_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_home_btn).add(inline_help_btn)
offer_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_home_btn).add(inline_help_btn)
help_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_home_btn)
# greet_kb.add(button_hi)
# greet_kb.add(button_help)