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

* **코드 자체에는 보안 취약점 수정이 불가능합니다.**  제공된 코드는 Streamlit 웹 애플리케이션을 구축하는 코드이며,  `eval()` 함수 사용과 같은 보안 취약점은 사용자가 입력하는 코드에 존재하는 것이지, Streamlit 애플리케이션 코드 자체에 있는 것이 아닙니다.  Streamlit 애플리케이션 코드는 사용자 입력을 안전하게 처리하는 방법을 개선해야 합니다.  하지만,  사용자 입력 코드 자체를 분석하고 수정하는 부분은  `run_bandit_cli` 함수와 LLM(Grok_req)의 역할입니다.  본 코드는  `eval()`의 사용을 감지하고  LLM을 통해 안전한 대안을 제시받아 사용자가 수정하도록 유도하는 구조입니다.

* **사용자 입력 처리 개선:**  `eval()`을 사용하는 사용자 코드를 직접 수정할 수는 없지만, 애플리케이션에서  `eval()`을 사용하는 코드를 직접 처리하지 않도록 설계하는 것이 중요합니다. (예: 사용자 코드를 샌드박스 환경에서 실행하거나,  안전한 코드 해석 라이브러리를 사용하는 방안을 LLM이 제안하도록 유도)

* **에러 처리 개선:**  실제 구현에서는  `run_bandit_cli`, `Grok_req`, `pdf_report.pdf_builder` 함수에서 발생할 수 있는 예외를 처리하는 try-except 블록을 추가하는 것이 좋습니다.


**LLM(Grok_req 또는 llm.invoke)이 반환해야 할 내용:**

LLM은 Bandit 결과를 바탕으로  `eval()` 함수의 위험성과 `ast.literal_eval()` 사용을 권장하는 보고서를 생성해야 합니다.  또한, 사용자의 코드를 직접 수정할 수는 없으므로, `eval()`을 대체하는 안전한 코드를 제안하는 것이 좋습니다. 예를 들어, 다음과 같은 응답을 LLM이 생성하도록 프롬프트를 설계해야 합니다.


**LLM이 생성해야 하는 보고서의 예시 (일부):**

```
4. 권고 사항 및 개선 방안

취약점 개선을 위한 구체적인 권고 사항:  `eval()` 함수는 임의의 코드를 실행할 수 있으므로, 사용자 입력을 직접 실행하는 데 사용해서는 안 됩니다.  대신, `ast.literal_eval()` 함수를 사용하여 안전하게 문자열을 평가할 수 있습니다.  `ast.literal_eval()`은 문자열을 파이썬 리터럴로만 파싱하므로, 임의의 코드 실행을 방지합니다.

수정된 코드 예시:

```python
import ast

def safe_vulnerable():
    user_input = input("Enter expression: ")
    try:
        result = ast.literal_eval(user_input)
        print("Result:", result)
    except (ValueError, SyntaxError):
        print("Invalid input")

if __name__ == "__main__":
    safe_vulnerable()
```

추가적인 보안 모범 사례 제시: 사용자 입력을 항상 검증하고, 입력의 형식과 길이를 제한하여 공격을 방지하십시오.  입력값에 대한 유효성 검사를 추가하고, 예외 처리를 통해 오류를 적절히 처리하십시오.
```

요약하자면, Streamlit 애플리케이션 코드 자체는 수정할 필요가 없지만,  LLM을 통해 사용자 코드의 보안 취약점을 분석하고,  안전한 코드로 수정하는 방법을 제시해야 합니다.  그리고 그 결과를 Streamlit으로 표시하는 것이 중요합니다.
