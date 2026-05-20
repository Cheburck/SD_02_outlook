"""RabbitMQ Event Publisher."""

import json
import logging
from typing import Optional
import pika

from .events import Event
from .config import RabbitMQConfig

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes events to RabbitMQ."""
    
    def __init__(self):
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel = None
        self._setup()
    
    def _setup(self):
        """Set up RabbitMQ connection and declare exchange."""
        try:
            credentials = pika.PlainCredentials(
                RabbitMQConfig.USERNAME,
                RabbitMQConfig.PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=RabbitMQConfig.HOST,
                port=RabbitMQConfig.PORT,
                virtual_host=RabbitMQConfig.VHOST,
                credentials=credentials,
            )
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            
            # Declare topic exchange
            self._channel.exchange_declare(
                exchange=RabbitMQConfig.EXCHANGE_NAME,
                exchange_type=RabbitMQConfig.EXCHANGE_TYPE,
                durable=True,
            )
            
            logger.info(f"Connected to RabbitMQ at {RabbitMQConfig.HOST}:{RabbitMQConfig.PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._connection = None
            self._channel = None
    
    def publish(self, event: Event, routing_key: str) -> bool:
        """
        Publish an event to the exchange.
        
        Args:
            event: The event to publish
            routing_key: The routing key for the event
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self._channel:
            logger.warning("Cannot publish: not connected to RabbitMQ")
            return False
        
        try:
            message_body = json.dumps(event.to_dict()).encode("utf-8")
            
            properties = pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # Persistent message
                headers=event.metadata,
            )
            
            self._channel.basic_publish(
                exchange=RabbitMQConfig.EXCHANGE_NAME,
                routing_key=routing_key,
                body=message_body,
                properties=properties,
            )
            
            logger.info(f"Published event {event.event_type} with routing key '{routing_key}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            return False
    
    def close(self):
        """Close the connection."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("RabbitMQ connection closed")


# Global publisher instance
_publisher: Optional[EventPublisher] = None


def get_publisher() -> Optional[EventPublisher]:
    """Get or create the global event publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher


def init_publisher() -> Optional[EventPublisher]:
    """Initialize the global publisher (call at application startup)."""
    global _publisher
    _publisher = EventPublisher()
    return _publisher


def close_publisher():
    """Close the global publisher (call at application shutdown)."""
    global _publisher
    if _publisher:
        _publisher.close()
        _publisher = None
