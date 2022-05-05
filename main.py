import json
from threading import Thread
from time import sleep
import toogoodtogo
from telegramBot import telegramBot
import os
from pathlib import Path

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

try:
    TGTG_REFRESH = int(os.environ['TGTG_REFRESH'])
except:
    print("No TGTG_REFRESH given; defaulting to 20")
    TGTG_REFRESH = 20


tgtg_object = None
stored_items = [dict()]  # id to data


def store_credentials(c):
    data = json.dumps(c)
    with open(os.path.join('data', 'credentials.json'), 'w') as writer:
        writer.write(data)


def load_credentials():
    try:
        with open(os.path.join('data', 'credentials.json'), 'r') as reader:
            data = reader.read()
            return json.loads(data)
    except Exception as e:
        print(e)
        return None


def store_chat_ids(ids):
    data = json.dumps(ids[0])
    with open(os.path.join('data', 'chat_ids.json'), 'w') as writer:
        writer.write(data)


def load_chat_ids(ids):
    try:
        with open(os.path.join('data', 'chat_ids.json'), 'r') as reader:
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
        try:
            print("Checking for new items...")
            items = tgtg_object.get_favourites()

            items_formatted = dict()
            for item in items:
                if item['items_available'] > 0:
                    items_formatted[item['item']['item_id']] = item

            new_items = dict()
            removed_items = dict()

            for key in items_formatted:
                if not key in stored_items[0]:
                    new_items[key] = items_formatted[key]

            for key in stored_items[0]:
                if not key in items_formatted:
                    removed_items[key] = stored_items[0][key]

            stored_items[0] = items_formatted

            print({'new_items': len(new_items), 'removed_items': len(removed_items)})

            if len(new_items) > 0:
                telegram_thread.send_info_items(stored_items[0])

            for item_id in removed_items:
                telegram_thread.delete_chats_with_item(item_id)
        except Exception as e:
            print(e)

        sleep(TGTG_REFRESH)


if __name__ == '__main__':
    Path("data").mkdir(exist_ok=True)

    # init telegram
    chat_ids_list = [list()]
    load_chat_ids(chat_ids_list)
    telegram_thread = telegramBot(TELEGRAM_TOKEN, chat_ids_list, stored_items, EMAIL)

    telegram_thread.hello()

    # thread all 10 sec to store
    t_store_chat_ids = Thread(target=loop_store_chat_ids, args=(chat_ids_list,))
    t_store_chat_ids.start()
    print("Telegram running...")

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

    print("Tgtg running...")

    runner()
