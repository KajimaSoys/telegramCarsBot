from server_utils import States

current_state_message = 'Текущее состояние - "{current_state}", что удовлетворяет условию "один из {states}"'
help_message = 'Нужна помощь?... Сейчас она всем нужна :)'
start_message = 'Скажите, что Вас интересует?'# + help_message
find_message = 'Опишите интересующую машину, а я найду тебе похожие'
offer_message = 'Введите данные о машине и себе в следующем виде\n' \
                '[ФИО] [Регион] [Номер телефона]\n' \
                '[Марка] [Модель] [Год производства]\n' \
                '[Пробег(км)] [Кол-во владельцев]\n' \
                '[Ваша цена]\n' \
                '[Свой комментарий]\n' \
                'Не забудьте прикрепить одну лучшую фотографию Вашей машины!'
searching_message = 'Так, нашел вот это.. То?'
compare_message = 'Введите данные о машине, я найду диапозон цен среди похожих машин\n' \
                  'Формат [Марка Модель Год] подойдет для поиска лучше всего'

MESSAGES = {
    'start': start_message,
    'help' : help_message,
    'current_state': current_state_message,
    'find': find_message,
    'searching': searching_message,
    'offer': offer_message,
    'compare': compare_message,
}

