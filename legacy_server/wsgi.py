from dotenv import load_dotenv
import os
if not os.getenv("DONT_USE_DOT_ENV")==1:
    load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from db_init import init_db
from resources.db_connection import generate_engine, generate_session
from routines.stock_price import gen_stock_price_routine, gen_stock_recommendation_routine, gen_stock_daily_states_routine
from routines.zacks import gen_stock_of_the_day_routine
from RoutineManager import RoutineManager

app = Flask(__name__)
cors = CORS(app)


engine = generate_engine()
price_session = generate_session(engine)
daily_session = generate_session(engine)
recommendations_session = generate_session(engine)
zacks_session = generate_session(engine)

stock_price_routine = gen_stock_price_routine(price_session)
stock_daily_states = gen_stock_daily_states_routine(daily_session)
stock_recommendation_routine = gen_stock_recommendation_routine(recommendations_session)
stock_of_the_day = gen_stock_of_the_day_routine(zacks_session)

rm = RoutineManager()
rm.add_routine(stock_price_routine)
rm.add_routine(stock_daily_states)
rm.add_routine(stock_recommendation_routine)
rm.add_routine(stock_of_the_day)
init_db(engine)
rm.start()

# Initialize routine manager
# @app.before_request
# def create_tables():
#   pass


@app.route("/ping", methods=["GET", "POST"])
@cross_origin()
def ping():
    return "pong"

@app.route("/routine/status", methods=["POST"])
@cross_origin()
def routine_status():
    data = request.json
    routine_name = data.get("routine_name", None)
    if routine_name is None:
        return jsonify({"message": "Routine name not provided"})

    return jsonify({"routine": routine_name, "status": rm.get_routine_status(routine_name)})

@app.route("/routine/restart", methods=["POST"])
@cross_origin()
def restart_routine():
    data = request.json
    routine_name = data.get("routine_name", None)
    if routine_name is None:
        return jsonify({"message": "Routine name not provided"})

    rm.restart_routine(routine_name)
    return jsonify({"routine": routine_name, "status": rm.get_routine_status(routine_name)})

@app.route("/routine/stop", methods=["POST"])
@cross_origin()
def stop_routine():
    data = request.json
    routine_name = data.get("routine_name", None)
    if routine_name is None:
        return jsonify({"message": "Routine name not provided"})

    rm.stop_routine(routine_name)
    return jsonify({"routine": routine_name})

@app.route("/routine/all", methods=["POST"])
@cross_origin()
def all_routines():
    return jsonify({"routines": [routine.name for routine in rm.routines]})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
