import React, {useState, useEffect} from 'react';
import Task from './Task';
import 'bootstrap-icons/font/bootstrap-icons.css';

function Routine(props) {
    const [status, setStatus] = useState("");
    const [tasks, setTasks] = useState([]);

    let requestStatus = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            routine_name: props.name
        })
    }

    const requestCommand = (command) => {
        console.log(command);

        return {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                routine_name: props.name,
                command: command
            })
        }
    };

    const sendCommand = (event) => {
        console.log(event.target.getAttribute('name'));

        fetch(`${process.env.REACT_APP_SERVER_ADDRESS}/routine/command`, requestCommand(event.target.getAttribute('name')))
        .then(response => response.json())
        .then(response => {
            console.log(response)
        }).catch(err=>console.log(err));
    }

    const updateStatus = () => {
        fetch(`${process.env.REACT_APP_SERVER_ADDRESS}/routine/status`, requestStatus)
        .then(response => response.json())
        .then(response => {
            console.log(response)
            setStatus(response.status);
            setTasks(response.tasks);
        }).catch(err=>console.log(err));
    }
    useEffect(()=>{
        const id = setInterval(() => {
            updateStatus();
        }, 30000);
        return () => clearInterval(id);

    },[]);

    useEffect(()=>{
        updateStatus();
    },[]);


    return (
        <div className='routine'>
            <h1 className='routine-header'>{props.name}</h1>
            <p>{props.description}</p>
            <div className='routine-status'>{status}</div>
            <div className='routine-tasks'>{tasks && tasks.map((task)=><Task name={task.name} status={task.status} />)}</div>
            <i onClick={sendCommand} name="cancel" className="bi bi-pause-circle-fill"></i>
            <i onClick={sendCommand} name="start" className="bi bi-play-circle-fill"></i>
        </div>
    );
}

export default Routine;