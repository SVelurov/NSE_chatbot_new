#  Bot: NSE_bot
#  User: NSE_KIVI_bot
#  https://habr.com/ru/articles/700484/

#  Bot: NSE_test
#  User: NSE_fortest_bot

from aiogram import Bot, Dispatcher, types
import pandas as pd
from nse_update import login_et


async def mk_bot(token):
    bot = Bot(token)
    dp = Dispatcher(bot)

    # # Authenticate and copy NSE data file from GoogleDrive
    # login_et()

    @dp.message_handler(commands=["start"])
    async def start_message(message: types.Message):

        await bot.send_message(message.chat.id,
                               text='Бот проверяет статус акта НРП на телевизоры KIVI и JVC')
        await bot.send_message(message.chat.id,
                               text='Введите серийный номер телевизора в формате KIVI*** или JVC***'
                                    'или номер акта НРП в формате NSE***')

    @dp.message_handler(content_types=["text"])
    async def dialog(message: types.Message):
        try:
            process_message = await bot.send_message(message.chat.id, '_Проверяю..._', parse_mode='Markdown')

            response, status = search_excel(message.text)
            if status == 0:
                btn = types.InlineKeyboardButton("👎", callback_data=f"dislike{process_message.message_id}")
            else:
                btn = types.InlineKeyboardButton("👍", callback_data=f"like{process_message.message_id}")

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(btn)

            # Generate and send response
            await bot.edit_message_text(response, message.chat.id, process_message.message_id, reply_markup=markup)

        except Exception:
            await bot.edit_message_text("Внутренняя ошибка бота!", process_message.message_id, message.chat.id)

    # Function to search for the corresponding value in the Excel file
    def search_excel(search_string):
        df = pd.read_excel('NSE.xlsx')
        # The search string is in the first column and the corresponding values are in the second column
        if search_string[:3] == 'JVC' or search_string[:4] == 'KIVI':
            try:
                result = df[df.iloc[:, 0] == search_string].iloc[0, 1]
                nse_num = df[df.iloc[:, 0] == search_string].iloc[0, 2]
                if result == 'Утвержден ECS':
                    output = f'Акт НРП {nse_num} подтвержден'
                    status = 1
                else:
                    output = f'Акт НРП {nse_num} не подтвержден. Свяжитесь с офисом Киви'
                    status = 0
            except IndexError:
                output = f'Такой серийный номер не найден. Убедитесь, что номер введен правильно, в формате KIVI*** ' \
                         f'или JVC***. Если номер верный, то свяжитесь с офисом Киви'
                status = 0
        # The search string is in the third column and the corresponding values are in the second column
        elif search_string[:3] == 'NSE':
            try:
                result = df[df.iloc[:, 2] == search_string].iloc[0, 1]
                if result == 'Утвержден ECS':
                    output = f'Акт НРП {search_string} подтвержден'
                    status = 1
                else:
                    output = f'Акт НРП {search_string} не подтвержден. Свяжитесь с офисом Киви'
                    status = 0
            except IndexError:
                output = f'Такой номер акта не найден. Убедитесь, что номер введен правильно, в формате NSE***. ' \
                         f'Если номер верный, то свяжитесь с офисом Киви'
                status = 0

        else:
            output = f'Это вообще не номер. Введите номер правильно, в формате KIVI*** или JVC*** или NSE***'
            status = 0
        return output, status

    return bot, dp
