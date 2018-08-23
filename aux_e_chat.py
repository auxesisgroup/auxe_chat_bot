import time

import nltk
import telepot
import ConfigParser
import logging

from nltk import FreqDist
from telepot.loop import MessageLoop
from telepot.delegate import (
    create_open, pave_event_space,
    include_callback_query_chat_id, per_chat_id)
from apscheduler.scheduler import Scheduler
from nltk.corpus import stopwords

from db_folder import db_config


db_client_connection = db_config.mongo_connection()
db_name = db_client_connection['auxesis_chatbot_db']
db_updates_collection = db_name['new_users_table']

config = ConfigParser.ConfigParser()
config.read('config.ini')

TOKEN = config.get('General', 'api_key')
administrators = list(map(int, config.get('General', 'admins').split(',')))
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
                if msg['new_chat_participant']['is_bot'] is True & msg['new_chat_participant']['id'] not in administrators:
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

        if content_type == "text":
            fdist_list =[]
            most_common_words_list =[]
            logging.info("bot got message it will proceeds on it.")
            if msg['text']:
                sentence = msg['text'].lower()

                test_match_string1 = "auxchips issued"
                test_match_string2 = "security Auxchips "
                test_match_string3 = "restrictions transaction limit"
                test_match_string4 = "cryptocurrency transferring exchange "
                test_match_string5 = "kyc process "
                test_match_string6 = "unsold "
                test_match_string7 = "auxledger"
                test_match_string8 = "auxChips"
                test_match_string9 = "auxGas"
                stop_words = set(stopwords.words('english'))
                sentence_tokenize = nltk.tokenize.sent_tokenize(sentence)
                for sent in sentence_tokenize:
                    word_tokenize = nltk.tokenize.word_tokenize(sent)
                    filtered_sentence = [w for w in word_tokenize if not w in stop_words]
                    fdist = FreqDist(filtered_sentence)
                    fdist_list = fdist.most_common(6)
                    print fdist_list
                    most_common_words_list = [x[0].encode('utf-8') for x in fdist_list]
                    print most_common_words_list

                    if any(word in test_match_string1 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="AuxChips token have an adequate supply of 100 million tokens which makes it limited for additional tokens to be issued.", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string2 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="AuxChips is a utility token which makes it flexible and executable for its users, thus gives you administrative rights in the network. ", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in question.".format(most_common_words_list))

                    elif any(word in test_match_string3 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text=" It has to come on forum yet.", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string4 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text=" If you are going for Crowdsale, then transferring the Cryptocurrency from the exchange is not applicable. .", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string5 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="KYC is the mandatory phenomenon for Crowdsale participants, hence it is to be considered.", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string6 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="Unsold tokens will be given out proportionally to the Auxchips holder and if not, then it ought to be burnt. .", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string7 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="Auxledger, the internet of blockchain allows transactions between different blockchain networks. Auxledger provides the methodologies to deploy multi-tier Blockchain networks and ensuring cross-chain transactions, communication is possible in a trust-less manner while maintaining the complete data integrity.", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string8 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="AuxChips Provides us administrative access into the Auxnet and the ability to create tiered networks. It gives us the ability to participate in block formation, deploying a new tiered network and also the voting rights when making an important decision on network governance.", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

                    elif any(word in test_match_string9 for word in most_common_words_list):
                        time.sleep(10)
                        self.sender.sendMessage(text="AuxGas is fuel in Auxnet ecosystem which incentivizes network to participate in any consensus process, make computation, allow storage and thus securing the integrity of network. New AuxGas can further be mined by AuxChips holder while participating in a hybrid proof of stake consensus model.", reply_to_message_id=chat_id, parse_mode='Markdown')
                        logging.info("{} list of keywords found in answer.".format(most_common_words_list))

            elif msg['text'].lower().startswith(("wh", "how")) or msg['text'].lower().endswith(("?")):
                time.sleep(300)
                self.sender.sendMessage(text= "Thanks for asking Question with us !! You can find relative answer here in [whitepaper](https://auxledger.org/) Till our admin team review your question.", reply_to_message_id=chat_id, parse_mode='Markdown')

    @sched.interval_schedule(seconds=60)
    def _sent_message():

        new_users_list = list(db_updates_collection.find({"user_flag": True}, {"date": 1, "new_user": 1, "chat_id":1, "user_flag":1, "_id": 0}))

        chat_id = [d["chat_id"] for d in new_users_list if d["chat_id"] in administrators ]
        print chat_id
        users_list = [d["new_user"] for d in new_users_list]
        print users_list

        for i in new_users_list:
            db_updates_collection.find_one_and_update({'new_user': i["new_user"], 'chat_id': i["chat_id"]}, {'$set': {'user_flag': False}})
            logging.info("{}'s user_flag changed ,now its :{} .".format(i['new_user'], 'False'))

        if len(users_list) >= 2:
            bot.sendMessage(chat_id=chat_id[0], text="Hey !  *" + ' , '.join(users_list) + "* . Welcome to Auxledger community.Did you check our [website](https://auxledger.org/) and got yourself whitelisted? Do check out pinned message for regular updates and engage in our growing community.", parse_mode='Markdown')
            logging.info("Message Sent to UserList {} !".format(users_list))
        elif len(users_list) == 1:
            bot.sendMessage(chat_id=chat_id[0], text="Hey ! *{}* .  Welcome to Auxledger community.Did you checked our [website](https://auxledger.org/) and got yourself whitelisted? Do check out pinned message for regular updates and engage in our growing community.".format(users_list[0]), parse_mode='Markdown')
            logging.info("Message Sent to UserList {} !".format(users_list))
        else:
            time.sleep(10)
            pass


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
