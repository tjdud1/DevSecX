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
        llm_output = Grok_req(prompt) #로컬모델 사용시 llm.invoke(prompt)
    
    
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

* 코드 자체에는 보안 취약점이 없으므로 수정할 부분이 없습니다.  제공된 코드는 Streamlit 웹 애플리케이션을 구축하는 코드이며,  `eval()` 함수의 사용은 사용자 입력 코드에서 발생하는 문제입니다.  따라서  `run_bandit_cli` 함수가  `eval()` 사용을 감지하고 그 결과를 `bandit_result`에 반영한다고 가정하여,  Streamlit 앱 코드 자체는 수정할 필요가 없습니다.


만약 `run_bandit_cli` 함수가  `eval()` 사용을 검출하지 못하거나,  다른 보안 취약점 분석 도구를 사용한다면,  해당 도구의 결과에 따라  `code_input` 에 입력된 코드를 수정하는 부분이 추가되어야 합니다.  예를 들어,  `ast.literal_eval`을 사용하는 코드로 변경하는 로직을 추가해야 할 수 있습니다.  하지만 제공된 정보만으로는 그러한 수정을 구현할 수 없습니다.


**추가적인 개선 사항:**

* **에러 핸들링:**  `run_bandit_cli`, `Grok_req`, `pdf_report.pdf_builder` 함수에서 예외가 발생할 경우를 처리하는 `try-except` 블록을 추가하여 애플리케이션의 안정성을 높여야 합니다.
* **파일 이름 생성:**  `user_input_code.py` 대신 고유한 파일 이름 (예: 타임스탬프 포함)을 사용하여 파일 충돌을 방지하는 것이 좋습니다.
* **입력 검증:** 사용자 입력 코드에 대한 검증을 추가하여 악의적인 코드 실행을 방지하는 것이 중요합니다. (예: 특정 키워드 필터링, 실행 시간 제한 등)
* **LLM 응답 처리:**  `Grok_req` 함수의 반환값 형태에 따라  `st.code` 함수의 사용 방식을 조정해야 할 수 있습니다.  LLM이  Markdown이나 HTML 형식으로 보고서를 생성할 수도 있으므로,  적절한 출력 방식을 선택해야 합니다.


이러한 개선 사항들을 추가하여 더욱 안전하고 강력한 Streamlit 애플리케이션을 만들 수 있습니다.  하지만,  `run_bandit_cli`, `Grok_req`, `pdf_report.pdf_builder` 함수의 구현 없이는  보다 구체적인 코드 수정을 제공할 수 없습니다.
