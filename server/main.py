import asyncio
import logging
import sys
from flask import request, jsonify
from flask_cors import cross_origin
import threading
from RoutineManager.RoutineManager import RoutineManager

# Set logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
    )

logger = logging.getLogger(__name__)

# 1. Instantiate a queue
queue=asyncio.Queue()

# 2. Running RoutineManager in a separate thread
routine_manager = RoutineManager(queue=queue)
async def run_routine_manager(routine_manager):
    await routine_manager.run()
thread = threading.Thread(target=asyncio.run, args=(run_routine_manager(routine_manager),))
thread.start()

# 3. Running flask app on main thread with access to the queue
from wsgi import app


@app.route("/routine/command", methods=["POST"])
@cross_origin()
def put():
    """
    """
    data = request.json

    # Validate the command
    valid_commands = ["start", "stop", "pause", "resume", "restart"]
    if data["command"] not in valid_commands:
        return jsonify({
            "status": "error",
            "error": "Invalid command"
        })
    
    # Validate the routine
    # TODO: Add validation for routine

    # Add the command to the queue
    try:
        queue.put_nowait((data["routine"], data["command"]))
        return "ok"
    except asyncio.QueueFull:
        return "queue full"

# Should not be expose to user
@app.route("/routine/get", methods=["POST"])
@cross_origin()
def get():
    try:
        resp = queue.get_nowait()
        return jsonify({
            "routine": resp[0], 
            "command": resp[1],
            "status": "ok"
            })
    except asyncio.QueueEmpty:
        return jsonify({
            "status": "error",
            "error": "queue empty"
        })


@app.route("/routine/update", methods=["POST"])
@cross_origin()
def routine_update():
    return "routine_update"
    # data = request.json
    # routine_name = data.get("routine_name", None)
    # status = data.get("status", None)
    # if routine_name is None or status is None:
    #     return jsonify({"message": "Routine name or status not provided"})

    # return jsonify({"routine": routine_name, "status": rm.update_routine_status(routine_name, status)})

if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5050, debug=True)