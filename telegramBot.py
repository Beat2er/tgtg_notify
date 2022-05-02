import datetime

from telegram.ext import Updater, dispatcher, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from telegram.ext import CommandHandler
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def truncate(str, max_len):
    return (str[:max_len] + '..') if len(str) > max_len else str


class telegramBot:
    chat_ids = None  # by reference
    bot = None
    stored_items = None  # by reference
    email = None
    """
    keyboard = [
            [InlineKeyboardButton("Info", callback_data='/info')],
            [
                InlineKeyboardButton("Stop", callback_data='/stop'),
                InlineKeyboardButton("Reset", callback_data='/reset'),
            ],
        ]
    """

    def __init__(self, token, chat_ids_list, stored_items, email):
        self.stored_items = stored_items
        self.chat_ids = chat_ids_list
        self.email = email
        updater = Updater(token=token, use_context=True)
        start_handler = MessageHandler(Filters.command, self.start)
        stop_handler = CommandHandler('stop', self.stop)
        reset_handler = CommandHandler('reset', self.reset)
        info_handler = CommandHandler('info', self.info)
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(info_handler)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(stop_handler)
        dispatcher.add_handler(reset_handler)
        dispatcher.add_handler(unknown_handler)
        self.bot = updater.bot
        updater.start_polling()

    def start(self, update: Update, context: CallbackContext):

        # reply_markup = InlineKeyboardMarkup(self.keyboard)

        if update.effective_chat.id in self.chat_ids[0]:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Already started.")  # , reply_markup=reply_markup)
            return

        # check password:
        words = update.message.text.split(" ")
        if len(words) < 2:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, please login with /start "
                                                                            "<password>!")
            return
        if len(words) >= 2:
            if words[1].lower() != self.email.lower():
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="incorrect password, please login with /start <password>!")
                return

        if update.effective_chat.id not in self.chat_ids[0]:
            self.chat_ids[0].append(update.effective_chat.id)

        context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")  # , reply_markup=reply_markup)

    def info(self, update: Update, context: CallbackContext):
        self.send_info_to_chat(self.stored_items[0], update.effective_chat.id, "Info:\n")

    def reset(self, update: Update, context: CallbackContext):
        self.stored_items[0] = dict()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Reset")

    def stop(self, update: Update, context: CallbackContext):
        try:
            self.chat_ids[0].remove(update.effective_chat.id)
        except:
            pass
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bye!")

    def unknown(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def send_info_items(self, stored_items):
        for chat_id in self.chat_ids[0]:
            self.send_info_to_chat(stored_items, chat_id)

    def send_info_to_chat(self, stored_items, chat_id, title="New items:\n"):
        message = title
        for i in stored_items:
            item = stored_items[i]
            item_data = {'name': item['item']['name'],
                         'description': item['item']['description'],
                         'price': str(item['item']['price_including_taxes']['minor_units'])[
                                  :-item['item']['price_including_taxes']['decimals']] + "," + str(
                             item['item']['price_including_taxes']['minor_units'])[-item['item'][
                             'price_including_taxes']['decimals']:] + " " + item['item']['price_including_taxes'][
                                      'code'],
                         'store': item['store']['store_name'],
                         'store_address': item['store']['store_location']['address']['address_line'],
                         'in_sales_window': item['in_sales_window'],
                         }
            try:
                item_data['time_end'] = datetime.datetime.strptime(item['purchase_end'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                    "%y.%m.%d, %H:%M:%S") + \
                                        " remaining: " + str(
                    datetime.datetime.strptime(item['purchase_end'], '%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.now())
            except:
                pass

            message += item_data['name'] + ": " + truncate(item_data['description'], 35) + "\n" + \
                       truncate(item_data['store'], 35) + "(" + item_data['store_address'] + ")" + "\n" + \
                       item_data['price']

            print("Sending telegram to " + str(chat_id))
            self.bot.sendMessage(chat_id=chat_id, text=message)
