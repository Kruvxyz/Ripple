import React from 'react';
import TaskElement from './TaskElement';

function TasksContainer(props) {
    let last_task = props.tasks[0];
    console.log(last_task);
    return (
        <div className='tasks-container'>
            {props.tasks && props.tasks.slice(1).map((task)=><TaskElement name={task.name} status={task.status} arrow={true} />)}
            {last_task && <TaskElement name={last_task.name} status={last_task.status} />}
        </div>
    );
}

export default TasksContainer;