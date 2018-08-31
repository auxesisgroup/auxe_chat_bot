import time

import telepot
import ConfigParser
import logging

from telepot.loop import MessageLoop
from telepot.delegate import (
    create_open, pave_event_space,
    include_callback_query_chat_id, per_chat_id)
from apscheduler.scheduler import Scheduler

from db_folder import db_config


db_client_connection = db_config.mongo_connection()
db_name = db_client_connection['auxesis_chatbot_db']
db_updates_collection = db_name['new_users_table']
db_message_collection = db_name['new_msg_table']

config = ConfigParser.ConfigParser()
config.read('config.ini')

TOKEN = config.get('General', 'api_key')
group_id = list(map(int, config.get('General', 'group_id').split(',')))
sched = Scheduler()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='log.log', level=logging.INFO)


class AuxEChat(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(AuxEChat, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == "new_chat_member":
            user_name = '@{}'.format(msg['new_chat_participant']['first_name'])
            if len(user_name) > 3:
                if msg['new_chat_participant']['is_bot'] is True & msg['new_chat_participant']['id'] not in group_id:
                    self.bot.kickChatMember(msg['chat']['id'], msg['new_chat_participant']['id'])
                    logging.info("User {} (ID: {}) Kicked Out of the Group! Hooray!".format(user_name, msg['new_chat_participant']['id']))
                else:
                    new_user_name = msg['new_chat_participant']['first_name']
                    new_user = new_user_name.title()
                    db_updates_collection.insert_one(
                        {
                            'new_user': new_user,
                            'chat_id': msg['chat']['id'],
                            'message_id': msg['message_id'],
                            'date': msg['date'],
                            'group': msg['chat']['title'],
                            "user_flag": True
                        }
                    )
                    logging.info("{} has joined with {} chat id to {} group .".format(user_name, msg['chat']['id'], msg['chat']['title']))

            else:
                self.bot.kickChatMember(msg['chat']['id'], msg['new_chat_participant']['id'])
                logging.info("User {} (ID: {}) Kicked Out of the Group! Hooray!".format(user_name, msg['new_chat_participant']['id']))


    @sched.interval_schedule(seconds=60)
    def _sent_message():

        new_users_list = list(db_updates_collection.find({"user_flag": True}, {"date": 1, "new_user": 1, "chat_id":1, "user_flag":1, "_id": 0}))
        print new_users_list
        chat_id = [d["chat_id"] for d in new_users_list if d["chat_id"] in group_id ]
        print chat_id
        users_list = [d["new_user"] for d in new_users_list]
        print users_list

        if len(users_list) >= 2:
            bot.sendMessage(chat_id=chat_id[0], text="Welcome " + ', '.join(users_list) + " to Auxledger community. Have you checked out our [website](https://auxledger.org/) and got yourself whitelisted? Do check out the pinned message to get continuous updates.", parse_mode='Markdown')
            logging.info("Message Sent to UserList {} !".format(users_list))
        elif len(users_list) == 1:
            bot.sendMessage(chat_id=chat_id[0], text="Welcome {} to Auxledger community. Have you checked out our [website](https://auxledger.org/) and got yourself whitelisted? Do check out the pinned message to get continuous updates.".format(users_list), parse_mode='Markdown')
            logging.info("Message Sent to User {} !".format(users_list))
        else:
            time.sleep(10)
            pass

        for i in new_users_list:
            db_updates_collection.find_one_and_update({'new_user': i["new_user"], 'chat_id': i["chat_id"]}, {'$set': {'user_flag': False}})
            logging.info("{}'s user_flag changed ,now its :{} ,".format(i['new_user'], 'False'))


bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['group']), create_open, AuxEChat, timeout=200),
])


def main():
    MessageLoop(bot).run_as_thread()
    logging.info("Bot started.")
    sched.start()
    while 1:
        time.sleep(15)


if __name__ == '__main__':
    main()
