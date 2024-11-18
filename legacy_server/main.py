from db_init import init_db
from resources.db_connection import generate_engine, generate_session
from routines import gen_stock_price_routine
from RoutineManager import RoutineManager


engine = generate_engine()
init_db(engine)

session = generate_session(engine)

stock_price_routine = gen_stock_price_routine(session)
rm = RoutineManager()
rm.add_routine(stock_price_routine)

