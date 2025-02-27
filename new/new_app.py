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

* 코드 자체에는 보안 취약점이 없었습니다.  문제는 `eval()` 함수의 사용을 지적하는 것이었고, 이는  `st.text_area`, `st.button`, `st.write`, `st.subheader`, `st.text_area`, `st.spinner`, `st.success`, `st.code`, `st.download_button` 등 Streamlit 함수를 사용하는 방식과는 무관합니다.  `eval()` 사용 자체가 취약점이므로,  `run_bandit_cli` 함수가 그 부분을 검출하고 `llm_output` 에 그 결과가 반영된다고 가정하고 코드를 수정하지 않았습니다.

* 만약 `run_bandit_cli` 와 `Grok_req` (혹은 `llm.invoke`) 함수가  `eval()`의 사용을 감지하여  `llm_output`에  `ast.literal_eval`을 사용하라고  제안하는 결과를 반환한다면,  추가적인 코드 수정은 필요하지 않습니다.  보고서 생성 부분은 이미  `llm_output`을 사용하고 있으므로,  LLM이 생성한 수정된 코드가  `llm_output`에 포함될 것입니다.


**추가적인 보안 강화 방안 (만약 `run_bandit_cli`나 `Grok_req`가 자동 수정을 하지 않는 경우):**

LLM이 자동으로 코드를 수정하지 못할 경우,  `llm_output`을 처리하는 부분에 추가적인 로직을 넣어  `eval()`을 `ast.literal_eval()`로  수동으로 교체하는 기능을 추가해야 할 수도 있습니다. 이는  `llm_output`의 문자열을 파싱하고  `eval()`을 찾아  `ast.literal_eval()`로 대체하는 정규 표현식이나 문자열 조작을 필요로 합니다.  하지만 이 경우  코드의 구조가 복잡해지고 오류 가능성도 높아집니다.  가능한 한 LLM이 직접 코드 수정을 하도록 프롬프트를 개선하는 것이 더 안전하고 효율적입니다.


**프롬프트 개선:**

LLM에게 더 명확한 지시를 내리기 위해, 프롬프트에 다음과 같은 내용을 추가하는 것을 고려할 수 있습니다:

* `eval()` 함수 사용의 위험성을 명시적으로 설명하고,  `ast.literal_eval()` 사용을 명확하게 제안합니다.
*  수정된 코드를  json 형식으로 반환하도록 요청합니다. (파싱을 용이하게 함)
*  `eval()`을 사용하는 코드 부분을  정확히 지적하고  그 부분만 수정하도록 지시합니다.


결론적으로, 제공된 코드 자체에는 보안 취약점이 없으며, `eval()` 사용을 감지하고 처리하는 부분은  `run_bandit_cli`  및  LLM (혹은 Grok API)  의 기능에 의존합니다.  만약 이 함수들이 `eval()`을  `ast.literal_eval()`로 수정하지 않는다면,  `llm_output` 처리 로직에  수정 코드를 적용하는 추가적인 부분을 구현해야 합니다.  하지만 이는 LLM이 코드 수정을 직접 수행하도록 하는 것보다  복잡하고 오류 가능성이 높습니다.
