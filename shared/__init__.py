import os
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
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
                logger.info("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            logger.info(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
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
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)  # Thread-safe session
    return Session()

def init_queue_db() -> None:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        Message.metadata.create_all(engine)
    finally:
        session.close()
        engine.dispose()

def get_latest_pending_command() -> Optional[Message]:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        logger.info("get_latest_pending_command : Getting latest pending command")
        message = session.query(Message).filter(Message.sender == "flask", Message.status == "pending").order_by(Message.timestamp.desc()).first()
        logger.info(f"get_latest_pending_command : Got latest message: {message}")
        return message
    except SQLAlchemyError as e:
        logger.error("get_latest_pending_command : SQLAlchemyError occurred:", e)
        session.rollback()
    finally:
        session.close()
        engine.dispose()
    return None

def update_command_status(
        message: Message, 
        new_status: str, 
        error: Optional[str] = None
    ) -> None:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        message = session.merge(message) 
        logger.info(f"update_command_status : Updating command status for {message.routine} to status: {new_status} and error {error}")
        message.status = new_status
        if error:
            message.error = error
        session.commit()
        logger.info(f"Updating {message.routine} with status {new_status} and error {error}")
    except SQLAlchemyError as e:
        logger.error("update_command_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"update_command_status : Error in updating command status for {message.routine} to status: {new_status} and error {error}: {e}")
    finally:
        session.close()
        engine.dispose()

def add_error_message(routine_name: str, error: str):
    engine = generate_engine()
    session = generate_session(engine)
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
        logger.error("add_error_message : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"add_error_message : Error in adding error message for {routine_name} with error: {e}")
    finally:
        session.close()
        engine.dispose()

def send_command(routine_name: str, command: str) -> bool:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        logger.info(f"sending command {command} for {routine_name} to queue")
        session.add(Message("flask", routine_name, command))
        session.commit()
        logger.info(f"sent command {command} for {routine_name} to queue")
        return True
    except Exception as e:
        logger.error(f"send_command : Error in sending command {command} for {routine_name} to queue: {e}") 
        session.rollback()
    except SQLAlchemyError as e:
        logger.error("send_command : SQLAlchemyError occurred:", e)
        session.rollback()
    finally:
        session.close()
        engine.dispose()
    return False

## Routine interface
def get_routine_list() -> List[str]:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        logger.info("get_routine_list : Getting routine list")
        messages = session.query(Message.routine).filter(Message.sender == "scheduler").distinct().all()
        logger.info(f"get_routine_list : Got routine list: {messages}")
        return [message[0] for message in messages]
    except SQLAlchemyError as e:
        logger.error("get_routine_list : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"get_routine_list : Error in getting routine list: {e}")
    finally:
        session.close()
        engine.dispose()
    return []

def get_routine_status(routine_name: str) -> Optional[str]:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        logger.info(f"get_routine_status : Getting status for {routine_name}")
        message = session.query(Message).filter(Message.sender == "scheduler", Message.routine == routine_name).order_by(Message.timestamp.desc()).first()
        logger.info(f"get_routine_status : Got status for {routine_name}: {message}")
        if message:
            return message.status
        return None
    except SQLAlchemyError as e:
        logger.error("get_routine_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"get_routine_status : Error in getting status for {routine_name}: {e}")
    finally:
        session.close()
        engine.dispose()
    return None

def update_routine_status(
        routine_name: str, 
        new_status: str, 
        error: Optional[str] = None
    ) -> bool:
    engine = generate_engine()
    session = generate_session(engine)
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
        logger.error("update_routine_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"update_routine_status : Error in updating status for {routine_name} to status: {new_status} and error {error}: {e}")
    finally:
        session.close()
        engine.dispose()
    return False

## Task interface
def get_tasks_id(routine_name: str, length: int = 1) -> List[int]:
    engine = generate_engine()
    session = generate_session(engine)
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
        logger.error("get_tasks_id : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"get_tasks_id : Error in getting task for {routine_name}: {e}")
    finally:
        session.close()
        engine.dispose()
    return []

def get_task(
        routine_name: str,
        task_id: int
) -> Optional[Message]: 
    engine = generate_engine()
    session = generate_session(engine)
    try:
        logger.info(f"get_task_status : Getting task status for {routine_name} and task {task_id}")
        message = session.query(Message).filter(
            Message.sender == "scheduler", 
            Message.routine == routine_name, 
            Message.command == "task",
            Message.response == str(task_id)
        ).order_by(Message.timestamp.desc()).limit(1).all()
        # ).order_by(Message.timestamp.desc()).first()
        logger.info(f"get_task_status : Got task status for {routine_name} and task {task_id}: {message}")
        # return message
        return message[0] if message else None
    except SQLAlchemyError as e:
        logger.error("get_task_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"get_task_status : Error in getting task status for {routine_name}: {e}")
    finally:
        session.close()
        engine.dispose()
    return None

def get_tasks(
        routine_name: str, 
        num_tasks: int = 5,
    ) -> Optional[List[Message]]:
    engine = generate_engine()
    session = generate_session(engine)
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
        logger.error("get_tasks_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"get_tasks_status : Error in getting task status for {routine_name}: {e}")
    finally:
        session.close()
        engine.dispose()
    return None

def get_task_status(
        routine_name: str, 
        num_tasks: int = 5,
    ) -> Optional[Message]:
    engine = generate_engine()
    session = generate_session(engine)
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
        logger.error("get_task_status : SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"get_task_status : Error in getting task status for {routine_name}: {e}")
    finally:
        session.close()
        engine.dispose()
    return None

def update_task_status(
        routine_name: str,
        task_id: int,
        new_status: str,
        error: Optional[str] = None
    ) -> bool:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        logger.info(f"update_task_status [{task_id}]: Updating task status for {routine_name} to {new_status}")
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
        logger.info(f"update_task_status [{task_id}]: Updating {routine_name} and task {task_id} with status {new_status} and error {error}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"update_task_status [{task_id}]: SQLAlchemyError occurred:", e)
        session.rollback()
    except Exception as e:
        logger.error(f"update_task_status [{task_id}]: Error in updating task status for {routine_name} to status: {new_status} and error {error}: {e}")
    finally:
        logger.info(f"update_task_status [{task_id}]: Closing session and disposing engine")
        session.close()
        engine.dispose()
    return False
