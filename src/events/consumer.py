"""RabbitMQ Event Consumer example."""

import json
import logging
from typing import Callable, Dict, Any
import pika

from .config import RabbitMQConfig
from .events import Event

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes events from RabbitMQ."""
    
    def __init__(self, queue_name: str, routing_keys: list[str]):
        """
        Initialize consumer.
        
        Args:
            queue_name: Name of the queue to consume from
            routing_keys: List of routing keys to bind
        """
        self.queue_name = queue_name
        self.routing_keys = routing_keys
        self._connection: pika.BlockingConnection = None
        self._channel = None
        self._handlers: Dict[str, Callable] = {}
        self._setup()
    
    def _setup(self):
        """Set up RabbitMQ connection, exchange, and queue."""
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
            
            # Declare exchange
            self._channel.exchange_declare(
                exchange=RabbitMQConfig.EXCHANGE_NAME,
                exchange_type=RabbitMQConfig.EXCHANGE_TYPE,
                durable=True,
            )
            
            # Declare queue
            self._channel.queue_declare(
                queue=self.queue_name,
                durable=True,
            )
            
            # Bind queue to exchange with routing keys
            for routing_key in self.routing_keys:
                self._channel.queue_bind(
                    exchange=RabbitMQConfig.EXCHANGE_NAME,
                    queue=self.queue_name,
                    routing_key=routing_key,
                )
            
            logger.info(f"Consumer setup complete for queue '{self.queue_name}'")
            
        except Exception as e:
            logger.error(f"Failed to setup consumer: {e}")
            self._connection = None
            self._channel = None
    
    def register_handler(self, event_type: str, handler: Callable[[Event], None]):
        """Register a handler for a specific event type."""
        self._handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
    
    def _process_message(self, channel, method, properties, body):
        """Process incoming message."""
        try:
            message = json.loads(body.decode("utf-8"))
            event_type = message.get("event_type")
            
            logger.info(f"Received event: {event_type}")
            
            # Create event object from message
            event = Event(
                event_id=message.get("event_id"),
                event_type=event_type,
                timestamp=message.get("timestamp"),
                aggregate_id=message.get("aggregate_id"),
                payload=message.get("payload", {}),
                metadata=message.get("metadata", {}),
            )
            
            # Call registered handler
            if event_type in self._handlers:
                self._handlers[event_type](event)
            else:
                logger.warning(f"No handler registered for event type: {event_type}")
            
            # Acknowledge message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Processed event: {event_type}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Negative acknowledge - requeue the message
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages."""
        if not self._channel:
            logger.error("Cannot start consuming: not connected")
            return
        
        # Set QoS to 1 (process one message at a time)
        self._channel.basic_qos(prefetch_count=1)
        
        # Set up consumer
        self._channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._process_message,
        )
        
        logger.info(f"Starting to consume from queue '{self.queue_name}'...")
        self._channel.start_consuming()
    
    def stop_consuming(self):
        """Stop consuming messages."""
        if self._channel and self._channel.is_open:
            self._channel.stop_consuming()
            logger.info("Stopped consuming")
    
    def close(self):
        """Close the connection."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("Consumer connection closed")


# Example handlers
def handle_user_created(event: Event):
    """Example handler for UserCreated event."""
    payload = event.payload
    logger.info(f"🎉 New user registered: {payload.get('login')} (ID: {payload.get('id')})")
    # Here you would send a welcome email, etc.


def handle_folder_created(event: Event):
    """Example handler for FolderCreated event."""
    payload = event.payload
    logger.info(f"📁 New folder created: {payload.get('name')} (ID: {payload.get('id')})")
    # Here you would update search index, etc.


def handle_message_created(event: Event):
    """Example handler for MessageCreated event."""
    payload = event.payload
    logger.info(
        f"📧 New message: '{payload.get('subject')}' "
        f"from {payload.get('sender')} to {payload.get('recipient')}"
    )
    # Here you would send notification to recipient, etc.


def handle_analytics(event: Event):
    """Generic handler for analytics - processes all events."""
    logger.info(f"📊 Analytics event: {event.event_type} - {event.aggregate_id}")
    # Here you would send to analytics service, update metrics, etc.


def handle_audit(event: Event):
    """Generic handler for audit logging - processes all events."""
    logger.info(f"🔒 Audit log: {event.event_type} at {event.timestamp}")
    # Here you would write to audit log storage


# Factory functions
def create_notifications_consumer() -> EventConsumer:
    """Create consumer for notification events."""
    consumer = EventConsumer(
        queue_name=RabbitMQConfig.NOTIFICATIONS_QUEUE,
        routing_keys=[
            RabbitMQConfig.ROUTING_USER_CREATED,
            RabbitMQConfig.ROUTING_MESSAGE_CREATED,
        ],
    )
    consumer.register_handler("UserCreated", handle_user_created)
    consumer.register_handler("MessageCreated", handle_message_created)
    return consumer


def create_analytics_consumer() -> EventConsumer:
    """Create consumer for analytics events (all events)."""
    consumer = EventConsumer(
        queue_name=RabbitMQConfig.ANALYTICS_QUEUE,
        routing_keys=["#"],  # All events
    )
    consumer.register_handler("UserCreated", handle_analytics)
    consumer.register_handler("FolderCreated", handle_analytics)
    consumer.register_handler("MessageCreated", handle_analytics)
    return consumer


def create_audit_consumer() -> EventConsumer:
    """Create consumer for audit logging (all events)."""
    consumer = EventConsumer(
        queue_name=RabbitMQConfig.AUDIT_QUEUE,
        routing_keys=["#"],  # All events
    )
    consumer.register_handler("UserCreated", handle_audit)
    consumer.register_handler("FolderCreated", handle_audit)
    consumer.register_handler("MessageCreated", handle_audit)
    return consumer
