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

코드 자체에는 보안 취약점이 없었습니다.  제공된 코드는 Streamlit 웹앱을 구축하는 코드이며,  `eval()` 함수를 사용하는 부분은 사용자 입력 코드를 실행하는 데 사용되므로,  웹앱 자체의 취약점이 아니라 사용자 입력 코드의 취약점을 검출하는 부분입니다.  따라서  웹앱 코드 자체를 수정할 필요는 없습니다.  `eval()`의 사용은 위험하지만,  이 코드의 목적 상  (사용자 코드를 실행하여 분석하는 것)  필수적인 부분입니다.

웹앱의 보안을 강화하려면 다음과 같은 부분을 고려해야 합니다.

* **사용자 입력 검증:** 사용자 입력 코드를 실행하기 전에  악성 코드를 방지하기 위한 엄격한 검증이 필요합니다.  단순한 문자열 검사를 넘어,  정적 및 동적 분석을 통한 안전성 검사가 필요합니다. (이 부분은 `run_bandit_cli` 함수에서 이미 어느 정도 처리되고 있지만, 더 강력한 검증이 필요할 수 있습니다.)
* **샌드박싱:** 사용자 코드를 안전한 샌드박스 환경에서 실행하여 시스템에 대한 접근을 제한해야 합니다.
* **출력 제한:** 사용자 코드의 출력을 제한하여 시스템 정보 유출을 방지해야 합니다.
* **에러 핸들링:** 예외 상황을 적절히 처리하여 시스템의 안정성을 유지해야 합니다.
* **의존성 관리:** 사용하는 라이브러리의 버전을 관리하고 보안 패치를 적용해야 합니다.


**요약:** 제공된 코드에는 웹앱 자체의 보안 취약점은 없으며, 사용자 입력 코드의 취약점을 검출하는 것이 목적입니다.  위에서 언급된 보안 강화 방안들을 고려하여  더 안전한 웹앱을 만들어야 합니다.  코드 수정 자체는 필요하지 않지만,  위험한 함수인 `eval()`의 사용은 항상 주의해야 합니다.  대안으로  `ast.literal_eval()`을 사용하는 것을 고려할 수 있습니다.  하지만 이 역시 모든 상황에 적합하지 않을 수 있으며, 사용자 입력에 대한 엄격한 검증이 필수적입니다.
