import os
import logging

from typing import Any, Dict, Tuple
from dotenv import load_dotenv
from telegram import ( 
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
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

from text_analizer import get_summary, get_one_sentence, get_theses
from parser.url_parser import parse_url_to_file
from parser.doc_parser import parse_document_to_file


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
    print(id(logger))
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Это ИИ для краткого изложения текстов. Введите ссылку на текст или прикрепите документ")
    return SELECT_SOURCE

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    
    logger.info('document')
    user = update.message.from_user
    file_info = await context.bot.get_file(update.message.document.file_id)
    logger.info(file_info)
    filename = f'./storage/{update.message.document.file_name}'
    context.user_data["current_doc"] = filename
    logger.info(filename)
    await file_info.download_to_drive(filename)
    result = parse_document_to_file(filename, user['id'])

    if not result:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Извините, не получилось распознать документ.')
        return SELECT_SOURCE
    
    buttons = [
        [
            InlineKeyboardButton(text="Краткое описание", callback_data=str(SUMMARY)),
            InlineKeyboardButton(text="Одним предложением", callback_data=str(ONE_SENTENCE)),
            InlineKeyboardButton(text="Тезисы", callback_data=str(THESES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)
    return SELECT_SHORT


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('url')
    user = update.message.from_user
    url = update.message.text
    result = parse_url_to_file(url, user['id'])

    if not result:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Извините, не удалось прочитать ссылку {url}. Попробуйте, пожалуйста, другую')
        return SELECT_SOURCE
    
    buttons = [
        [
            InlineKeyboardButton(text="Краткое описание", callback_data=str(SUMMARY)),
            InlineKeyboardButton(text="Одним предложением", callback_data=str(ONE_SENTENCE)),
            InlineKeyboardButton(text="Тезисы", callback_data=str(THESES)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

    return SELECT_SHORT
 
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('summary')
    user = update.callback_query.from_user
    answer = get_summary(user['id'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
    return SELECT_SOURCE

async def one_sentence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('one_sentence')
    user = update.callback_query.from_user
    answer = get_one_sentence(user['id'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
    return SELECT_SOURCE

async def theses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    logger.info('theses')
    user = update.callback_query.from_user
    answer = get_theses(user['id'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
    return SELECT_SOURCE

def main():
    if not os.path.exists("./storage"):
        os.makedirs("./storage")
    logger.info("Init App...")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={ # словарь состояний разговора, возвращаемых callback функциями
            SELECT_SOURCE: [
                MessageHandler(filters.Document.TEXT 
                               | filters.Document.DOC
                               | filters.Document.DOCX
                               | filters.Document.PDF, handle_document),
                MessageHandler(filters.Regex('^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$'), handle_url),
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
