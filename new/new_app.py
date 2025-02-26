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

**수정 사항:**

* 코드 자체에는 보안 취약점이 없었습니다.  기존 코드는 Streamlit 어플리케이션의 구조를 보여주는 예시였습니다.  따라서 보안 취약점을 개선할 부분이 없으므로, 코드 수정은 없습니다.  만약 `run_bandit_cli` 함수가 실제로 Bandit 결과를 반환하고, 그 결과에 따라  `Grok_req` 또는 `llm.invoke`가  `eval()` 사용에 대한 경고를 반환한다면,  LLM이  `eval()`을 `ast.literal_eval()`로 대체하는 방법을 제안하는 보고서를 생성할 것입니다.  하지만 제공된 코드 자체는 안전합니다.


**개선을 위한 추가 사항 (만약 `run_bandit_cli`가  `eval()` 사용을 감지한다면):**

`run_bandit_cli` 함수가  `eval()` 사용을 감지하여  `bandit_result`에 그 정보를 포함한다면,  LLM은  `ast.literal_eval()`을 사용하도록 코드를 수정하는 방법을 제안할 것입니다. 이 경우, Streamlit 앱은  LLM의 제안을 받아 수정된 코드를 사용자에게 보여주는 기능을 추가해야 합니다.  이를 위해 다음과 같은 변경이 필요할 수 있습니다.

1. **LLM 응답 파싱:** LLM의 응답에서 수정된 코드 부분을 추출하는 파서를 추가합니다.
2. **코드 업데이트 및 표시:**  추출된 수정된 코드를 `code_input`에 업데이트하고, 사용자에게 수정된 코드를 보여줍니다.
3. **다운로드 기능 업데이트:** 수정된 코드를 포함하여 PDF 보고서를 생성하고 다운로드할 수 있도록 합니다.


요약하자면, 제공된 코드에는 보안 취약점이 없으며,  실제 보안 취약점 분석 및 수정은 `run_bandit_cli` 와 LLM의 응답 처리 로직에 달려있습니다.  제공된 코드는 Streamlit 어플리케이션의 기본 틀을 제공하는 것입니다.
