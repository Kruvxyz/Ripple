import json
import os
import pika
import time
from typing import Any, Callable, Dict, Optional
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection


def get_connection() -> BlockingConnection:
    user = os.environ.get("RABBITMQ_USER")
    password = os.environ.get("RABBITMQ_PASS")
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters("rabbitmq", 5672, '/', credentials)
    for attempt in range(5):  # Retry up to 5 times
        try:
            connection = pika.BlockingConnection(parameters)
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    raise Exception("Failed to connect to RabbitMQ after 5 attempts")

def send_message(queue_name: str, message: str) -> None:
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(
        exchange='', 
        routing_key=queue_name, 
        body=json.dumps(message)
    )
    connection.close()

def receive_message_callback(
        queue_name: str, 
        callback: Callable[[Any, Any, Any, str], None]
    ) -> BlockingChannel:
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    # channel.start_consuming()
    return channel