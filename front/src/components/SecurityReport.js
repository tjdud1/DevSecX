import React, { useState, useEffect } from "react";
import { fetchLLMResults } from "../api/githubApi";

const getIssues = (entry) => {
  // 'issues' (영어) 또는 '이슈' (한글) key 체크
  return entry.issues || entry.이슈 || [];
};

export default function SecurityReport() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const getData = async () => {
      const result = await fetchLLMResults();
      setData(result || []);
    };
    getData();
  }, []);

  const formatFilePath = (filePath) => {
    const parts = filePath.split("/DevSecX/");
    const path = parts.length > 1 ? parts[1] : filePath;
    const pathParts = path.split("/");
    return pathParts.slice(-2).join("/");
  };

  if (!data.length) {
    return <p>데이터를 불러오는 중...</p>;
  }

  return (
    <div>
      <h1>🛡️ 보안 취약점 분석 결과</h1>
      {data.map((entry, index) => {
        const issues = getIssues(entry);

        return (
          <div key={index} style={{ border: "1px solid black", padding: "1rem", marginBottom: "2rem" }}>
            <h2>📁 파일명: {formatFilePath(entry.file)}</h2>

            <h3>취약점 목록:</h3>
            {issues.length > 0 ? (
              <ul>
                {issues.map((issue, i) => (
                  <li key={i}>
                    <p><strong>ID:</strong> {issue.ID || issue.id || "N/A"}</p>
                    <p><strong>심각도:</strong> {issue.심각도 || issue.severity || "N/A"}</p>
                    <p><strong>신뢰도:</strong> {issue.신뢰도 || issue.reliability || "N/A"}</p>
                    <p><strong>위치:</strong> {issue.위치 || issue.location || "N/A"}</p>
                    <p>
                      <strong>CWE:</strong>{" "}
                      <a href={issue.CWE?.match(/\((.*?)\)/)?.[1] || "#"} target="_blank" rel="noopener noreferrer">
                        {issue.CWE || "N/A"}
                      </a>
                    </p>
                    {issue.설명 || issue.description ? (
                      <p><strong>설명:</strong> {issue.설명 || issue.description}</p>
                    ) : null}
                    {issue.권고사항 || issue.recommendation ? (
                      <p><strong>권고사항:</strong> {issue.권고사항 || issue.recommendation}</p>
                    ) : null}
                    {issue.코드스니펫 || issue.code_snippet ? (
                      <>
                        <p><strong>코드 스니펫:</strong></p>
                        <pre>{Array.isArray(issue.코드스니펫 || issue.code_snippet) ? (issue.코드스니펫 || issue.code_snippet).join("\n") : issue.코드스니펫 || issue.code_snippet}</pre>
                      </>
                    ) : null}
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