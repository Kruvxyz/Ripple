import React, {useState, useEffect} from 'react';
import './App.css';
import Menu from './Menu';
import Container from './Container';
import Routine from './Routine';


function App() {

  const [routineList, setRoutineList] = useState([]);
  let requestList = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
  }

  const getList = () => {
    fetch(`${process.env.REACT_APP_SERVER_ADDRESS}/routine/list`, requestList)
    .then(response => response.json())
    .then(response => {
      console.log(response)
      if (response.status == 'ok') {
        setRoutineList(response.list);
      }
      else {
        console.log("Error getting routine list");
      }
    }).catch(err=>console.log(err));
  }

  useEffect(()=>{
    getList();
  },[]);


  return (
    <div className="App">
      <Menu name='Breakfast Menu' description='This is the breakfast menu' status='active' />
      <Container routines={routineList} />
    </div>
  );
}

export default App;
