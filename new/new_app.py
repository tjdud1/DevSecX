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

코드 자체에는 보안 취약점이 없었습니다.  문제는 `eval()` 함수의 사용으로, 사용자가 입력한 문자열을 코드로 실행하는 위험성을 내포하고 있었습니다.  하지만 제공된 코드는  **Streamlit 애플리케이션의 구조**와 **LLM 결과 처리**에 초점을 맞춰 작성되어 있었고,  `eval()` 함수의 사용 자체는 Streamlit 애플리케이션의 외부에 있기 때문에,  이 코드 자체를 수정할 필요가 없습니다.  `eval()` 함수의 사용은 사용자 입력을 처리하는 부분에서 발생하는 취약점이고, 이 부분은  `code_input` 변수에 사용자가 입력한 코드에 대한 분석에 의존하는 것입니다.


만약  `code_input`에 입력된 코드에서 `eval()` 함수를 제거하고 안전한 대안을 사용하도록 하는 기능을 추가하려면,  코드 분석 및 변환 로직을 추가해야 합니다.  이를 위해서는  **추가적인 파이썬 코드 분석 라이브러리** (예: `ast`) 가 필요하며,  `run_bandit_cli` 함수 이후에 코드를 파싱하고,  `eval()` 함수를 찾아서  `ast.literal_eval()`  등의 안전한 대체 함수로 바꿔주는 기능을 구현해야 합니다.  하지만 이 부분은  `run_bandit_cli`  및  `Grok_req` 또는  `llm.invoke` 함수의 구현에 따라 달라지므로,  구체적인 코드는 제공할 수 없습니다.  해당 함수들의 구현부를 확인하여 필요한 로직을 추가해야 합니다.


요약하자면,  제공된 코드 자체에는 수정할 보안 취약점이 없으며,  사용자 입력 코드의 `eval()` 사용 문제는 별도의 코드 분석 및 변환 로직을 추가해야 해결 가능합니다.
