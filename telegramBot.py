import datetime
import os
import sys

from telegram.ext import Updater, dispatcher, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext

from telegram.ext import CommandHandler
import logging
import html

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def truncate(str, max_len):
    return (str[:max_len] + '..') if len(str) > max_len else str


class telegramBot:
    chat_ids = None  # by reference
    bot = None
    stored_items = None  # by reference
    email = None
    message_ids = dict()  # item_id -> list(message_ids)
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
        start_handler = CommandHandler("start", self.start)
        stop_handler = CommandHandler('stop', self.stop)
        reset_handler = CommandHandler('reset', self.reset)
        info_handler = CommandHandler('info', self.info)
        clearall_handler = CommandHandler('clearall', self.clearall)
        unknown_handler = MessageHandler(Filters.command, self.unknown)

        dispatcher = updater.dispatcher
        dispatcher.add_handler(info_handler)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(stop_handler)
        dispatcher.add_handler(reset_handler)
        dispatcher.add_handler(clearall_handler)
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
        if len(context.args) < 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, please login with /start "
                                                                            "<password>!")
            return
        if len(context.args) >= 1:
            if context.args[0].lower() != self.email.lower():
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="incorrect password, please login with /start <password>!")
                return

        if update.effective_chat.id not in self.chat_ids[0]:
            self.chat_ids[0].append(update.effective_chat.id)

        context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")  # , reply_markup=reply_markup)

    def info(self, update: Update, context: CallbackContext):
        if update.effective_chat.id not in self.chat_ids[0]:
            return
        self.send_info_to_chat(self.stored_items[0], update.effective_chat.id, "Info:\n", False)

    def reset(self, update: Update, context: CallbackContext):
        if update.effective_chat.id not in self.chat_ids[0]:
            return
        self.stored_items[0] = dict()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Reset")

    def stop(self, update: Update, context: CallbackContext):
        if update.effective_chat.id not in self.chat_ids[0]:
            return
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

    def send_info_to_chat(self, stored_items, chat_id, title="New items:\n", delete_if_outdated=True):
        messages = dict()
        messages[-2] = title
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
                         'pickup_interval': datetime.datetime.strptime(item['pickup_interval']['start'],
                                                                       '%Y-%m-%dT%H:%M:%SZ').strftime(
                             "%d.%m.%Y %H:%M") + " - " + datetime.datetime.strptime(item['pickup_interval']['end'],
                                                                                    '%Y-%m-%dT%H:%M:%SZ').strftime(
                             "%d.%m.%Y %H:%M")
                         }
            try:
                item_data['cover'] = item['item']['cover_picture']['current_url']
            except:
                pass
            try:
                item_data['logo'] = item['item']['logo_picture']['current_url']
            except:
                pass

            """
            try:
                item_data['time_end'] = datetime.datetime.strptime(item['purchase_end'], '%Y-%m-%dT%H:%M:%SZ').strftime(
                    "%y.%m.%d, %H:%M") + \
                                        " remaining: " + str(
                    datetime.datetime.strptime(item['purchase_end'], '%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.now())
            except:
                pass
            """

            messages[i] = html.escape(item_data['name'] + ": " + truncate(item_data['description'], 35)) + "\n" + \
                          html.escape(
                              truncate(item_data['store'], 35) + " (" + item_data['store_address'] + ")") + "\n" + \
                          html.escape(item_data['price']) + "\n" + \
                          html.escape(item_data['pickup_interval']) + "\n" + \
                          (("<a href='" + item_data['cover'] + "'>Cover</a>\n") if 'cover' in item_data else '') + \
                          "<a href='https://share.toogoodtogo.com/item/" + i + "/'>" + (
                              item_data['name'] if len(item_data['name']) > 0 else "Click me") + " - Link</a>\n" + \
                          "\n\n"

        if len(stored_items) == 0:
            messages[-1] = "Nothing there :("
        print("Sending telegrams (" + str(len(messages) - 1) + ") to " + str(chat_id))

        for item_id in messages:
            message = messages[item_id]
            sent_message = self.bot.sendMessage(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
            if item_id != -1 and item_id != -2:  # -1 not a item_id
                if delete_if_outdated and sent_message:
                    if item_id not in self.message_ids:
                        self.message_ids[item_id] = list()
                    self.message_ids[item_id].append((chat_id, sent_message.message_id))

    def delete_chats_with_item(self, item_id):
        for message in self.message_ids[item_id]:
            print("Deleting telegram message " + str(message[0]) + " " + str(message[1]) + " from item " + str(item_id))
            self.bot.delete_message(message[0], message[1])

        del self.message_ids[item_id]

    def hello(self):
        for chat_id in self.chat_ids[0]:
            self.bot.sendMessage(chat_id=chat_id, text="Hello!")

    def clearall(self, update: Update, context: CallbackContext):
        if update.effective_chat.id not in self.chat_ids[0]:
            return
        context.bot.send_message(chat_id=update.effective_chat.id, text="Going to clearall!")

        for file in os.scandir('data'):
            print(file.path)
            os.unlink(file.path)
        os._exit(0)