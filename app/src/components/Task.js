import React from 'react';

function Task(props) {
    return (
        <div className="task">
            <div className="task-name">{props.name}</div>
            <div className="task-status">{props.status}</div>
            {/* <div className="task-timestamp">{props.timestamp}</div> */}
            {/* <div className="task-command">
                <button className="btn btn-primary" name="start" onClick={props.sendCommand}>Start</button>
                <button className="btn btn-danger" name="stop" onClick={props.sendCommand}>Stop</button>
            </div> */}
        </div>
    );
}

export default Task;