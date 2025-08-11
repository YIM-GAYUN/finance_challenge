import React, { useState } from 'react';
import './Character.css';
import logo from './asset/logo.png';
import { Link } from 'react-router-dom';

const Character = () => {
  const [activePage, setActivePage] = useState('character');

  return (
    <div className="character-page">
      <header className="header">
        <img src={logo} alt="Logo" className="logo" />
        <nav className="nav">
          <Link to="/search" className={`nav-link ${activePage === 'search' ? 'active' : ''}`} onClick={() => setActivePage('search')}>종목 검색</Link>
          <Link to="/intro" className={`nav-link ${activePage === 'intro' ? 'active' : ''}`} onClick={() => setActivePage('intro')}>페이지 개요</Link>
          <Link to="/character" className={`nav-link ${activePage === 'character' ? 'active' : ''}`} onClick={() => setActivePage('character')}>캐릭터 소개</Link>
        </nav>
      </header>
      <main className="main-content">
        <h1>캐릭터 소개</h1>
        <p>이 페이지는 캐릭터 정보를 제공합니다.</p>
      </main>
    </div>
  );
};

export default Character;
