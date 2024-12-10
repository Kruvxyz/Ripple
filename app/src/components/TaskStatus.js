import React from 'react';


function TaskStatus(props) {
    return (
        <div className={`task-status task-status_${props.status}`}>
            <div className="task-status">{props.status.charAt(0).toUpperCase()}</div>
        </div>
    );
}

export default TaskStatus;