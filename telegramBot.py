import datetime

from telegram.ext import Updater, dispatcher, MessageHandler, Filters
from telegram import Update
from telegram.ext import CallbackContext

from telegram.ext import CommandHandler


def truncate(str, max_len):
    return (str[:max_len] + '..') if len(str) > max_len else str


class telegramBot:
    chat_ids = None  # by reference
    bot = None
    stored_items = None

    def __init__(self, token, chat_ids_list, stored_items):
        self.stored_items = stored_items
        self.chat_ids = chat_ids_list
        updater = Updater(token=token, use_context=True)
        start_handler = CommandHandler('start', self.start)
        stop_handler = CommandHandler('stop', self.stop)
        reset_handler = CommandHandler('reset', self.reset)
        echo_handler = MessageHandler(Filters.text & (~Filters.command), self.echo)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(echo_handler)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(stop_handler)
        dispatcher.add_handler(reset_handler)
        self.bot = updater.bot
        updater.start_polling()

    def start(self, update: Update, context: CallbackContext):
        if update.effective_chat.id not in self.chat_ids[0]:
            self.chat_ids[0].append(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")

    def echo(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    def reset(self, update: Update, context: CallbackContext):
        self.stored_items = dict()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Reset")

    def stop(self, update: Update, context: CallbackContext):
        try:
            self.chat_ids[0].remove(update.effective_chat.id)
        except:
            pass
        context.bot.send_message(chat_id=update.effective_chat.id, text="Bye!")

    def sendInfoItems(self, stored_items):
        message = "New items:\n"
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

        for chat_id in self.chat_ids[0]:
            self.bot.sendMessage(chat_id=chat_id, text=message)
