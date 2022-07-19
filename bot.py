import logging.config
import os

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Filters, MessageHandler, Updater)

from cms import (add_product_to_cart, get_access_token, get_cart_items,
                 get_product_detail, get_products, get_total_cost_cart,
                 remove_product_from_cart)
from log_config import LOGGING_CONFIG, TelegramLogsHandler

logger = logging.getLogger(__file__)


_database = None


def start(context: CallbackContext, update: Update):
    access_token = context.bot_data.get('access_token')
    products = get_products(access_token)
    keyboard = [
        [InlineKeyboardButton(name, callback_data=product_id)]
        for product_id, name in products.items()
    ]
    keyboard.append([InlineKeyboardButton('🛒 Cart', callback_data='cart')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Choose your fish',
        reply_markup=reply_markup
    )
    return 'HANDLE_MENU'


def handle_menu(context: CallbackContext, update: Update):
    access_token = context.bot_data.get('access_token')
    query = update.callback_query
    if query.data == 'cart':
        show_cart(context, update)
        return 'HANDLE_CART'
    elif query.data == 'menu':
        start(context, update)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id
        )
        return 'HANDLE_MENU'
    product_id = query.data
    context.user_data['product_id'] = product_id
    name, price, description, weight, img_link = get_product_detail(
        access_token, product_id)
    context.user_data['name'] = name
    text = f'{name}\n\n{price} per kg\n{weight} on stock\n\n{description}'
    keyboard = [
        [
            InlineKeyboardButton('1 kg', callback_data='1'),
            InlineKeyboardButton('5 kg', callback_data='5'),
            InlineKeyboardButton('10 kg', callback_data='10')
        ],
        [
            InlineKeyboardButton('Back', callback_data='menu'),
            InlineKeyboardButton('🛒 Cart', callback_data='cart')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=img_link,
        caption=text,
        reply_markup=reply_markup
    )
    return 'HANDLE_DESCRIPTION'


def handle_description(context: CallbackContext, update: Update):
    query = update.callback_query
    if query.data == 'menu':
        start(context, update)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id
        )
        return 'HANDLE_MENU'
    elif query.data == 'cart':
        show_cart(context, update)
        return 'HANDLE_CART'
    else:
        access_token = context.bot_data.get('access_token')
        user_id = query.from_user.id
        product_id = context.user_data.get('product_id')
        name = context.user_data.get('name')
        quantity = int(query.data)
        add_product_to_cart(access_token, user_id, product_id, quantity)
        keyboard = [
            [
                InlineKeyboardButton('🐟 Menu', callback_data='menu'),
                InlineKeyboardButton('🛒 Cart', callback_data='cart')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{quantity} kg {name} added to cart',
            reply_markup=reply_markup
        )
        return 'HANDLE_DESCRIPTION'


def show_cart(context: CallbackContext, update: Update):
    access_token = context.bot_data.get('access_token')
    query = update.callback_query
    user_id = query.from_user.id
    text = 'Your cart:\n\n'
    keyboard = []
    for product in get_cart_items(access_token, user_id):
        text += (
            f"{product.get('name')}\n"
            f"{product.get('price')} per kg\n"
            f"{product.get('quantity')}kg in cart "
            f"for {product.get('cost')}\n\n"
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Remove {product.get('name')}",
                    callback_data=product.get('product_id')
                )
            ]
        )
    keyboard.append([InlineKeyboardButton('🐟 Menu', callback_data='menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    cost = get_total_cost_cart(access_token, user_id)
    text += f'Total: {cost}'
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    return 'HANDLE_CART'


def handle_cart(context: CallbackContext, update: Update):
    query = update.callback_query
    if query.data == 'menu':
        start(context, update)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id
        )
        return 'HANDLE_MENU'
    else:
        access_token = context.bot_data.get('access_token')
        user_id = query.from_user.id
        product_id = query.data
        remove_product_from_cart(access_token, user_id, product_id)
        keyboard = [
            [
                InlineKeyboardButton('🐟 Menu', callback_data='menu'),
                InlineKeyboardButton('🛒 Cart', callback_data='cart')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Fish removed from cart',
            reply_markup=reply_markup
        )
        return 'HANDLE_MENU'


def handle_users_reply(update: Update, context: CallbackContext):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(context, update)
        db.set(chat_id, next_state)
    except Exception as err:
        logger.exception(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('DATABASE_PASSWORD')
        database_host = os.getenv('DATABASE_HOST')
        database_port = os.getenv('DATABASE_PORT')
        _database = redis.Redis(
            host=database_host,
            port=database_port,
            password=database_password
        )
    return _database


def main():
    load_dotenv()
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')
    cms_client_id = os.getenv('MOLTIN_CLIENT_ID')
    cms_client_secret = os.getenv('MOLTIN_CLIENT_SECRET')
    access_token = get_access_token(cms_client_id, cms_client_secret)

    logging.config.dictConfig(LOGGING_CONFIG)
    logger.addHandler(TelegramLogsHandler(telegram_token, chat_id))

    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['access_token'] = access_token

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    logger.info('The Telegram Bot is running')
    updater.start_polling()


if __name__ == '__main__':
    main()
