from aiogram.utils.helper import Helper, HelperMode, ListItem

class States(Helper):
    mode = HelperMode.snake_case

    START_STATE = ListItem()
    FIND_STATE = ListItem()
    OFFER_STATE = ListItem()
    COMPARE_STATE = ListItem()

if __name__ == '__main__':
    print(States.all())