import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import axios from 'axios';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // 백엔드 URL
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});

const handleSearch = async () => {
  if (!search.trim()) {
    setError('검색어를 입력해주세요.');
    return;
  }

  try {
    setError(null); // 기존 에러 초기화
    const response = await axios.get(`/api/analyze_by_name`, {
      params: { name: search.trim() }, // 사용자가 입력한 검색어를 API 요청에 포함
    });
    setData(response.data); // API 응답 데이터를 상태에 저장
  } catch (err) {
    setError(err.response?.data?.detail || '데이터를 가져오는 중 오류가 발생했습니다.');
  }
};
