from collections.abc import Callable
from datetime import datetime
import os
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy import create_engine, exc, Engine
from typing import Optional, Tuple
from RoutineManager.Status import RoutineStatus, TaskInstanceStatus 
from .models import Routine, Task


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
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
    connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    print(f"Connecting to database with connection string: {connection_string}")
    logger.info(f"Connecting to database with connection string: {connection_string}")

    for i in range(retries):
        try:
            engine = create_engine(connection_string, echo=True)
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")

def generate_session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()

def init_db() -> None:
    engine = generate_engine()
    Routine.metadata.create_all(engine)
    Task.metadata.create_all(engine)
    engine.dispose()

def get_routine(name: str) -> Optional[Routine]:
    engine = generate_engine()
    routine_session = generate_session(engine)
    try:
        logger.info(f"Getting routine with name: {name}")
        return routine_session.query(Routine).filter(Routine.name == name).first()
    except SQLAlchemyError as e:
        logger.error("get routine - SQLAlchemyError occurred:", e)
        routine_session.rollback()
    except Exception as e:
        logger.error("get routine - Error occurred:", e)
    finally:
        routine_session.close()
    return None

def add_routine(name: str, description: str, condition_function: Optional[str]=None, condition_function_args: Optional[str]=None, retry_delay: int=5*60, retry_limit: int=5) -> Routine:
    engine = generate_engine()
    routine_session = generate_session(engine)
    try:
        routine = Routine(name=name, description=description, condition_function=condition_function, condition_function_args=condition_function_args, retry_delay=retry_delay, retry_limit=retry_limit)
        routine_session.add(routine)
        routine_session.commit()
        return routine
    except SQLAlchemyError as e:
        logger.error("add routine - SQLAlchemyError occurred:", e)
        routine_session.rollback()
    except Exception as e:
        logger.error("add routine - Error occurred:", e)
    finally:
        routine_session.close()
    return None

def gen_routine_handlers(routine_name: str) -> Tuple[
    Session,
    Callable[[str, str, Optional[str], Optional[str], int, int], Routine],
    Callable[[str], None],
    Callable[[str], None],
    Callable[[], Optional[Task]],
    Callable[[Task], Tuple[Callable[[str], None], Callable[[str], None], Callable[[], None]]]   
]:
    """
    This function creates handlers to access and manage the database for a specific routine.
    It generates functions to get, create, update status, update error, create new tasks, 
    and update task details for the specified routine.
    """
    engine = generate_engine()
    session = generate_session(engine)

    def get_routine() -> Optional[Routine]:
        try:
            logger.info(f"Getting routine with name: {routine_name}")
            return session.query(Routine).filter(Routine.name == routine_name).first()
        except SQLAlchemyError as e:
            logger.error("get routine - SQLAlchemyError occurred:", e)
            session.rollback()
        except Exception as e:
            logger.error("get routine - Error occurred:", e)
        return None
        
    def gen_routine(
            description: str="", 
            retry_delay: int=5*60, 
            retry_limit: int=5
        ) -> Routine:
        routine = get_routine()
        if routine is None:
            routine = Routine(
                name=routine_name, 
                description=description, 
                retry_delay=retry_delay, 
                retry_limit=retry_limit
            )
            session.add(routine)
            session.commit()
        return routine
    
    def update_status(status: str) -> None:
        try:
            logger.info(f"update_status: Updating status of {routine_name} to {status}")
            routine = get_routine()
            logger.info(f"update_status: Updating status | Routine: {routine} with status {routine.status}")
            routine.status = status
            routine.error = ""
            routine.updated_at = datetime.now()
            session.commit()
            logger.info(f"update_status | Updated status of {routine_name} to {status}")
        except SQLAlchemyError as e:
            logger.error("update_status | SQLAlchemyError occurred:", e)
            session.rollback()
        except Exception as e:
            logger.error("update_status | Error occurred:", e)

    def update_error(error: str) -> None:
        try:  
            logger.info(f"update_error: Updating error of {routine_name} to {error}")
            routine = get_routine()
            logger.info(f"update_error: Updating error | Routine: {routine} with status {routine.status} and error {routine.error}")
            routine.status = RoutineStatus.ERROR
            routine.error = error
            routine.updated_at = datetime.now()
            session.commit()
            logger.info(f"update_error | Updated error of {routine_name} to {error}")
        except SQLAlchemyError as e:
            logger.error("update_error | SQLAlchemyError occurred:", e)
            session.rollback()
        except Exception as e:
            logger.error("update_error | Error occurred:", e)

    def create_new_task() -> Optional[Task]:
        try:
            logger.info(f"create_new_task: Creating new task for {routine_name}")
            routine = get_routine()
            logger.info(f"create_new_task: Creating new task | Routine: {routine} with status {routine.status}")
            task = Task(routine=routine)
            session.add(task)
            session.commit()
            logger.info(f"create_new_task | Created new task for {routine_name}")
            return task
        except SQLAlchemyError as e:
            logger.error("create_new_task | SQLAlchemyError occurred:", e)
            session.rollback()
        except Exception as e: 
            logger.error("create_new_task | Error occurred:", e)
        return None
    
    def gen_update_task(task: Task):
        def update_task_status(status: str) -> None:
            try:
                logger.info(f"update_task_status: Updating status of task {task.id} to {status}")
                task.updated_at = datetime.now()
                task.status = status
                session.commit()
                logger.info(f"update_task_status | Updated status of task {task.id} to {status}")
            except SQLAlchemyError as e:
                logger.error("update_task_status | SQLAlchemyError occurred:", e)
                session.rollback()
            except Exception as e:
                logger.error("update_task_status | Error occurred:", e)

        def update_task_error(error: str) -> None:
            try:
                logger.info(f"update_task_error: Updating error of task {task.id} to {error}")
                task.updated_at = datetime.now()
                task.error = error
                task.status = TaskInstanceStatus.ERROR
                session.commit()
                logger.info(f"update_task_error | Updated error of task {task.id} to {error}")
            except SQLAlchemyError as e:
                logger.error("update_task_error | SQLAlchemyError occurred:", e)
                session.rollback()
            except Exception as e:
                logger.error("update_task_error | Error occurred:", e)

        def update_task_completed() -> None:
            try:
                logger.info(f"update_task_completed: Updating task {task.id} to completed")
                task.updated_at = datetime.now()
                task.completed_at = datetime.now()
                task.status = TaskInstanceStatus.DONE
                session.commit()
                logger.info(f"update_task_completed | Updated task {task.id} to completed")
            except SQLAlchemyError as e:
                logger.error("update_task_completed | SQLAlchemyError occurred:", e)
                session.rollback()
            except Exception as e:
                logger.error("update_task_completed | Error occurred:", e)

        return update_task_status, update_task_error, update_task_completed

    return session, gen_routine, update_status, update_error, create_new_task, gen_update_task
