import json
from threading import Thread
from time import sleep
import toogoodtogo
from telegramBot import telegramBot
import os

try:
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
except:
    print("No TELEGRAM_TOKEN given")
    exit(1)

try:
    EMAIL = os.environ['EMAIL']
except:
    print("No EMAIL given")
    exit(1)



tgtg_object = None
stored_items = dict()  # id to data


def store_credentials(c):
    data = json.dumps(c)
    with open('credentials.json', 'w') as writer:
        writer.write(data)


def load_credentials():
    try:
        with open('credentials.json', 'r') as reader:
            data = reader.read()
            return json.loads(data)
    except Exception as e:
        print(e)
        return None


def store_chat_ids(ids):
    data = json.dumps(ids[0])
    with open('chat_ids.json', 'w') as writer:
        writer.write(data)


def load_chat_ids(ids):
    try:
        with open('chat_ids.json', 'r') as reader:
            data = reader.read()
            ids[0] = json.loads(data)
    except Exception as e:
        print(e)

def loop_store_chat_ids(ids):
    while True:
        store_chat_ids(ids)
        sleep(10)



def runner():
    global tgtg_object
    global stored_items
    while True:
        items = tgtg_object.get_favourites()

        items_formatted = dict()
        for item in items:
            if item['items_available'] >= 0: # todo >0
                items_formatted[item['item']['item_id']] = item

        new_items = dict()
        removed_items = dict()

        for key in items_formatted:
            if not key in stored_items:
                new_items[key] = items_formatted[key]

        for key in stored_items:
            if not key in items_formatted:
                removed_items[key] = stored_items[key]

        stored_items = items_formatted

        if len(new_items) > 0:
            telegram_thread.sendInfoItems(stored_items)

        sleep(20)


if __name__ == '__main__':

    # init telegram
    chat_ids_list = [list()]
    load_chat_ids(chat_ids_list)
    telegram_thread = telegramBot(TELEGRAM_TOKEN, chat_ids_list, stored_items)

    # thread all 10 sec to store
    t_store_chat_ids = Thread(target=loop_store_chat_ids, args=(chat_ids_list,))
    t_store_chat_ids.start()


    sleep(1)

    # init tgtg
    credentials = load_credentials()
    if credentials is not None:
        tgtg_object = toogoodtogo.TooGoodToGoWrapper(tokens=credentials)
    else:
        tgtg_object = toogoodtogo.TooGoodToGoWrapper(email=EMAIL)
        credentials = tgtg_object.credentials
        if credentials is not None:
            store_credentials(credentials)
        else:
            print("Couldn't log in")
            exit(1)



    runner()
