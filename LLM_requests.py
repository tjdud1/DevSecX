import requests
from typing import Optional, List
from langchain.llms.base import LLM
from pydantic import Field



class LMStudioLLM(LLM):
    api_url: str = Field(..., description="LM Studio API 엔드포인트")
    api_key: Optional[str] = Field(None, description="LM Studio API 키 (필요 시)")
    model: str = Field("deepseek-r1-distill-qwen-7b", description="사용할 모델")
    temperature: float = Field(0.7, description="생성 온도")
    max_tokens: int = Field(-1, description="최대 토큰 수 (-1이면 제한 없음)")
    do_stream: bool = Field(False, description="스트리밍 여부")  # 'stream' -> 'do_stream' 변경
    
    @property
    def _llm_type(self) -> str:
        return "lm_studio_chat"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.do_stream,  # 변경된 변수 사용
        }
        
        if stop:
            data["stop"] = stop
        
        response = requests.post(self.api_url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return result.get("text", "")
    
    def invoke(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return self._call(prompt, stop)
        
# 사용 예시
if __name__ == "__main__":
    # 예시: 'example.py' 파일을 읽어와 변수에 저장하기
    file_path = 'vulcode.py'

    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()
    # LM Studio API 엔드포인트 예시 (실제 환경에 맞게 수정)
    api_url = "http://127.0.0.1:1234/v1/chat/completions"
    llm = LMStudioLLM(api_url=api_url)
    
    prompt = file_contents+'''Respond as shown in the example below

[Report Writing Template Example]

Overview

Scan execution date/time and target file information
Summary of overall scan results (e.g., total issues detected, severity distribution, etc.)
Detailed Vulnerability Analysis

Vulnerability ID: e.g., B307
Vulnerability Description: Explanation of the issues related to the dangerous function (eval) used and associated security concerns
Severity and Confidence: e.g., Medium, High
Related CWE: CWE-78 (OS Command Injection)
Discovery Location: File path and code line number
References: Relevant documentation links (e.g., Bandit documentation link)
Impact Analysis and Risk Assessment

The impact of the vulnerability on the system or application
Security risk evaluation and prioritization
Recommendations and Mitigation Measures

Specific recommendations for improving the vulnerability (e.g., advise using ast.literal_eval instead of eval)
Additional security best practices
Conclusion

Report summary and recommendations for future remedial actions'''

    print("입력:\n", prompt)  
    output = llm.invoke(prompt)
    
    print("LM Studio 응답:", output)

