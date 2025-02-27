```python
import streamlit as st
import os
from LLM_requests import LMStudioLLM  # LMStudioLLM이 langcha 패키지에 있다고 가정
from bandit_result import run_bandit_cli  # Bandit CLI를 실행하는 함수 (문자열 반환)
from report import PDFReport
from Grok_api import Grok_req #  # Grok api 요청 함수 (응답 문자열 반환)

# LMStudio API 엔드포인트 설정
api_url = "http://127.0.0.1:1234/v1/chat/completions"
llm = LMStudioLLM(api_url=api_url)
pdf_report = PDFReport()

st.title("DevSecX 프로젝트")

# 업로드 폴더 생성 (없으면 생성)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 사용자가 직접 코드를 입력할 수 있는 텍스트 영역 (기본 코드 예시 포함)
code_input = st.text_area(
    "분석할 코드를 입력하세요",
    value='''def vulnerable():
    user_input = input("Enter expression: ")
    result = eval(user_input)  # 보안 취약점: eval 사용
    print("Result:", result)

if __name__ == "__main__":
    vulnerable()''',
    height=300
)

# 커밋(분석 실행) 버튼
if st.button("커밋 및 분석 실행"):
    
    # 입력받은 코드를 uploads 폴더에 저장 (고정 파일명 또는 타임스탬프 활용 가능)
    file_path = os.path.join(UPLOAD_FOLDER, "user_input_code.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_input)
    st.write("코드가 저장되었습니다:", file_path)
    
    # Bandit 취약점 분석 실행 (문자열 반환을 가정)
    bandit_result = run_bandit_cli(file_path)
    
    st.subheader("Bandit 취약점 분석 결과")
    st.text_area("Bandit 결과", value=bandit_result, height=200)
    
    # 분석 결과를 포함한 프롬프트 생성
    prompt = bandit_result + '''
아래 양식대로 보고서 작성해 그리고 한국어로 작성해
[보고서 작성 양식 예시]

1.개요

스캔 실행 일시 및 대상 파일 정보:
전체 스캔 결과 요약 (예: 검출된 총 이슈 수, 심각도 분포 등):
2.취약점 상세 분석

취약점 ID: 예) B307
취약점 설명:
위험한 함수(e.g., eval) 사용과 관련된 문제 및 이에 따른 보안 우려 사항에 대한 설명
심각도 및 신뢰도: 예) Medium, High
관련 CWE: CWE-78 (OS 명령어 주입)
발견 위치: 파일 경로 및 코드 라인 번호
참고 자료: 관련 문서 링크 (예: Bandit 문서 링크)
3.영향 분석 및 위험 평가

해당 취약점이 시스템 또는 애플리케이션에 미치는 영향:
보안 위험 평가 및 우선순위 산정:
4.권고 사항 및 개선 방안

취약점 개선을 위한 구체적인 권고 사항: (예: eval 대신 ast.literal_eval 사용 권장)
추가적인 보안 모범 사례 제시:
5.결론

보고서 요약 및 향후 보완 조치에 대한 권고사항:'''
    
    st.subheader("생성된 프롬프트")
    st.text_area("프롬프트 미리보기", value=prompt, height=200)
    
    # LLM 진단 실행
    with st.spinner("취약점 진단 중..."):
        llm_output = Grok_req(prompt)#로컬모델 사용시 llm.invoke(prompt)
    
    
    st.success("진단이 완료되었습니다!")
    st.subheader("LLM 진단 결과")
    st.code(llm_output, language='python')

    st.download_button(
    label="PDF 보고서 다운로드",
    data=pdf_report.pdf_builder(llm_output),
    file_name="diagnostic_report.pdf",
    mime="application/pdf"
    )
```

**수정 사항:**  제공된 코드에는 보안 취약점이 없었습니다.  질문에서 요구한 "수정 코드"는 원본 코드에 보안 문제가 있어야 생성될 수 있습니다.  위 코드는  본질적으로 변경되지 않았습니다.  `eval()` 함수 사용이 보안 취약점이므로,  `ast.literal_eval()` 로 대체하는 것이 필요합니다. 하지만,  이러한 수정은  `run_bandit_cli` 함수의 결과와 LLM의 응답에 따라 동적으로 이루어져야 합니다.  따라서,  LLM에서  `ast.literal_eval()` 사용을 권장하는 응답을 받았다고 가정하고  `code_input` 을 수정하는 부분을 추가해야 합니다.  하지만 LLM의 응답이 항상 `ast.literal_eval()` 사용을 권장하는 것은 아니므로,  LLM의 응답을 파싱하여 적절한 수정을 하는 로직이 필요합니다. 이 부분은  `Grok_req` 함수와 `llm_output` 의 구조에 따라 다르게 구현되어야 합니다.


**필요한 추가 작업:**

1. **LLM 응답 파싱:**  `llm_output`에서  `ast.literal_eval()` 사용 권장 여부를 파싱하는 로직을 추가해야 합니다.  정규 표현식이나 문자열 매칭을 사용할 수 있습니다.
2. **코드 수정:**  LLM 응답에 따라 `code_input`을 수정하는 함수를 작성해야 합니다.  `eval()`을  `ast.literal_eval()`로 안전하게 바꾸는 로직이 포함되어야 합니다.  단순한 문자열 치환이 아닌, 코드의 구조를 이해하고 수정하는 고급 로직이 필요할 수 있습니다.
3. **에러 처리:**  LLM 응답 파싱이나 코드 수정 과정에서 에러가 발생할 수 있으므로,  적절한 에러 처리를 추가해야 합니다.
4. **`Grok_req` 및 `LMStudioLLM` 구현:**  제공되지 않은 `Grok_req` 및 `LMStudioLLM` 함수의 구현이 필요합니다.


단순한 코드 수정이 아닌,  LLM 응답을 분석하고 그에 따라 코드를 동적으로 수정하는 복잡한 시스템을 구축해야 합니다.  위 수정된 코드는  기본적인 틀만 제공하며,  실제 동작을 위해서는  추가적인 작업이 필요합니다.
