import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext import ApplicationBuilder, CommandHandler

from analyzer import scan_files
from parsing.WebParser import process_auction_page

BOT_TOKEN = "7781043930:AAElBpRaGjjV6didS-WExBNTvfeTBdGE1jk"
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
    await update.message.reply_text("Выберете параметры, нажмите Начать чтобы продолжить:",
                                    reply_markup=reply_markup)
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
        await analyze_ulr(context)
        await update.message.reply_text("Введите новый URL:")
        return AWAIT_URL

    elif option == "Все":
        selected_options = ["1", "2", "3", "4", "5", "6"]
        url = context.user_data.get("url")
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
    print(auction_id)
    await process_auction_page(auction_id)
    result = await scan_files(auction_id, context.user_data.get("selected_options"))
    for index, res in result:
        if res:
            await update.message.reply_text(f"Требование {index + 1} выполнено")


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
