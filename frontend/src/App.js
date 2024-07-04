import './App.css';
import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import Services from './pages/Services';
function App() {

  return (
    <div className="App">
      <Services/>
      
    </div>
  );
}

export default App;
