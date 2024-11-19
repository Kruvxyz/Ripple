import os
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, exc, Engine, distinct, func, cast, Integer
from typing import List, Optional
from .models import Message


logger = logging.getLogger(__name__)

def connect_with_retry(db_url, retries=5, delay=2):
    for i in range(retries):
        try:
            engine = create_engine(db_url)
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")


def generate_engine(retries=5, delay=2):
    MYSQL_USER = os.environ.get("MYSQL_REMOTE_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_REMOTE_PASSWORD")
    MYSQL_HOST = os.environ.get("MYSQL_REMOTE_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_REMOTE_DATABASE")
    connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    logger.info(f"Connecting to database with connection string: {connection_string}")

    for i in range(retries):
        try:
            engine = create_engine(connection_string, echo=True, isolation_level="READ COMMITTED")
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")

def generate_session(engine: Engine):
    return sessionmaker(bind=engine)()

engine = generate_engine()
session = generate_session(engine)

def init_queue_db() -> None:
    Message.metadata.create_all(engine)

# def get_latest_message() -> Message:
#     return session.query(Message).filter(Message.sender == "flask").order_by(Message.timestamp.desc()).first()

def get_latest_pending_command() -> Optional[Message]:
    try:
        logger.info("get_latest_pending_command : Getting latest pending command")
        message = session.query(Message).filter(Message.sender == "flask", Message.status == "pending").order_by(Message.timestamp.desc()).first()
        logger.info(f"get_latest_pending_command : Got latest message: {message}")
        return message

    except SQLAlchemyError as e:
        # Catch OperationalError and rollback to reset the session
        logger.error("get_latest_pending_command : SQLAlchemyError occurred:", e)
        session.rollback()

    return None

def update_command_status(
        message: Message, 
        new_status: str, 
        error: Optional[str] = None
    ) -> None:
    try:
        logger.info(f"update_command_status : Updating command status for {message.routine} to status: {new_status} and error {error}")
        message.status = new_status
        if error:
            message.error = error
        session.commit()
        logger.info(f"Updating {message.routine} with status {new_status} and error {error}")
    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("update_command_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"update_command_status : Error in updating command status for {message.routine} to status: {new_status} and error {error}: {e}")

def add_error_message(routine_name: str, error: str):
    try:
        logger.info(f"add_error_message : Adding error message for {routine_name} with error: {error}")
        message = Message(
            sender="scheduler", 
            routine=routine_name,
            command="status",
            status="error",
            error=error
            )
        session.add(message)
        session.commit()
        logger.info(f"add_error_message : Added error message for {routine_name} with error: {error}")
    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("add_error_message : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"add_error_message : Error in adding error message for {routine_name} with error: {e}")

## Routine interface
def get_routine_list() -> List[str]:
    try:
        logger.info("get_routine_list : Getting routine list")
        messages = session.query(Message.routine).filter(Message.sender == "scheduler").distinct().all()
        logger.info(f"get_routine_list : Got routine list: {messages}")
        return [message[0] for message in messages]

    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("get_routine_list : SQLAlchemyError occurred:", e)
        session.rollback()

    except Exception as e:
        logger.error(f"get_routine_list : Error in getting routine list: {e}")
    
    return []    


def get_routine_status(routine_name: str) -> Optional[str]:
    try:
        logger.info(f"get_routine_status : Getting status for {routine_name}")
        message = session.query(Message).filter(Message.sender == "scheduler", Message.routine == routine_name).order_by(Message.timestamp.desc()).first()
        logger.info(f"get_routine_status : Got status for {routine_name}: {message}")
        if message:
            return message.status
        return None

    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("get_routine_status : SQLAlchemyError occurred:", e)
        session.rollback()

    except Exception as e:
        logger.error(f"get_routine_status : Error in getting status for {routine_name}: {e}")
    
    return None

def update_routine_status(
        routine_name: str, 
        new_status: str, 
        error: Optional[str] = None
    ) -> bool:
    # message = session.query(Message).filter(Message.sender == "flask", Message.routine == routine).order_by(Message.timestamp.desc()).first()
    try:    
        logger.info(f"update_routine_status : Updating routine status for {routine_name} to {new_status}")
        message = Message(
            sender="scheduler", 
            routine=routine_name,
            command="status",
            status=new_status
            )
        if error:
            message.error = error
        session.add(message)
        session.commit()
        logger.info(f"Updating {routine_name} with status {new_status} and error {error}")
        return True
    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("update_routine_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"update_routine_status : Error in updating status for {routine_name} to status: {new_status} and error {error}: {e}")
    return False

## Task interface
def get_tasks_id(routine_name: str, length: int = 1) -> List[int]:
    try:
        logger.info(f"get_tasks_id : Getting task for {routine_name}")
        ids = session.query(
            distinct(cast(Message.response, Integer))
        ).filter(
            Message.sender == "scheduler",
            Message.routine == routine_name, 
            Message.command == "task"
        ).order_by(cast(Message.response, Integer).desc()).limit(length).all()
        logger.info(f"get_tasks_id : Got task for {routine_name}: {ids}")
        return [id[0] for id in ids]

    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("get_tasks_id : SQLAlchemyError occurred:", e)
        session.rollback()

    except Exception as e:
        logger.error(f"get_tasks_id : Error in getting task for {routine_name}: {e}")
    
    return None

def get_task(
        routine_name: str,
        task_id: int
) -> Optional[Message]: 
    try:
        logger.info(f"get_task_status : Getting task status for {routine_name} and task {task_id}")
        message = session.query(Message).filter(
            Message.sender == "scheduler", 
            Message.routine == routine_name, 
            Message.command == "task",
            Message.response == str(task_id)
        ).order_by(Message.timestamp.desc()).first()
        logger.info(f"get_task_status : Got task status for {routine_name} and task {task_id}: {message}")
        return message

    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("get_task_status : SQLAlchemyError occurred:", e)
        session.rollback()

    except Exception as e:
        logger.error(f"get_task_status : Error in getting task status for {routine_name}: {e}")
    
    return None

def get_tasks(
        routine_name: str, 
        num_tasks: int = 5,
    ) -> Optional[List[Message]]:        
    tasks_ids = get_tasks_id(routine_name, num_tasks)
    try:
        output = []
        logger.info(f"get_tasks_status : Getting task status for {routine_name} and task {tasks_ids}")
        for task_id in tasks_ids:
            message = get_task(routine_name, task_id)
            logger.info(f"get_tasks_status : Got task status for {routine_name} and task {task_id}: {message}")
            if message:
                output.append(message)
        return output
    
    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("get_tasks_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        # logger.error(f"get_tasks_status : Error in updating task status for {routine_name} to status: {new_status} and error {error}: {e}")
        logger.error(f"get_tasks_status : Error in getting task status for {routine_name}: {e}")
    
    return None

def get_task_status(
        routine_name: str, 
        num_tasks: int = 5,
    ) -> Optional[Message]:        
    tasks_ids = get_tasks_id(routine_name, num_tasks)
    if not tasks_ids:
        logger.info(f"get_task_status : No tasks found for {routine_name}")
        return None
    try:
        logger.info(f"get_task_status : Getting task status for {routine_name} and task {tasks_ids}")
        output = []
        for task_id in tasks_ids:
            message = get_task(routine_name, task_id)
            logger.info(f"get_task_status : Got task status for {routine_name} and task {task_id}: {message}")
            if message:
                output.append((task_id, message.status))
        return output
    
    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("get_task_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        # logger.error(f"get_task_status : Error in updating task status for {routine_name} to status: {new_status} and error {error}: {e}")
        logger.error(f"get_task_status : Error in getting task status for {routine_name}: {e}")
    return None
    
        
def update_task_status(
        routine_name: str,
        task_id: int,
        new_status: str,
        error: Optional[str] = None
    ) -> bool:
    try:
        logger.info(f"update_task_status : Updating task status for {routine_name} to {new_status}")
        message = Message(
            sender="scheduler", 
            routine=routine_name,
            command="task",
            status=new_status,
            response=str(task_id)
        )
        if error:
            message.error = error
        session.add(message)
        session.commit()
        logger.info(f"Updating {routine_name} and task {task_id} with status {new_status} and error {error}")
        return True
    except SQLAlchemyError as e:
        # Catch SQLAlchemyError and rollback to reset the session
        logger.error("update_task_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"update_task_status : Error in updating task status for {routine_name} to status: {new_status} and error {error}: {e}")
    return False
