import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL;

fetch(`${API_URL}/api/analyze?ticker=TSLA`)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
