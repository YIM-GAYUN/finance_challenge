import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Search from './Search';
import Intro from './Intro';
import Character from './Character';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Search />} />
        <Route path="/search" element={<Search />} />
        <Route path="/intro" element={<Intro />} />
        <Route path="/character" element={<Character />} />
      </Routes>
    </Router>
  );
};

export default App;
