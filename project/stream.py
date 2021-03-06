from tweepy import Stream
from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from kafka import KafkaProducer

import csv
import pickle
import argparse
import json
import time


HASH_TAG = ['']
TOPIC = ''

IP = 'localhost'
PORT = '9092'
producer = None

ACCESS_TOKEN = ''
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
TWITTER_CSV = '/home/achanta/Desktop/twitter2.csv'

def set_kafka():
    global producer
    producer = KafkaProducer(bootstrap_servers=['%s:%s' % (IP, PORT)])


def credentials_load():
    # twitter app token key and consumer key
    data = pickle.load(open("creds.p", 'rb'))
    global ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
    ACCESS_TOKEN = data['ACCESS_TOKEN']
    ACCESS_SECRET = data['ACCESS_SECRET']
    CONSUMER_KEY = data['CONSUMER_KEY']
    CONSUMER_SECRET = data['CONSUMER_SECRET']


def authenticate():
    credentials_load()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return auth


class MyStreamListener(StreamListener):
    def __int__(self):
        pass

    def on_data(self, data):
        # Producer produces data for consumer
        producer.send(TOPIC, data.encode('utf-8'))
        print(data)
        return True

    def on_error(self, status):
        # Status printing
        print(status)
        return True


def stream():
    set_kafka()
    my_stream = Stream(auth=authenticate(), listener=MyStreamListener())
    my_stream.filter(languages=['en'], track=HASH_TAG)
    my_stream.sample()


def csv_data():
    set_kafka()
    with open(TWITTER_CSV, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            loc = None
            if len(row) > 1 and len(row[1]) != 0:
                loc = row[1]
            data = {
                'text': row[0],
                'user': {
                    'location': loc
                }
            }
            print(data)
            publish_message(TOPIC, json.dumps(data))
            time.sleep(2)


def publish_message(topic_name, value):
    try:
        producer.send(topic_name, key='foo'.encode('utf-8'), value=value.encode('utf-8'))
        producer.flush()
    except Exception as e:
        print('Exception in publishing message')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process tweets from twitter and stream them through kafka topic.')
    parser.add_argument('--hashtag', default='accident', dest='hashtag',
                        help='hashtag of the twitter app to retrieve tweets')
    parser.add_argument('--topic', default='twitter', dest='topic',
                        help='topic where kakfa can publish messages')

    args = parser.parse_args()
    HASH_TAG.append(args.hashtag)
    TOPIC = args.topic
    stream()
    # csv_data()
