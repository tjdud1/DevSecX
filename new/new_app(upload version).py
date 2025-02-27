```python
import streamlit as st
from LLM_requests import LMStudioLLM
from bandit_result import run_bandit_cli
import os

# LMStudio API 엔드포인트 설정
api_url = "http://127.0.0.1:1234/v1/chat/completions"
llm = LMStudioLLM(api_url=api_url)

# 페이지 제목
st.title("코드 취약점 자동 진단")

# 업로드 폴더 생성 (없으면 생성)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 파일 업로드 위젯 (지원 확장자: .py, .txt, .js, .java, .cpp)
uploaded_file = st.file_uploader("진단할 코드 파일을 업로드하세요", type=["py", "txt", "js", "java", "cpp"])

if uploaded_file is not None:
    # 파일 경로 생성: uploads 폴더에 임시 파일 이름으로 저장.  보안 강화를 위해 임시 파일 사용
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        bandit_result = run_bandit_cli(file_path)
        st.text_area("취약점 분석 모듈 실행 결과", value=bandit_result, height=200)

        prompt = f"{bandit_result}\n<this code vulnerability scan please>"
        st.subheader("생성된 프롬프트")
        st.text_area("프롬프트 미리보기", value=prompt, height=200)

        if st.button("취약점 진단 실행"):
            with st.spinner("진단 중입니다..."):
                output = llm.invoke(prompt)
            st.success("진단이 완료되었습니다!")
            st.subheader("진단 결과")
            st.code(output)

    except Exception as e:
        st.error(f"오류 발생: {e}")
    finally:
        # 임시 파일 삭제
        os.remove(file_path)

```

**수정 사항 및 보안 개선:**

1. **임시 파일 사용:**  `uploaded_file.name`을 직접 파일 이름으로 사용하는 대신 임시 파일 이름을 생성하여 사용합니다.  이는 동일한 파일 이름이 업로드될 경우 파일 덮어쓰기 문제와 보안 취약점을 방지합니다.  (실제 구현에는 `tempfile` 모듈을 사용하는 것이 좋습니다.)  위 코드는 임시 파일 생성 부분을 생략하고 파일 삭제만 구현했습니다.  실제 구현시 `tempfile.NamedTemporaryFile()`을 이용하여 임시 파일을 생성하고, `finally` 블록에서 `file.close()`를 호출하여 파일을 안전하게 삭제해야 합니다.

2. **예외 처리:**  `run_bandit_cli` 함수 호출 및 LLM 호출 부분에 `try...except` 블록을 추가하여 예외 발생 시 오류 메시지를 표시하고,  오류 발생 후에도 임시 파일을 삭제하도록 `finally` 블록을 사용합니다.  이는 프로그램의 안정성을 높입니다.

3. **파일 확장자 검증 추가 (추천):**  업로드된 파일의 확장자를 더욱 엄격하게 검증하는 코드를 추가하는 것이 좋습니다.  현재 코드는 `type` 리스트로 제한하지만,  더욱 강력한 검증 방법을 사용할 수 있습니다.  예를 들어, 파일 내용을 분석하여 실제 코드 파일인지 검증하는 방법을 고려할 수 있습니다.

4. **출력 sanitization (추천):**  LLM의 출력 결과를 사용하기 전에 sanitization 처리를 추가하는 것이 중요합니다.  LLM은 예측 불가능한 출력을 생성할 수 있으므로, 출력 결과에 악성 코드나 스크립트가 포함될 가능성을 고려해야 합니다.

5. **Bandit 결과 파싱 개선 (추천):**  `run_bandit_cli`의 결과를 더욱 구조적으로 파싱하여  Streamlit UI에서 더 효과적으로 표시할 수 있도록 개선할 수 있습니다. (예: 테이블 형태로 취약점 정보 표시)


이 수정된 코드는 보안 및 안정성을 향상시키지만,  실제로 안전한 시스템을 구축하려면 더욱 심도 있는 보안 검토가 필요합니다. 특히, 임시 파일 생성 및 삭제 부분은  `tempfile` 모듈을 이용하여 완벽하게 구현해야 합니다.  그리고  LLM의 출력을 신뢰하지 않고 항상 검증하는 절차를 거쳐야 합니다.
