import React, {useState, useEffect} from 'react';
import 'bootstrap-icons/font/bootstrap-icons.css';
import RoutineTitle from './RoutineTitle';
import CommandsContainer from './CommandsContainer';
import StatusContainer from './StatusContainer';

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

        fetch(`${process.env.REACT_APP_BE_ADDRESS}/routine/command`, requestCommand(event.target.getAttribute('name')))
        .then(response => response.json())
        .then(response => {
            console.log(response)
        }).catch(err=>console.log(err));
    }

    const updateStatus = () => {
        fetch(`${process.env.REACT_APP_BE_ADDRESS}/routine/status`, requestStatus)
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
        }, 5000);
        return () => clearInterval(id);

    },[]);

    useEffect(()=>{
        updateStatus();
    },[]);


    return (
        <div className='routine'>
            <RoutineTitle name={props.name} />
            <StatusContainer status={status} tasks={tasks}/>
            <CommandsContainer sendCommand={sendCommand} />
        </div>
    );
}

export default Routine;