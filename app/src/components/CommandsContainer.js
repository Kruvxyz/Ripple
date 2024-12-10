import React from 'react';


function CommandsContainer(props) {
    return (
        <div className="commands-container">
            <i onClick={props.sendCommand} name="cancel" className="bi bi-pause-circle-fill command-icon"></i>
            <i onClick={props.sendCommand} name="start" className="bi bi-play-circle-fill command-icon"></i>
        </div>
    );
}

export default CommandsContainer;