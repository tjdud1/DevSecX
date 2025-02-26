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

* 코드 자체에는 보안 취약점이 없으므로, 코드 수정이 필요하지 않습니다.  문제는 `eval()` 함수의 사용으로 인한 보안 위험성을  `run_bandit_cli` 와  LLM을 통해 감지하고 보고서를 생성하는 부분에 있습니다.  제공된 코드는 이미 이러한 기능을 포함하고 있습니다.  `eval()` 사용의 위험성은 Bandit가 감지하고, LLM은 그 결과를 바탕으로 보고서를 생성합니다.  따라서 코드 자체를 수정하는 것이 아니라,  `run_bandit_cli` , `Grok_req`, `PDFReport` 함수들의 구현이 올바르게 작동하도록 하는 것이 중요합니다.


**개선을 위한 추가 사항:**

* **에러 핸들링:**  `run_bandit_cli`, `Grok_req` 함수에서 발생할 수 있는 예외(예: 네트워크 에러, 파일 처리 에러)를 처리하는 `try-except` 블록을 추가해야 합니다.  Streamlit에서 에러 메시지를 적절하게 표시하여 사용자에게 정보를 제공해야 합니다.
* **입력 유효성 검사:** 사용자가 입력한 코드가 유효한 Python 코드인지 확인하는 기능을 추가해야 합니다.  유효하지 않은 코드를 처리하는 방법을 명확히 해야 합니다.
* **Bandit 설정:** Bandit의 설정을 사용자 정의할 수 있도록 인터페이스를 추가하여 분석의 정확성과 범위를 조절할 수 있도록 하는 것이 좋습니다.
* **LLM 응답 처리:** LLM에서 반환되는 응답을 더욱 효과적으로 처리하여 PDF 보고서에 잘 통합되도록 해야 합니다.  예를 들어, LLM이 예상치 못한 형식으로 응답할 경우를 대비한 에러 처리가 필요합니다.
* **보고서 형식:** PDF 보고서의 형식과 내용을 개선하여 더욱 전문적이고 읽기 쉬운 보고서를 생성할 수 있도록 합니다.


이러한 개선 사항을 추가하면 더욱 안전하고 사용자 친화적인 DevSecX 프로젝트가 될 것입니다.  하지만 제공된 코드는 이미 `eval()`의 위험성을 감지하고 처리하기 위한 핵심적인 기능을 갖추고 있습니다.  문제는 각 함수의 구현에 있습니다.  함수들을 구현하고 테스트한 후, 필요에 따라 에러 핸들링과 유효성 검사 등을 추가해야 합니다.
