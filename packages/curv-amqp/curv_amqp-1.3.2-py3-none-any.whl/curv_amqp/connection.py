import atexit
from typing import Callable, Any, Optional
from logging import Logger, getLogger, warning
from time import time

from pika.connection import URLParameters, ConnectionParameters, Parameters
from pika.adapters.blocking_connection import BlockingConnection, BlockingChannel
from pika.exceptions import ConnectionWrongStateError, ChannelClosedByBroker
from pika import PlainCredentials

from curv_amqp.exceptions import ConnectionClosedError, ReconnectingToFastError
from curv_amqp.conditional_reconnect import (
    conditional_reconnect as _conditional_reconnect,
)

URLParameters = URLParameters
ConnectionParameters = ConnectionParameters
PlainCredentials = PlainCredentials


class Connection:
    blocking_connection: BlockingConnection

    def __init__(
        self,
        parameters: Parameters,
        at_exit: Callable[["Connection"], Any] = None,
        logger: Logger = getLogger(__name__),
        reconnect_time_threshold: float = 1,
        reconnect_attempt_threshold: int = 3,
    ):
        self.reconnect_time_threshold = reconnect_time_threshold
        self.reconnect_attempt_threshold = reconnect_attempt_threshold
        self.logger = logger
        self.parameters = parameters
        self.blocking_connection = BlockingConnection(self.parameters)
        self.is_closed = False
        self._prev_connection_time = time()
        self._reconnected_too_fast_count = 0
        if at_exit is None:
            self._at_exit = self._at_exit_close
        else:
            self._at_exit = at_exit
        atexit.register(self._at_exit)

    @classmethod
    def create(
        cls,
        host: str,
        credentials: Optional[PlainCredentials] = None,
        virtual_host: Optional[str] = None,
        port: int = 5672,
        heartbeat: int = 0,
        blocked_connection_timeout: float = 300,
        socket_timeout: float = 400,
        stack_timeout: float = 600,
        connection_attempts: int = 3,
        retry_delay: float = 0.2,
    ) -> "Connection":
        """Helper class method - Create a new Connection with different defaults then ConnectionParameters
        NOTE: By default will use localhost or environment variables, disables heartbeat and has 3 connection attempts

        :param str host: Hostname or IP Address to connect to
        :param int port: TCP port to connect to
        :param str virtual_host: RabbitMQ virtual host to use
        :param pika.credentials.Credentials credentials: auth credentials
        :param int|None|callable heartbeat: Controls AMQP heartbeat timeout negotiation
            during connection tuning. An integer value always overrides the value
            proposed by broker. Use 0 to deactivate heartbeats and None to always
            accept the broker's proposal. If a callable is given, it will be called
            with the connection instance and the heartbeat timeout proposed by broker
            as its arguments. The callback should return a non-negative integer that
            will be used to override the broker's proposal.
        :param int connection_attempts: Maximum number of retry attempts
        :param int|float retry_delay: Time to wait in seconds, before the next
        :param int|float blocked_connection_timeout: A non-negative timeout, in seconds, for the
            connection to remain blocked (triggered by Connection.Blocked from
            broker); if the timeout expires before connection becomes unblocked,
            the connection will be torn down, triggering the adapter-specific
            mechanism for informing client app about the closed connection:
            passing `ConnectionBlockedTimeout` exception to on_close_callback
            in asynchronous adapters or raising it in `BlockingConnection`.
        :param int|float socket_timeout: Positive socket connect timeout in
            seconds.
        :param int|float stack_timeout: Positive full protocol stack
            (TCP/[SSL]/AMQP) bring-up timeout in seconds. It's recommended to
            set this value higher than `socket_timeout`.
        """
        if host != "localhost" and credentials is None:
            raise ValueError(
                'Credentials must be provided unless using host="localhost"'
            )

        if credentials is None:
            credentials = ConnectionParameters.DEFAULT_CREDENTIALS

        if virtual_host is None:
            virtual_host = ConnectionParameters.DEFAULT_VIRTUAL_HOST

        def heartbeat_func(_, proposed_heartbeat: int):
            warning(f"proposed_heartbeat: {proposed_heartbeat}")
            return heartbeat

        parameters = ConnectionParameters(
            host=host,
            credentials=credentials,
            port=port,
            virtual_host=virtual_host,
            connection_attempts=connection_attempts,
            retry_delay=retry_delay,
            heartbeat=heartbeat_func,
            socket_timeout=socket_timeout,
            stack_timeout=stack_timeout,
            blocking_connection_timeout=blocked_connection_timeout,
        )
        return cls(parameters=parameters)

    def close_connection(self):
        self.logger.info(
            f"close_connection called while "
            f'self.blocking_connection.is_closed="{self.blocking_connection.is_closed}"'
        )
        if not self.blocking_connection.is_closed:
            try:
                self.blocking_connection.close()
            except ConnectionWrongStateError as e:
                self.logger.error(e, exc_info=True)
            except ChannelClosedByBroker as e:
                self.logger.error(e, exc_info=True)

    def _at_exit_close(self):
        try:
            self.close()
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def close(self):
        self.logger.info(f"close called while " f'self.is_closed="{self.is_closed}"')
        self.is_closed = True
        self.close_connection()
        atexit.unregister(self._at_exit)

    def conditional_reconnect(self):
        if self.is_closed:
            raise ConnectionClosedError("Connection is closed!")
        if self.blocking_connection.is_closed:
            time_since_last_connection = time() - self._prev_connection_time
            self.logger.info(
                f"Connection time_since_last_connection: "
                f'"{time_since_last_connection}"'
            )
            if time_since_last_connection < self.reconnect_time_threshold:
                self._reconnected_too_fast_count += 1
                if self._reconnected_too_fast_count > self.reconnect_attempt_threshold:
                    raise ReconnectingToFastError(
                        "Connection was attempting to reconnect too quickly"
                    )
            else:
                self._reconnected_too_fast_count = 0
            self.blocking_connection = BlockingConnection(self.parameters)
            self._prev_connection_time = time()

    @_conditional_reconnect
    def channel(self, channel_number: int = None) -> BlockingChannel:
        """Create a new channel with the next available channel number or pass
        in a channel number to use. Must be non-zero if you would like to
        specify but it is recommended that you let Pika manage the channel
        numbers.

        :rtype: pika.adapters.blocking_connection.BlockingChannel
        """
        return self.blocking_connection.channel(channel_number=channel_number)


if __name__ == "__main__":
    con = Connection.create(host="localhost")
    print(con._prev_connection_time)
    con.blocking_connection.close()
    chan = con.channel()
    print(con._prev_connection_time)

    class MockConnection(Connection):
        pass
