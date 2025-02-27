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

본 코드에는 보안 취약점이 없으므로, 수정할 부분이 없습니다.  제공된 코드는 `eval()` 함수의 위험성을 보여주는 예시 코드이며,  Streamlit 앱 자체는  보안 취약점을 가지고 있지 않습니다.  `eval()` 함수의 사용은  사용자 입력을 직접 실행하기 때문에 매우 위험하며, 절대 실제 서비스 환경에서 사용해서는 안 됩니다.


만약 `run_bandit_cli`, `Grok_req`, `LMStudioLLM`, `PDFReport` 함수들의 구현에 보안 취약점이 있다면, 해당 함수들의 코드를 제공해야  구체적인 수정 방안을 제시할 수 있습니다.  예를 들어,  `Grok_req` 함수가  외부 API와의 통신을 처리한다면,  입력 값 검증,  출력 값 검증,  HTTP 요청에 대한 적절한 에러 처리 등의 보안 조치가 필요할 것입니다.


**보안을 강화하려면 다음과 같은 추가 조치가 필요합니다:**

* **입력 검증:** 사용자 입력을 항상 검증하여 악성 코드를 방지합니다.  `eval()` 대신 `ast.literal_eval()`을 사용하는 것이 좋습니다. `ast.literal_eval()`은 문자열을 안전하게 파싱하여 파이썬 객체로 변환하지만, 임의의 코드를 실행하지 않습니다.

* **출력 검증:**  `Grok_req` 함수의 출력을 검증하여 예상치 못한 결과를 처리합니다.

* **에러 처리:** 예외 처리를 철저히 구현하여 오류 발생 시 안전하게 처리합니다.

* **종속성 관리:**  프로젝트의 모든 종속성을 관리하고 정기적으로 업데이트하여 취약점을 해결합니다.  `pip-tools` 나 `poetry` 같은 도구를 사용하는 것이 좋습니다.


요약하자면, 제공된 코드 자체에는 보안 취약점이 없지만, 사용된 함수들(특히 `eval()`을 사용하는 부분과 외부 API 통신을 하는 부분)의 구현과  종속성 관리에 주의를 기울여야 안전한 애플리케이션을 만들 수 있습니다.  더 자세한 수정 방안은  `run_bandit_cli`, `Grok_req`, `LMStudioLLM`, `PDFReport` 함수들의 코드를 제공해 주시면 드릴 수 있습니다.
