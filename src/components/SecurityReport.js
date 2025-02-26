import React, { useState, useEffect } from "react";
import { fetchLLMResults } from "../api/githubApi";

export default function SecurityReport() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const getData = async () => {
      const result = await fetchLLMResults();
      setData(result || []);
    };
    getData();
  }, []);

  if (!data.length) {
    return <p>데이터를 불러오는 중...</p>;
  }

  return (
    <div>
      <h1>🛡️ 보안 취약점 분석 결과</h1>

      {data.map((entry, index) => {
        const issues = entry.issues || [];

        return (
          <div
            key={index}
            style={{
              border: "1px solid black",
              padding: "1rem",
              marginBottom: "2rem",
            }}
          >
            <h2>📁 파일명: {entry.file}</h2>
            <p><strong>실행 시간:</strong> {entry.run_started}</p>

            <h3>취약점 목록:</h3>
            {issues.length > 0 ? (
              <ul>
                {issues.map((issue, i) => (
                  <li key={i}>
                    <strong>ID:</strong> {issue.issue} <br />
                    <strong>심각도:</strong> {issue.severity} <br />
                    <strong>신뢰도:</strong> {issue.confidence} <br />
                    <strong>위치:</strong> {issue.location} <br />
                    <strong>CWE:</strong>{" "}
                    <a
                      href={issue.cwe_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {issue.cwe}
                    </a>
                    <br />
                    {issue.code_snippet && (
                      <>
                        <strong>코드 스니펫:</strong>
                        <pre>{Array.isArray(issue.code_snippet) ? issue.code_snippet.join("\n") : issue.code_snippet}</pre>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p>✅ 취약점 없음</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
