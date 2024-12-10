import React from 'react';


function RoutineTitle(props) {
    return (
        <div className="routine-title">
            <h1>{props.name}</h1>
            <p>{props.description}</p>
        </div>
    );
}

export default RoutineTitle;