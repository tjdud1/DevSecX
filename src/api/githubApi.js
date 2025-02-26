const owner = "tjdud1";
const repo = "DevSecX";
const branch = "refs/heads/main";
const path = "response.json";

export const fetchLLMResults = async () => {
  try {
    const response = await fetch(
      `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${path}`
    );

    const rawText = await response.text();
    console.log("📄 응답 데이터 (raw text):", rawText);

    // JSON 데이터 추출 로직
    const jsonStartIndex = rawText.indexOf('[');
    if (jsonStartIndex === -1) {
      throw new Error('JSON 배열 시작점을 찾을 수 없습니다.');
    }

    const jsonText = rawText.slice(jsonStartIndex);
    const data = JSON.parse(jsonText);

    // llm_response 내 JSON 추출
    const parsedData = data.map((entry) => {
      const llmText = entry.llm_response;

      // 코드 블록(```json ... ```) 제거
      const jsonStart = llmText.indexOf('{');
      const jsonEnd = llmText.lastIndexOf('}');
      const cleanJson = llmText.slice(jsonStart, jsonEnd + 1);

      try {
        const parsedJson = JSON.parse(cleanJson);
        return {
          file: entry.file,
          run_started: parsedJson.run_started || "N/A",
          issues:
            parsedJson.test_results?.issues ||
            parsedJson.results || // 새로운 구조 대응
            [],
          code_scanned: parsedJson.code_scanned || {},
          run_metrics: parsedJson.run_metrics || {},
        };
      } catch (err) {
        console.error("❌ llm_response JSON 파싱 실패:", err.message);
        return null;
      }
    });

    console.log("✅ 파싱된 데이터:", parsedData.filter(Boolean));
    return parsedData.filter(Boolean); // null 값 제거
  } catch (error) {
    console.error("❌ Error fetching LLM results:", error.message);
    return [];
  }
};
