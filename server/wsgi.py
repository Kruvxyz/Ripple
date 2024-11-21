from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import logging
from shared import send_command, Message, get_latest_pending_command, update_command_status, get_routine_status, get_routine_list, get_tasks, get_task_status
import sys

# Set logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
    )

logger = logging.getLogger(__name__)

# Set flask app and cors
app = Flask(__name__)
cors = CORS(app)

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
    valid_commands = ["start", "cancel"] #, "execute"]
    if data.get("command","None") not in valid_commands:
        return jsonify({
            "status": "error",
            "error": "Invalid command"
        })
    
    # Validate the routine

    # Add the command to the queue
    res = send_command(data.get("routine_name", "None"), data.get("command", "None"))
    if res:
        return jsonify({
            "status": "ok"
        })
    else:
        return jsonify({
            "status": "error",
            "error": "Failed to send command"
        })

@app.route("/routine/get_command", methods=["POST"])
@cross_origin(origins="http://localhost")
def get_command():
    try:
        logger.info("Getting latest message")
        # message = session.query(Message).filter(Message.sender == "flask").order_by(Message.timestamp.desc()).first()
        message = get_latest_pending_command()
        if message is None:
            return jsonify({
                "status": "error",
                "error": "no pending command"
            })
        # session.delete(message)
        # session.commit()
        # update_command_status(message, "executing")
        return jsonify({
            "routine": message.routine, 
            "command": message.command,
            "status": message.status,
            })
    except Exception as e:
        logger.error(e)
        return jsonify({
            "status": "error",
            "error": str(e)
        })
    
@app.route("/routine/list", methods=["POST"])
@cross_origin(origins="http://localhost")
def routine_list():
    try:
        return jsonify({"list": get_routine_list(),
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
    tasks = get_tasks(routine_name)
    logger.info(f"Getting status for routine {routine_name} with {num_tasks} tasks: {tasks}")
    return jsonify({
        "status": get_routine_status(routine_name),
        "tasks": [{
            "name": message.response,
            "status": message.status
        } for message in tasks],
    })

# Run server if the script is run directly
if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5050, debug=True)