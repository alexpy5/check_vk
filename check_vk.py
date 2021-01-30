import os
from datetime import datetime

import vk_api
import telebot
from dotenv import load_dotenv


load_dotenv()


TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
VK_TOKEN = os.environ.get('VK_TOKEN')
MSG_SEPARATOR = '-' * 40


def main():
    last_id = get_last_id()
    tg_bot = telebot.TeleBot(TG_BOT_TOKEN)
    tg_bot.config['api_key'] = TG_BOT_TOKEN
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    conversations = vk.messages.getConversations(filter='unread')
    if conversations:
        conversations = conversations['items']
        vk_msgs_list = []
        for conv in conversations:
            messages, full_name = get_unread_messages(conv, vk)
            messages = messages['items']
            vk_msgs_list = add_messages_to_list(messages, last_id, full_name,
                                                vk_msgs_list)
            if vk_msgs_list:
                tg_text, last_id = make_text_for_tg(last_id, vk_msgs_list)
                tg_bot.send_message(TG_CHAT_ID, tg_text)
                with open('last_id.txt', 'w', encoding='utf-8') as txt_file:
                    last_id = str(last_id)
                    txt_file.write(last_id)


def get_last_id():
    if os.path.isfile('last_id.txt'):
        with open('last_id.txt', 'r', encoding='utf-8') as txt_file:
            last_id = txt_file.read()
            return int(last_id)
    else:
        with open('last_id.txt', 'w', encoding='utf-8') as txt_file:
            last_id = '0'
            txt_file.write(last_id)
            return 0


def get_unread_messages(conversation, vk):
    from_id = conversation['last_message']['from_id']
    user = vk.users.get(user_ids=from_id)
    full_name = user[0]['first_name'] + ' ' + user[0]['last_name']
    unread_count = conversation['conversation']['unread_count']
    vk_msgs = vk.messages.getHistory(count=unread_count, user_id=from_id)
    return vk_msgs, full_name


def add_messages_to_list(messages, last_id_vk, full_name, vk_msgs_list):
    last_id_vk = int(last_id_vk)
    for msg in messages:
        if msg['id'] > last_id_vk:
            vk_msgs_list.append(
                (msg['id'], full_name, msg['date'], msg['text'])
            )
    return vk_msgs_list


def make_text_for_tg(last_id, vk_msgs_list):
    vk_msgs_list.sort()
    last_id = vk_msgs_list[-1][0]
    text = '# New VK messages \n\n'
    for msg in vk_msgs_list:
        timestamp = datetime.fromtimestamp(msg[2]).strftime("%H:%M - %d.%m.%Y")
        text += '{0}\n{1} - {2}\n\n{3}\n'.format(
            MSG_SEPARATOR, msg[1], timestamp, msg[3])
    return text, last_id


if __name__ == '__main__':
    main()
