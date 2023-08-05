from typing import Optional, Dict, List, Callable
import uuid
from multiprocessing import Process

from dataclasses import dataclass, asdict

import pika
from pika.exceptions import ChannelClosed
from pika.frame import Method
from pika.spec import Queue
from pika.connection import Parameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import ChannelClosedByBroker


from pika.spec import BasicProperties
from pika.spec import Basic


@dataclass
class UnDelivered:
    delivery_tag: int
    redelivered: bool
    routing_key: str
    exchange: Optional[str]


@dataclass
class MockPublishedMessage:
    method_info: UnDelivered
    properties: BasicProperties
    body: bytes


@dataclass
class MockDeclaredQueue:
    queue: str
    passive: bool
    durable: bool
    exclusive: bool
    auto_delete: bool
    arguments: Optional[dict]
    consumer_count: int
    published_messages: Dict[int, MockPublishedMessage]
    unacknowledged_messages: Dict[int, MockPublishedMessage]

    @property
    def message_count(self):
        return len(self.published_messages) + len(self.unacknowledged_messages)


class MockBlockingChannel:
    # TODO: Figure out correct pika errors
    consumer_tags: List[str]

    def __init__(self, channel_number: int, connection: "MockBlockingConnection"):
        if channel_number in connection._mock_channels:
            raise NotImplementedError(
                "The correct pika error for a channel_number already existing"
                "has not been implemented..."
            )
        self.connection = connection
        self.channel_number = channel_number
        self._is_closed = False
        self.prefetch_count = 0
        self.connection._mock_channels[channel_number] = self
        self.consumer_tags = []

    @property
    def is_closed(self):
        return self._is_closed or self.connection.is_closed

    def close(self):
        self._is_closed = True

    def basic_qos(
        self, prefetch_size: int = 0, prefetch_count: int = 0, global_qos: bool = False
    ):
        self.prefetch_count = prefetch_count
        if prefetch_size:
            NotImplementedError("prefetch_size not mock implemented")
        if global_qos:
            NotImplementedError("global_qos not mock implemented")

    def queue_declare(
        self,
        queue,
        passive=False,
        durable=False,
        exclusive=False,
        auto_delete=False,
        arguments=None,
    ):
        if exclusive:
            raise NotImplementedError("exclusive not implemented")
        if auto_delete:
            raise NotImplementedError("auto_delete not implemented")
        if arguments:
            raise NotImplementedError("arguments not implemented")
        if passive:
            if queue not in self.connection._declared_queues:
                # TODO: Get real reply code and reply text - Note not used anywhere yet
                print("WARNING: Passive error ChannelClosed not full implemented")
                raise ChannelClosed(reply_code=0, reply_text="passive")
        else:
            declared_queue = MockDeclaredQueue(
                queue=queue,
                passive=passive,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments,
                consumer_count=0,
                published_messages={},
                unacknowledged_messages={},
            )

            if queue in self.connection._declared_queues:
                declared_queue_dict = asdict(declared_queue)
                # Its not in the docstring but this method will throw if you pass in
                # a different config then the originally defined queue...
                for key, value in asdict(self.connection._declared_queues[queue]):
                    if key in ["message_count", "consumer_count"]:
                        continue
                    if value != declared_queue_dict[key]:
                        # TODO: - do the rest of the error messages properly - this only works for
                        #  durable being different
                        if key != "durable":
                            raise NotImplementedError(
                                f"No mock error implemented for '{key}'"
                            )
                        raise ChannelClosedByBroker(
                            reply_code=406, reply_text=f"Mock error for {key}"
                        )
            else:
                self.connection._declared_queues[queue] = declared_queue

        method = Queue.DeclareOk(
            queue=queue,
            message_count=self.connection._declared_queues[queue].message_count,
            consumer_count=self.connection._declared_queues[queue].consumer_count,
        )
        return Method(self.channel_number, method)

    def queue_delete(self, queue, if_unused=False, if_empty=False):
        """Delete a queue from the broker.

        :param str queue: The queue to delete
        :param bool if_unused: only delete if it's unused
        :param bool if_empty: only delete if the queue is empty
        :returns: Method frame from the Queue.Delete-ok response
        :rtype: `pika.frame.Method` having `method` attribute of type
            `spec.Queue.DeleteOk`
        """
        # TODO: Figure out proper error messages from pika
        if queue not in self.connection._declared_queues[queue]:
            NotImplementedError(
                "The correct error message for deleted a queue "
                "that does not exists is not implemented!"
            )

        is_unused = not self.connection._declared_queues[queue].consumer_count
        is_empty = not self.connection._declared_queues[queue].message_count
        if if_unused and not is_unused or if_empty and not is_empty:
            NotImplementedError(
                "The correct error message for if_unused and is_empty "
                "are not implemented!"
            )

        method = Queue.DeleteOk(
            message_count=self.connection._declared_queues[queue].message_count,
        )
        return Method(self.channel_number, method)

    def basic_publish(
        self,
        exchange: str,
        routing_key: str,
        body: bytes,
        properties: BasicProperties = None,
        mandatory: bool = False,
    ):
        if mandatory:
            print(
                "WARNING: I have not seen mandatory work in the real implementation so I do not want to mock it"
                "it is supposed to raise a NackError - but it does not work when I test it."
            )
        if exchange:
            raise NotImplementedError("exchange")
        if routing_key not in self.connection._declared_queues:
            raise NotImplementedError(
                "correct queue not declared yet error has not been added yet."
            )

        properties = BasicProperties() if properties is None else properties

        while True:
            delivery_tag = self.connection._declared_queues[routing_key].message_count
            if (
                delivery_tag
                not in self.connection._declared_queues[
                    routing_key
                ].unacknowledged_messages
            ):
                break
            if (
                delivery_tag
                not in self.connection._declared_queues[routing_key].published_messages
            ):
                break
            # TODO: This does not match pika exactly and could cause
            print("Warning! using uuid delivery tag instead of normal pika in sequence")
            delivery_tag = uuid.uuid4().int

        method_info = UnDelivered(
            delivery_tag=delivery_tag,
            redelivered=False,
            routing_key=routing_key,
            exchange=exchange,
        )
        message = MockPublishedMessage(
            method_info=method_info, body=body, properties=properties
        )

        self.connection._declared_queues[routing_key].published_messages[
            method_info.delivery_tag
        ] = message

    _is_stopped: bool = True
    consumer_tag: Optional[str] = None

    def stop_consuming(self):
        self._is_stopped = True

    def _create_message_args(self, message: MockPublishedMessage):
        return (
            self,
            Basic.Deliver(
                consumer_tag=self._consumer_tag,
                delivery_tag=message.method_info.delivery_tag,
                redelivered=message.method_info.redelivered,
                exchange=message.method_info.exchange,
                routing_key=message.method_info.routing_key,
            ),
            message.properties,
            message.body,
        )

    def start_consuming(self):
        if self._on_message_callback is None or self._queue is None:
            raise NotImplementedError(
                "consumer not created yet - correct error not implemented"
            )

        self._is_stopped = False

        while not self._is_stopped:
            if self._queue not in self.connection._declared_queues[self._queue]:
                print("Warning: queue was deleting with consumer still running.")
                raise NotImplementedError(
                    "queue was deleted while consuming, pika error not implemented"
                )

            if self.connection._declared_queues[self._queue].message_count == 0:
                continue

            published_messages = self.connection._declared_queues[
                self._queue
            ].published_messages
            unacknowledged_messages = self.connection._declared_queues[
                self._queue
            ].unacknowledged_messages
            message_args = []
            for i, tag in enumerate(published_messages.keys()):
                if self.prefetch_count != 0 and i > self.prefetch_count:
                    break
                message = published_messages.pop(tag)
                unacknowledged_messages[tag] = message
                message_args.append(self._create_message_args(message))
                self._on_message_callback(*self._create_message_args(message))

        if self.connection._declared_queues[self._queue].consumer_count > 0:
            self.connection._declared_queues[self._queue].consumer_count -= 1
        else:
            raise Exception(
                "tried to lower consumer count below zero when exiting consuming."
            )

    def basic_consume(
        self,
        queue,
        on_message_callback,
        auto_ack=False,
        exclusive=False,
        consumer_tag=None,
        arguments=None,
    ):
        if consumer_tag in self.consumer_tags:
            raise pika.exceptions.DuplicateConsumerTag(self.channel_number)
        self._consumer_tag = (
            consumer_tag
            if consumer_tag
            else f"ctag{self.channel_number}.{uuid.uuid4().hex}"
        )
        self._queue = queue

        self._auto_ack = auto_ack
        self._exclusive = exclusive
        self._arguments = arguments
        if queue not in self.connection._declared_queues:
            raise NotImplementedError(
                "queue doesnt exist - correct error not implemented"
            )
        self.connection._declared_queues[queue].consumer_count += 1
        self._on_message_callback = on_message_callback

    def basic_ack(self, delivery_tag=0, multiple=False):
        if multiple:
            raise NotImplementedError("basic_ack multiple")
        if (
            delivery_tag
            not in self.connection._declared_queues[self._queue].published_messages
        ):
            raise NotImplementedError(
                "pika error for missing delivery_tag not implemented"
            )
        message = self.connection._declared_queues[
            self._queue
        ].unacknowledged_messages.pop(delivery_tag)
        self.connection._debug_acknowledged_messages.append(
            (self.channel_number, self._queue, message)
        )

    def basic_nack(self, delivery_tag=None, multiple=False, requeue=True):
        if multiple:
            raise NotImplementedError("basic_ack multiple")
        message = self.connection._declared_queues[
            self._queue
        ].unacknowledged_messages.pop(delivery_tag)
        if not requeue:
            self.connection._debug_nacknowledged_messages.append(
                (self.channel_number, self._queue, message)
            )
        else:
            if (
                delivery_tag
                in self.connection._declared_queues[self._queue].published_messages
            ):
                raise Exception(
                    "mock failed to requeue nacked message because of delivery tag conflict"
                )
            self.connection._declared_queues[self._queue].published_messages[
                delivery_tag
            ] = message


class MockBlockingConnection:
    _declared_queues: Dict[str, MockDeclaredQueue] = {}
    _mock_channels: Dict[int, BlockingChannel] = {}
    _debug_acknowledged_messages: list = []
    _debug_nacknowledged_messages: list = []

    def __init__(self, _: Parameters):
        self.is_closed = False

    def channel(self, channel_number: int = None) -> BlockingChannel:
        if channel_number is None:
            channel_number = len(self._mock_channels)

        return MockBlockingChannel(channel_number, self)

    def close(self):
        self.is_closed = True
