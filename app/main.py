import os
import logging

from typing import Any, Dict, Tuple
from dotenv import load_dotenv
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Updater,
    filters,
)

# Based on https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
SELECT_SOURCE, SELECT_SHORT = range(2)
SUMMARY, ONE_SENTENCE, THESES = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('started')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Это ИИ для краткого изложения текстов. Введите ссылку на текст или прикрепите документ")
    return SELECT_SOURCE

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('pdf')
    return SELECT_SHORT

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('link')
    buttons = [
        [
            InlineKeyboardButton(text="Краткое описание", callback_data=str(SUMMARY)),
            InlineKeyboardButton(text="Одним предложением", callback_data=str(ONE_SENTENCE)),
            InlineKeyboardButton(text="Тезисы", callback_data=str(THESES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Это ссылка. Выберите опцию:", reply_markup=reply_markup)

    return SELECT_SHORT
 
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info('summary')
    pass

async def one_sentence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info('one_sentence')
    pass

async def theses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info('theses')
    pass

def main():
    logger.info("Init App...")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={ # словарь состояний разговора, возвращаемых callback функциями
            SELECT_SOURCE: [
                MessageHandler(filters.Document.PDF, handle_document),
                MessageHandler(filters.Regex('^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$'), handle_link),
            ],
            SELECT_SHORT: [
                CallbackQueryHandler(summary,       pattern='^' + str(SUMMARY) + '$'),
                CallbackQueryHandler(one_sentence,  pattern='^' + str(ONE_SENTENCE) + '$'),
                CallbackQueryHandler(theses,        pattern='^' + str(THESES) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
