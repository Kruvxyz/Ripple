import React from 'react';
import Routine from './Routine';

const Container = (props) => {
    return (
        <div className="container">
            {props.routines.map((routine, index) => {
                    return <Routine name={routine} key={index} description='' />
                }
            )}
        </div>
    );
};

export default Container;
