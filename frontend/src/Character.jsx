import React, { useState } from 'react';
import './Character.css';
import logo from './asset/logo.png';
import { Link } from 'react-router-dom';

import guardianWarrior from './asset/수호 전사.png';
import guardianMage from './asset/수호 마법사.png';
import guardianRogue from './asset/수호 도적.png';
import adventurerWarrior from './asset/모험 전사.png';
import adventurerMage from './asset/모험 마법사.png';
import adventurerRogue from './asset/모험 도적.png';

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
        <div className="character-row">
          <div className="character-card">
            <img src={guardianWarrior} alt="수호 전사" className="character-image" />
            <div className="character-info">
              <h2>수호 전사</h2>
              <p>안정적 수익성과 저평가 매력을 바탕으로 자신을 지키는 타입</p>
            </div>
          </div>
          <div className="character-card">
            <img src={guardianMage} alt="수호 마법사" className="character-image" />
            <div className="character-info">
              <h2>수호 마법사</h2>
              <p>검증된 기반 위에 분석과 혁신을 결합한 전략가</p>
            </div>
          </div>
          <div className="character-card">
            <img src={guardianRogue} alt="수호 도적" className="character-image" />
            <div className="character-info">
              <h2>수호 도적</h2>
              <p>저평가 구간에서 반등을 노리는 잠행형</p>
            </div>
          </div>
        </div>
        <div className="character-row">
          <div className="character-card">
            <img src={adventurerWarrior} alt="모험 전사" className="character-image" />
            <div className="character-info">
              <h2>모험 전사</h2>
              <p>수익성을 무기로 새로운 기회를 추적하는 도전형</p>
            </div>
          </div>
          <div className="character-card">
            <img src={adventurerMage} alt="모험 마법사" className="character-image" />
            <div className="character-info">
              <h2>모험 마법사</h2>
              <p>성장성과 기술 혁신을 앞세우는 개척자</p>
            </div>
          </div>
          <div className="character-card">
            <img src={adventurerRogue} alt="모험 도적" className="character-image" />
            <div className="character-info">
              <h2>모험 도적</h2>
              <p>높은 변동성을 기회로 삼는 추격형</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Character;
