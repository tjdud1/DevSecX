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

이 코드는 보안 취약점을 **직접 수정하지 않습니다**.  제공된 코드는 Streamlit 웹 애플리케이션을 구축하는 데 중점을 두고 있으며,  `eval()` 함수의 사용으로 인한 보안 취약점 분석 및 보고서 생성 기능을 제공합니다.  `eval()` 함수를 사용하는 코드 자체를 수정하려면,  사용자가 입력한 코드를 분석하고 `ast.literal_eval()` 과 같은 안전한 대안으로 바꿔주는 기능을 추가해야 합니다.  이는 추가적인 코드 분석 및 변환 로직이 필요하며,  단순히 이 코드만으로는 불가능합니다.  

**`eval()` 함수를 안전하게 대체하는 방법은 다음과 같습니다:**

사용자가 입력한 코드를 `ast.literal_eval()`을 사용하여 안전하게 평가하는 방법을 추가해야 합니다.  이는 별도의 함수로 구현해야 하며,  입력 검증을 추가하여  예상치 못한 입력에 대한 오류 처리도 고려해야 합니다.

예시 (추가적인 함수):

```python
import ast

def safe_eval(user_input):
    try:
        result = ast.literal_eval(user_input)
        return result
    except (ValueError, SyntaxError):
        return "Invalid input"
    except Exception as e:
        return f"An error occurred: {e}"

def vulnerable_fixed():
    user_input = input("Enter expression: ")
    result = safe_eval(user_input)
    print("Result:", result)

if __name__ == "__main__":
    vulnerable_fixed()
```

**중요:** 위에 추가된 `safe_eval` 함수는 `eval()` 보다 안전하지만,  임의의 Python 코드를 실행할 수 없다는 제약이 있습니다.  더 복잡한 입력 검증 및 sanitization이 필요한 경우,  보다 정교한 코드 분석 기법을 적용해야 합니다.  사용자 입력을 처리할 때는 항상 보안을 최우선으로 고려해야 합니다.
