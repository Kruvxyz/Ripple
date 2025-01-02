from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import logging
import threading
from logic import send_message_to_scheduler, handle_message, Logic 
from rabbitMQ import receive_message_callback
import sys

# Set logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
    )

logger = logging.getLogger(__name__)

# Set rabbitMQ callback
channel = receive_message_callback("status_updates", handle_message)
receive_messages_thread = threading.Thread(target=channel.start_consuming)
receive_messages_thread.start()

# Set flask app and cors
app = Flask(__name__)
cors = CORS(app)

logic = Logic()

@app.route("/ping", methods=["GET", "POST"])
@cross_origin(origins="http://localhost")
def ping():
    return "pong"

@app.route("/routine/command", methods=["POST"])
@cross_origin(origins="http://localhost")
def routine_command():
    data = request.json
    logger.info(f"Received command: {data}")

    # Validate the command
    valid_commands = ["start", "cancel", "execute"]
    if data.get("command","None") not in valid_commands:
        return jsonify({
            "status": "error",
            "error": "Invalid command"
        })
    
    # Validate the routine
    if data.get("routine_name", None) not in logic.get_routines_list():
        return jsonify({
            "status": "error",
            "error": "Invalid routine"
        })
    
    # send command to the queue
    try:
        res = send_message_to_scheduler(data.get("command", "None"), data.get("routine_name", "None"))
        return jsonify({
            "status": "ok"
        })
    except Exception as e:
        logger.error(e)
        return jsonify({
            "status": "error",
            "error": str(e)
        })

# @app.route("/routine/get_command", methods=["POST"])
# @cross_origin(origins="http://localhost")
# def get_command():
#     try:
#         logger.info("Getting latest message")
#         # message = session.query(Message).filter(Message.sender == "flask").order_by(Message.timestamp.desc()).first()
#         message = get_latest_pending_command()
#         if message is None:
#             return jsonify({
#                 "status": "error",
#                 "error": "no pending command"
#             })
#         # session.delete(message)
#         # session.commit()
#         # update_command_status(message, "executing")
#         return jsonify({
#             "routine": message.routine, 
#             "command": message.command,
#             "status": message.status,
#             })
#     except Exception as e:
#         logger.error(e)
#         return jsonify({
#             "status": "error",
#             "error": str(e)
#         })
    
@app.route("/routine/list", methods=["POST"])
@cross_origin(origins="http://localhost")
def routine_list():
    try:
        return jsonify({"list": logic.get_routines_list(),
                    "status": "ok"})
    except Exception as e:
        logger.error(e)
        return jsonify({"status": "error",
                        "error": str(e)})


@app.route("/routine/status", methods=["POST"])
@cross_origin(origins="http://localhost")
def routine_status():
    num_tasks = request.json.get("num_tasks", 5)
    routine_name = request.json.get("routine_name","")
    routine_state = logic.get_state(routine_name)

    tasks = routine_state.get("tasks", {})
    logger.info(f"Getting status for routine {routine_name} with {num_tasks} tasks: {tasks}")
    sorted_tasks_list = [{
            "name": task,
            "status": tasks.get(task, {}).get("status", None),
        } for task in tasks]
    sorted_tasks_list.sort(key=lambda x: x["name"], reverse=True)
    return jsonify({
        "status": routine_state.get("status", None),
        "tasks": sorted_tasks_list,
    })

# Run server if the script is run directly
if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5050, debug=True)