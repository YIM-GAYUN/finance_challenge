import React from 'react';
import './Intro.css';
import logo from './asset/logo.png';
import { Link } from 'react-router-dom';
import wizardImage from './asset/모험 마법사.png';

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
        <div className="intro-section">
          <div className="intro-text">
            <p>주식이 어렵게 느껴지시나요?<br />복잡한 주식 용어가 낯설게만 다가오시나요?<br />
            관심 있는 종목의 핵심 정보를 한눈에 보고 싶으신가요?<br /><br />그렇다면?</p>
            <div className='intro-plus'><strong>K-STOCK INSIGHTS !</strong></div></div>
          <div className="intro-image">
            <img src={wizardImage} alt="모험 마법사" />
          </div>
        </div>
        <div className="intro-footer">
          <p>저희 서비스는 관심 있는 주식 종목의 핵심 지표를 보기 쉽게 정리해드립니다.<br />
          ROE, PBR, PER 등 주요 지표부터 과거 흐름과 앞으로의 전망까지 분석하여, 해당 종목의 투자 태세를 RPG 게임 속 캐릭터에 빗대어 쉽고 재미있게 전달합니다.<br />
          또한 종목의 장단점을 함께 제시해, 투자 판단에 필요한 인사이트를 제공합니다.<br />
          이제 주식 분석을 쉽고 재미있게 경험해보세요!</p>
        </div>
      </main>
    </div>
  );
};

export default Intro;
