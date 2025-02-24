import React, { useState } from 'react';
import Editor from '@monaco-editor/react';

export default function CodeAnalysisPage() {
  const [code, setCode] = useState('// 여기에 코드를 입력하세요');
  const [result, setResult] = useState(null);

  const handleCheck = () => {
    setResult('중간 산출물: 코드가 정상적으로 입력되었습니다.');
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>코드 취약점 분석기</h1>
      <div style={{ marginBottom: '1rem' }}>
        <h2>코드 입력 폼</h2>
        <Editor
          height="400px"
          language="javascript"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value)}
        />
      </div>
      <button onClick={handleCheck} style={{ padding: '0.5rem 1rem', backgroundColor: 'blue', color: 'white', border: 'none', cursor: 'pointer' }}>
        중간 산출물 확인
      </button>
      {result && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f4f4f4' }}>
          <h2>중간 산출물 결과</h2>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}
