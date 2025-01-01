import json
import logging
import os
import pika
import time
from typing import Any, Dict, Optional
from pika.adapters.blocking_connection import BlockingConnection

logger = logging.getLogger(__name__)

def get_connection() -> BlockingConnection:
    user = os.environ.get("RABBITMQ_USER")
    password = os.environ.get("RABBITMQ_PASS")
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters("rabbitmq", 5672, '/', credentials)
    for attempt in range(5):  # Retry up to 5 times
        try:
            logger.debug(f"Attempting to connect to RabbitMQ, attempt {attempt + 1}")
            connection = pika.BlockingConnection(parameters)
            logger.debug("Connection to RabbitMQ established")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.debug(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    logger.error("Failed to connect to RabbitMQ after 5 attempts")
    raise Exception("Failed to connect to RabbitMQ after 5 attempts")

def send_message(queue_name: str, message: str) -> None:
    logger.debug(f"Sending message to queue {queue_name}: {message}")
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(
        exchange='', 
        routing_key=queue_name, 
        body=json.dumps(message)
    )
    connection.close()
    logger.debug(f"Message sent to queue {queue_name}")

def receive_message(queue_name: str) -> Optional[Dict[str,Any]]:
    logger.debug(f"Receiving message from queue {queue_name}")
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    method_frame, _header_frame, body = channel.basic_get(queue=queue_name, auto_ack=False)
    def ack_message():
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
    return json.loads(body) if body else None, ack_message
