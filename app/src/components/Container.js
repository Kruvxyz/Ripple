import React from 'react';
import Routine from './Routine';

const Container = (props) => {
    return (
        <div className="container">
            {props.routines.map((routine, index) => {
                    return <Routine name={routine} key={index} description='This is my morning routine' />
                }
            )}
        </div>
    );
};

export default Container;
