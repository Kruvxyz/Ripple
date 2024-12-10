import React from 'react';
import TasksContainer from './TasksContainer';


function StatusContainer(props) {
    return (
        <div className="status-container">
            <TasksContainer tasks={props.tasks} status={props.status} />
            <div className='routine-status'>{props.status}</div>
        </div>
    );
}

export default StatusContainer;