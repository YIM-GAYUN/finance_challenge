import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [search, setSearch] = useState(''); // 검색어 상태
  const [data, setData] = useState(null); // API 응답 데이터 상태
  const [error, setError] = useState(null); // 에러 상태

  const handleSearch = async () => {
    if (!search.trim()) {
      setError('검색어를 입력해주세요.');
      return;
    }

    try {
      setError(null); // 기존 에러 초기화
      const response = await axios.get(`${API_BASE_URL}/api/analyze_by_name`, {
        params: { name: search.trim() }, // 사용자가 입력한 검색어를 API 요청에 포함
      });
      setData(response.data); // API 응답 데이터를 상태에 저장
    } catch (err) {
      setError(err.response?.data?.detail || '데이터를 가져오는 중 오류가 발생했습니다.');
    }
  };

  const renderMetric = (metric) => {
    return metric !== null && metric !== undefined ? metric : "데이터 없음";
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      {/* Main Title */}
      <h1 className="text-4xl font-bold text-center text-blue-600 mb-6">은행 해커톤</h1>

      {/* Header */}
      <header className="mb-6">
        <div className="flex items-center justify-center">
          <input
            type="text"
            placeholder="기업 키워드 입력"
            value={search}
            onChange={(e) => setSearch(e.target.value)} // 검색어 상태 업데이트
            className="border rounded-l px-4 py-2 w-1/2"
          />
          <button
            onClick={handleSearch} // 검색 버튼 클릭 시 API 호출
            className="bg-blue-600 text-white px-4 py-2 rounded-r"
          >
            검색
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="space-y-6">
        {error && (
          <div className="text-red-500 text-center">{error}</div>
        )}

        {data ? (
          <>
            {/* Metric Chips */}
            <div className="flex space-x-4">
              <div className={`px-4 py-2 rounded ${data.roe >= 10 ? 'bg-blue-500 text-white' : 'bg-gray-300'}`}>
                ROE: {data.roe}%
              </div>
              <div className={`px-4 py-2 rounded ${data.per <= 12 ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'}`}>
                PER: {data.per}x
              </div>
              <div className={`px-4 py-2 rounded ${data.pbr <= 1 ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'}`}>
                PBR: {data.pbr}x
              </div>
            </div>

            {/* RPG Card */}
            <div className="p-4 bg-white rounded shadow">
              <h2 className="text-xl font-bold mb-2">{data.rpg.title}</h2>
              <p className="text-sm text-gray-600">{data.rpg.description}</p>
            </div>

            {/* Summary and Insights */}
            <div className="p-4 bg-white rounded shadow space-y-4">
              <div>
                <h3 className="font-bold">3문장 요약</h3>
                <ul className="list-disc pl-5">
                  {data.summary3.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="flex space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-yellow-500">⚠️</span>
                  <p>{data.insights.caution}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-green-500">✅</span>
                  <p>{data.insights.positive}</p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center text-gray-500">검색 결과가 여기에 표시됩니다.</div>
        )}
      </main>
    </div>
  );
}

export default App;
