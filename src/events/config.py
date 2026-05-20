"""RabbitMQ configuration."""

import os


class RabbitMQConfig:
    """RabbitMQ configuration from environment variables."""
    
    HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    USERNAME: str = os.getenv("RABBITMQ_USERNAME", "guest")
    PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    VHOST: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # Exchange configuration
    EXCHANGE_NAME: str = "email_events"
    EXCHANGE_TYPE: str = "topic"
    
    # Queue names
    NOTIFICATIONS_QUEUE: str = "notifications_queue"
    ANALYTICS_QUEUE: str = "analytics_queue"
    AUDIT_QUEUE: str = "audit_queue"
    
    # Routing keys
    ROUTING_USER_CREATED: str = "user.created"
    ROUTING_FOLDER_CREATED: str = "folder.created"
    ROUTING_MESSAGE_CREATED: str = "message.created"
    
    @classmethod
    def get_url(cls) -> str:
        """Get RabbitMQ connection URL."""
        return f"amqp://{cls.USERNAME}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.VHOST}"
