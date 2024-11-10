import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext import ApplicationBuilder, CommandHandler

from parsing.WebParser import process_auction_page
from analyzer import checker

BOT_TOKEN = "7567933002:AAFhchpry5MWvlAmqQbR5Tm-YrfO4MtXThQ"
BOT_MENU = "Выберете параметры для проверки котировочной сессии на корректность:\n     1. Проверка наименования закупки \n     2. Проверка Обеспечения исполнения контракта\n     3. Проверка Наличие сертификатов/лицензий\n     4. Проверка Графика поставки и Этапов поставки\n     5. Проверка Максимального и Начального значения цены контракта\n     6. Проверка Характеристики спецификации закупки\n"

AWAIT_URL = 1
AWAIT_OPTION = 2

OPTIONS = ["Все", "1", "2", "3", "4", "5", "6", "Начать"]

URL_PATTERN = re.compile(r'^(http|https)://')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите URL сессии:")
    return AWAIT_URL


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text
    if not URL_PATTERN.match(url):
        await update.message.reply_text("Ошибка в формате URL:")
        return AWAIT_URL

    context.user_data["url"] = url
    context.user_data["selected_options"] = []

    reply_markup = ReplyKeyboardMarkup([OPTIONS], one_time_keyboard=True)
    await update.message.reply_text(BOT_MENU, reply_markup=reply_markup)
    await update.message.reply_text("Выберите параметры, нажмите Начать чтобы продолжить:",
                                    reply_markup=reply_markup)
    auction_id = context.user_data.get("url").split("/")[-1]
    await process_auction_page(auction_id)
    return AWAIT_OPTION


async def receive_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    option = update.message.text

    if option == "Начать":
        selected_options = context.user_data.get("selected_options", [])
        if not selected_options:
            await update.message.reply_text("Не выбраны параметры.")
            return AWAIT_OPTION

        url = context.user_data.get("url")
        await update.message.reply_text(f"Вы выбрали параметры {selected_options} для URL: {url}")
        await analyze_ulr(update= update, context=context)
        await update.message.reply_text("Введите новый URL:")
        return AWAIT_URL

    elif option == "Все":
        selected_options = ["1", "2", "3", "4", "5", "6"]
        url = context.user_data.get("url")
        context.user_data["selected_options"] = [True, True, True, True, True ,True]
        await update.message.reply_text(f"Вы выбрали параметры {selected_options} для URL: {url}")
        await analyze_ulr(update, context)
        await update.message.reply_text("Введите новый URL:")
        return AWAIT_URL

    elif option in OPTIONS[:-1]:
        context.user_data["selected_options"].append(option)
        await update.message.reply_text(
            f"Параметр '{option}' добавлен. Выберите еще или нажмите 'Начать' для продолжения.")
        return AWAIT_OPTION

    else:
        reply_markup = ReplyKeyboardMarkup([OPTIONS], one_time_keyboard=True)
        await update.message.reply_text(BOT_MENU, reply_markup=reply_markup)
        await update.message.reply_text("Выберете параметры, нажмите 'Начать' чтобы продолжить:",
                                        reply_markup=reply_markup)
        return AWAIT_OPTION


async def analyze_ulr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auction_id = context.user_data.get("url").split("/")[-1]
    result = checker(auction_id, [False, False, False, [True, []], False, False])
    selected = context.user_data.get("selected_options")
    print(f'selected = {selected}')
    # result = await scan_files(auction_id, context.user_data.get("selected_options"))
    # for index in result:
    #     await update.message.reply_text(f"Требование {index + 1} выполнено")
    if selected[0]:
        if result[0]:
            await sendMessage("Условие 1 выполнено, названия закупок совпадают", update)
        else:
            await sendMessage("Условие 1 не выполнено, названия закупок не совпадают", update)

    if selected[1]:
        if result[1]:
            await sendMessage("Условие 2 выполнено, Обеспечение исполнения контракта имеется", update)
        else:
            await sendMessage("Условие 2 не выполнено, в документах нет обеспечение исполнения контракта", update)

    if selected[2]:
        if result[2]:
            await sendMessage("Условие 3 выполнено, наличие сертификатов/лицензий соответствует документам", update)
        else:
            await sendMessage("Условие 3 не выполнено,  наличие сертификатов/лицензий соответствует документам", update)

# sel[3][1] = text
    if selected[3]:
        if result[3][0]:
            await sendMessage("Условие 4 выполнено, график поставок совпадает", update)
        else:
            await sendMessage(f"Условие 4 не выполнено, {selected[3][1]}", update)

    if selected[4]:
        if result[4]:
            await sendMessage("Условие 5 выполнено, начальная и максимальная цены соответствуют", update)
        else:
            await sendMessage("Условие 5 не выполнено, начальная и максимальная цены соответствуют", update)

    # if selected[5]:
    #     if result[5]:
    #         await sendMessage("Условие 1 выполнено, названия закупок совпадают", update)
    #     else:
    #         await sendMessage("Условие 1 не выполнено, названия закупок не совпадают", update)


async def sendMessage(text: str, update: Update):
    await update.message.reply_text(text)



def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AWAIT_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url)],
            AWAIT_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_option)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
