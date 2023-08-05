# curv_amqp
Pika framework that handles reconnecting while using a blocking connection and has helpful defaults, building blocks, type hints, and a priority requeue method
## Installing package
```shell script
pip install curv-amqp
```

## Installing for local development
```shell script
git clone https://github.com/rep-ai/curv_amqp.git
cd curv_amqp
pip install -r requirements.txt
pip install -e .
```

## Basic Usage
```python
from curv_amqp.connection import Connection, ConnectionParameters
from curv_amqp.publisher import Publisher
from curv_amqp.consumer import Consumer, ConsumerMessage
host = 'localhost'
queue_name = 'test'
connection = Connection(parameters=ConnectionParameters(host))

publisher = Publisher(connection=connection)
publisher.publish(routing_key=queue_name, body=b'message')

consumer = Consumer(connection=connection)

def on_message_callback(message: ConsumerMessage):
    print('message.body:', message.body)
    message.ack()
    # you don't have to stop consuming here - but you do have to stop the consumer in this thread
    # eventually since consumer.consume is blocking
    message.consumer.stop_consuming()

consumer.consume(queue=queue_name, prefetch_count=1, on_message_callback=on_message_callback)

```
## Usage
```python
from argparse import ArgumentParser

from curv_amqp.connection import Connection, URLParameters, ConnectionParameters
from curv_amqp.publisher import Publisher
from curv_amqp.consumer import Consumer, ConsumerMessage
from curv_amqp.exceptions import ChannelClosedError, ConnectionClosedError, RequeueRetryCountError


def main():
    parser = ArgumentParser()
    parser.add_argument('--url', type=str, default='localhost', help='amqp url or localhost - '
                                                                     'localhost assumes rabbitmq is installed - '
                                                                     '"brew install rabbitmq"')
    parser.add_argument('--queue', type=str, default='test-queue-name', help='amqp queue name')
    parser.add_argument('--body', type=str, default='your message', help='amqp message body')
    args = parser.parse_args()
    # pass in URLParameters or ConnectionParameters
    # its recommended that a single connection per process is used.
    url: str = args.url
    parameters = ConnectionParameters(url) if url is 'localhost' else URLParameters(url)
    queue_name = args.queue
    body = bytes(args.body, encoding='utf-8')

    connection = Connection(parameters=parameters)
    # testing auto reconnect for connection
    connection.blocking_connection.close()
    # its required that two different channels are used for a publisher and consumer
    # NOTE: will automatically declare queue for you
    publisher = Publisher(connection=connection)
    # testing auto reconnect for channel / publisher
    publisher.blocking_channel.close()
    publisher.publish(routing_key=queue_name, body=body)

    consumer = Consumer(connection=connection)
    # testing auto reconnect for channel / consumer
    consumer.blocking_channel.close()

    def on_message_callback(message: ConsumerMessage):
        print('message.body:', message.body)
        print('message.properties.priority', message.properties.priority)
        try:
            message.priority_requeue(publisher)
        except RequeueRetryCountError as ex:
            print(ex)
            message.ack()
            message.consumer.stop_consuming()

    consumer.consume(queue=queue_name, prefetch_count=1, on_message_callback=on_message_callback)

    publisher.publish(routing_key=queue_name, body=body)
    for msg in consumer.consume_generator(queue=queue_name, prefetch_count=1, auto_ack=True, inactivity_timeout=1):
        print('msg.body:', msg.body)

    try:
        # testing proper channel close
        publisher.close()
        publisher.publish(routing_key=queue_name, body=body)
    except ChannelClosedError as e:
        print(e)

    try:
        # testing proper connection close
        publisher = Publisher(connection=connection)
        connection.close()
        publisher.publish(routing_key=queue_name, body=body)
    except ConnectionClosedError as e:
        print(e)


if __name__ == '__main__':
    main()

```

## Updating package
```shell script
# update __version__ in __init__.py
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*
```
### or using this script - note it will remove build and dist directories
```shell script
bash deploy.sh
```
