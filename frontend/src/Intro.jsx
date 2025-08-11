import React from 'react';
import './Intro.css';
import logo from './asset/logo.png';
import { Link } from 'react-router-dom';

const Intro = () => {
  return (
    <div className="intro-page">
      <header className="header">
        <img src={logo} alt="Logo" className="logo" />
        <nav className="nav">
          <Link to="/search" className="nav-link">종목 검색</Link>
          <Link to="/intro" className="nav-link active">페이지 개요</Link>
          <Link to="/character" className="nav-link">캐릭터 소개</Link>
        </nav>
      </header>
      <main className="main-content">
        <h1>페이지 개요</h1>
        <p>이 페이지는 금융 정보를 검색하고 투자 요약을 제공합니다.</p>
      </main>
    </div>
  );
};

export default Intro;
