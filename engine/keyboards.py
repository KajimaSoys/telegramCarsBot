#Импорт утилит для работы с виртуальной клавиатурой
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


inline_find_btn = InlineKeyboardButton('Поиск 🔎', callback_data='find')
inline_offer_btn = InlineKeyboardButton('Отправить заявку 📝', callback_data='offer')
inline_compare_btn = InlineKeyboardButton('Сравнить авто с другими 📈', callback_data='compare')
inline_help_btn = InlineKeyboardButton('Помогите! 👋', callback_data='help')
inline_home_btn = InlineKeyboardButton('Домой!', callback_data='start')


greet_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_find_btn).add(inline_compare_btn).add(inline_offer_btn).add(inline_help_btn)
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