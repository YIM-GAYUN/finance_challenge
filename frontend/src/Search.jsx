import React, { useState } from 'react';
import './Search.css';
import logo from './asset/logo.png';
import { Link } from 'react-router-dom';

const API_BASE_URL = "http://127.0.0.1:8000";

const Search = () => {
  const [activePage, setActivePage] = useState('search');
  const [search, setSearch] = useState(""); // 검색어 상태
  const [data, setData] = useState(null); // API 응답 데이터 상태
  const [error, setError] = useState(null); // 에러 상태
  const [loading, setLoading] = useState(false); // 로딩 상태 추가

  const handleSearch = async () => {
    setError(null);
    setData(null);
    setLoading(true); // 로딩 시작

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze_by_name?name=${encodeURIComponent(search)}`);
      if (!response.ok) {
        throw new Error("데이터를 가져오는 데 실패했습니다. 조금 더 구체적인 종목명 또는 영어 종목명을 작성해주세요!");
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false); // 로딩 종료
    }
  };

  return (
    <div className="search-page">
      <header className="header">
        <img src={logo} alt="Logo" className="logo" />
        <nav className="nav">
          <Link to="/search" className={`nav-link ${activePage === 'search' ? 'active' : ''}`} onClick={() => setActivePage('search')}>종목 검색</Link>
          <Link to="/intro" className={`nav-link ${activePage === 'intro' ? 'active' : ''}`} onClick={() => setActivePage('intro')}>페이지 개요</Link>
          <Link to="/character" className={`nav-link ${activePage === 'character' ? 'active' : ''}`} onClick={() => setActivePage('character')}>캐릭터 소개</Link>
        </nav>
      </header>
      <main className="main-content">
        <div className="search-bar">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="   종목명을 입력하세요 (예: 삼성전자)"
            className="search-input"
          />
          <button onClick={handleSearch} className="search-button">
            검색
          </button>
        </div>

        {loading && (
          <div className="loading">
            <img src="/asset/loading.gif" alt="Loading" className="loading-image" />
            <p>캐릭터 및 투자 정보를 생성중입니다. 잠시만 기다려주세요...</p>
          </div>
        )}

        {error && <div className="error">에러: {error}</div>}

        {data && (
          <div className="search-results">
            <div className="stock-info">
              <div className="info">종목 정보</div><br />
              <p><strong>회사명:</strong> {data.company}</p>
              <p><strong>티커:</strong> {data.ticker}</p><br />

              <h3>⚜️주요 지표</h3>
              <p>
                <strong>ROE:</strong> {data.roe !== null ? `${data.roe}%` : "데이터 없음"} &emsp;
                <strong>PER:</strong> {data.per !== null ? `${data.per}x` : "데이터 없음"} &emsp;
                <strong>PBR:</strong> {data.pbr !== null ? `${data.pbr}x` : "데이터 없음"}
              </p>
              <br />

              <h3>⚜️RPG 캐릭터 분류</h3>
              <p>
                <strong>타이틀:</strong> {data.rpg.title} &emsp;
                <strong>직업:</strong> {data.rpg.job} &emsp;
                <strong>성격:</strong> {data.rpg.temper}
              </p>
              <p><strong>설명:</strong> {data.rpg.description}</p><br />
              {data.rpg.title && (
                <img 
                  src={`/asset/${data.rpg.title}.png`} 
                  alt={data.rpg.title} 
                  className="rpg-image"
                />
              )}
            </div>

            <div className="investment-summary">
              <div className='info'>투자 정보</div><br />
              <ul>
                {data.summary3.map((summary, index) => (
                  <li key={index}>{summary}</li>
                ))}
              </ul>
              <br />

              <h3>⚜️인사이트</h3>
              <p><strong>주의:</strong> {data.insights.caution || '위 요약본 참고'}</p>
              <p><strong>장점:</strong> {data.insights.positive || '위 요약본 참고'}</p>

              <br />
              <h3>⚜️데이터 출처</h3>
              <p><strong>출처:</strong> {data.source.primary}</p>
              <p><strong>기준 시점:</strong> {data.source.as_of}</p>
            </div>
          </div>
        )}

        {!data && !error && (
          <div className="background-image">
            <div className = 'bginfo'>내가 투자하는 종목의 RPG 캐릭터성을 알아보세요</div>
            <div className = 'bginfo2'>RPG 캐릭터에 대한 각각의 설명은 '캐릭터 소개' 페이지에서 확인할 수 있습니다.</div>
            <div className = 'bgimg'><img src="/asset/bg.png" alt="Background" /></div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Search;
