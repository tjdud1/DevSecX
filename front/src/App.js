// src/App.js

import React from "react";
import SecurityReport from "./components/SecurityReport"; // SecurityReport 불러오기

function App() {
  return (
    <div>
      <h1>LLM 보안 취약점 분석기</h1>
      <SecurityReport />
    </div>
  );
}

export default App;
