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
    
      const jsonStart = llmText.indexOf('{');
      const jsonEnd = llmText.lastIndexOf('}');
    
      if (jsonStart === -1 || jsonEnd === -1 || jsonStart >= jsonEnd) {
        console.error("❌ JSON 데이터가 올바르지 않습니다:", llmText);
        return null;
      }
    
      const cleanJson = llmText.slice(jsonStart, jsonEnd + 1);
    
      try {
        const parsedJson = JSON.parse(cleanJson);
    
        return {
          file: entry.file,
          run_started: parsedJson["스캔 시작 시간"] || parsedJson["run_started"] || "N/A",
          issues: parsedJson["이슈"] || 
                  parsedJson.test_results?.issues || 
                  parsedJson.results || 
                  [],
          code_scanned: parsedJson["코드 분석 결과"] || parsedJson.code_scanned || {},
          run_metrics: parsedJson["메트릭"] || parsedJson.run_metrics || {},
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
