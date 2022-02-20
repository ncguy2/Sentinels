
import React from 'react';
import logo from './logo.svg';
import './App.css';
import DeckList from "./components/DeckList";
import CardList from "./components/CardList";
import CardView from "./components/CardView";


function App() {
  return (
    <div className="App">
      <div>
          <div style={{float:"left",width:"20%"}}>
            <DeckList/>
          </div>
          <div style={{float:"left",width:"20%"}}>
              <CardList/>
          </div>
          <div style={{float:"left",width:"20%"}}>
              <CardView/>
          </div>
      </div>
    </div>
  );
}

export default App;
