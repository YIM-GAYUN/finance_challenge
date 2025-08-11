import React, { useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [search, setSearch] = useState(""); // 검색어 상태
  const [data, setData] = useState(null); // API 응답 데이터 상태
  const [error, setError] = useState(null); // 에러 상태

  const handleSearch = async () => {
    setError(null);
    setData(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze_by_name?name=${encodeURIComponent(search)}`);
      if (!response.ok) {
        throw new Error("데이터를 가져오는 데 실패했습니다.");
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>KR Stock Analyzer</h1>
      <div style={{ marginBottom: "20px" }}>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="종목명을 입력하세요 (예: 삼성전자)"
          style={{ padding: "10px", width: "300px", marginRight: "10px" }}
        />
        <button onClick={handleSearch} style={{ padding: "10px 20px" }}>
          검색
        </button>
      </div>

      {error && <div style={{ color: "red" }}>에러: {error}</div>}

      {data && (
        <div style={{ border: "1px solid #ccc", padding: "20px", borderRadius: "5px" }}>
          <h2>종목 정보</h2>
          <p><strong>회사명:</strong> {data.company}</p>
          <p><strong>티커:</strong> {data.ticker}</p>

          <h3>주요 지표</h3>
          <p><strong>ROE:</strong> {data.roe !== null ? `${data.roe}%` : "데이터 없음"}</p>
          <p><strong>PER:</strong> {data.per !== null ? `${data.per}x` : "데이터 없음"}</p>
          <p><strong>PBR:</strong> {data.pbr !== null ? `${data.pbr}x` : "데이터 없음"}</p>

          <h3>RPG 분류</h3>
          <p><strong>타이틀:</strong> {data.rpg.title}</p>
          <p><strong>직업:</strong> {data.rpg.job}</p>
          <p><strong>성격:</strong> {data.rpg.temper}</p>
          <p><strong>설명:</strong> {data.rpg.description}</p>

          <h3>투자 요약</h3>
          <ul>
            {data.summary3.map((summary, index) => (
              <li key={index}>{summary}</li>
            ))}
          </ul>

          <h3>인사이트</h3>
          <p><strong>주의:</strong> {data.insights.caution}</p>
          <p><strong>장점:</strong> {data.insights.positive}</p>

          <h3>데이터 출처</h3>
          <p><strong>출처:</strong> {data.source.primary}</p>
          <p><strong>기준 시점:</strong> {data.source.as_of}</p>
        </div>
      )}
    </div>
  );
}

export default App;
