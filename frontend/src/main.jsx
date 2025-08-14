import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const API_BASE = "https://finance-challenge.onrender.com"; // https!

async function callApi(payload) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // credentials: "include", // 정말 필요한 경우만
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}
