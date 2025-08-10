import React, { useState } from 'react';

function App() {
  const [search, setSearch] = useState('');

  // Dummy data for UI rendering
  const dummyData = {
    company: '삼성전자',
    ticker: '005930.KS',
    roe: 12.4,
    per: 11.8,
    pbr: 1.1,
    rpg: {
      title: '수호 전사',
      job: '전사',
      temper: '수호',
      description: '안정적 수익성과 저평가 매력을 바탕으로 자산을 지키는 타입',
    },
    summary3: [
      'ROE가 기준치를 상회해 수익성이 양호합니다.',
      'PER이 낮아 밸류에이션 부담이 크지 않습니다.',
      '환율/업황 변동이 실적에 미칠 영향은 점검이 필요합니다.',
    ],
    insights: {
      caution: '성장 속도가 둔화되면 밸류에이션 매력이 약해질 수 있습니다.',
      positive: '견고한 수익성과 상대적으로 낮은 밸류에이션이 장기 매력을 높입니다.',
    },
  };

  const handleSearch = () => {
    console.log('Searching for:', search);
    alert(`검색된 키워드: ${search}`);
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
            onChange={(e) => setSearch(e.target.value)}
            className="border rounded-l px-4 py-2 w-1/2"
          />
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-4 py-2 rounded-r"
          >
            검색
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="space-y-6">
        {/* Metric Chips */}
        <div className="flex space-x-4">
          <div className={`px-4 py-2 rounded ${dummyData.roe >= 10 ? 'bg-blue-500 text-white' : 'bg-gray-300'}`}>
            ROE: {dummyData.roe}%
          </div>
          <div className={`px-4 py-2 rounded ${dummyData.per <= 12 ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'}`}>
            PER: {dummyData.per}x
          </div>
          <div className={`px-4 py-2 rounded ${dummyData.pbr <= 1 ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'}`}>
            PBR: {dummyData.pbr}x
          </div>
        </div>

        {/* RPG Card */}
        <div className="p-4 bg-white rounded shadow">
          <h2 className="text-xl font-bold mb-2">{dummyData.rpg.title}</h2>
          <p className="text-sm text-gray-600">{dummyData.rpg.description}</p>
        </div>

        {/* Summary and Insights */}
        <div className="p-4 bg-white rounded shadow space-y-4">
          <div>
            <h3 className="font-bold">3문장 요약</h3>
            <ul className="list-disc pl-5">
              {dummyData.summary3.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="flex space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-yellow-500">⚠️</span>
              <p>{dummyData.insights.caution}</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-green-500">✅</span>
              <p>{dummyData.insights.positive}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
