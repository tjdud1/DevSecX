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

**수정 사항:**  코드 자체에는 보안 취약점이 없었습니다.  문제는 `eval()` 함수의 사용이었습니다.  Streamlit 앱 자체는 수정이 필요 없고,  `eval()` 함수를 사용하는 코드를 분석하고  보고서를 생성하는 부분에  집중해야 합니다.  앱 코드를 수정하는 대신  `eval()` 사용의 위험성을 감지하고  대안을 제시하는 LLM 프롬프트와 `Grok_req` (혹은 `llm.invoke`)  함수의 응답 처리에  집중하는 것이  핵심입니다.  즉,  `eval()` 사용을 경고하고  `ast.literal_eval()` 로 대체하는 방법을  LLM이 제안하도록  프롬프트를 설계해야 합니다.  아래는 개선된 프롬프트 예시입니다.

**개선된 프롬프트 (예시):**

```
bandit_result + """
아래 양식대로 보고서를 작성하고, 특히 `eval()` 함수 사용에 대한 위험성과 `ast.literal_eval()`을 사용한 안전한 대체 방법을 명시하십시오. 한국어로 작성해주세요.

[보고서 작성 양식 예시]

1. 개요
    - 스캔 실행 일시 및 대상 파일 정보:
    - 전체 스캔 결과 요약 (예: 검출된 총 이슈 수, 심각도 분포 등):

2. 취약점 상세 분석
    - 취약점 ID: 예) B307
    - 취약점 설명:  `eval()` 함수 사용으로 인한 코드 실행 취약성에 대한 설명.  사용자 입력을 직접 실행하는 위험성을 구체적으로 설명.
    - 심각도 및 신뢰도: 예) Medium, High
    - 관련 CWE: CWE-94 (임의 코드 실행)
    - 발견 위치: 파일 경로 및 코드 라인 번호
    - 안전한 대체 방법: `ast.literal_eval()` 사용 방법과 예시 코드 포함.

3. 영향 분석 및 위험 평가
    - 해당 취약점이 시스템 또는 애플리케이션에 미치는 영향: 악성 코드 실행 가능성, 정보 유출 가능성 등 구체적으로 설명.
    - 보안 위험 평가 및 우선순위 산정:

4. 권고 사항 및 개선 방안
    - 취약점 개선을 위한 구체적인 권고 사항:  `eval()`을 `ast.literal_eval()`로 대체하는 방법 상세히 설명 및 코드 제공.
    - 추가적인 보안 모범 사례 제시: 사용자 입력 검증 및 sanitize 방법 등

5. 결론
    - 보고서 요약 및 향후 보완 조치에 대한 권고사항:
"""
```

이 개선된 프롬프트를 사용하면 LLM이  `eval()`의 위험성을 인지하고  구체적인 대안을 제시하는 보고서를 생성할 가능성이 높아집니다.  `Grok_req`  또는  `llm.invoke`  함수는 이  개선된 프롬프트를 사용하도록 수정해야 합니다.  그리고 `PDFReport` 클래스는 생성된 보고서를  잘 포맷팅하여  PDF로 변환해야 합니다.  중요한 것은  **LLM에게 명확한 지침을 주는 것**입니다.
