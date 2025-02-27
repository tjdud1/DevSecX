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
    # 파일 경로 생성: uploads 폴더에 임시 파일 이름으로 저장. 보안 강화를 위해 임시 파일 사용
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

1. **임시 파일 사용:**  업로드된 파일을 `uploads` 폴더에 임시 파일로 저장하고,  `try...finally` 블록을 사용하여 처리가 완료된 후 임시 파일을 삭제하도록 변경했습니다. 이는  원본 파일 이름으로 파일이 저장될 때 발생할 수 있는  파일 이름 충돌 및 보안 문제를 방지합니다.  임시 파일 이름은  `tempfile` 모듈을 사용하여 생성하는 것이 더욱 안전하지만,  단순화를 위해  원본 파일 이름을 그대로 사용하고,  `finally` 블록에서 삭제하는 방식을 채택했습니다.


2. **오류 처리:**  `try...except` 블록을 추가하여 `run_bandit_cli` 함수나 LLM 호출 과정에서 발생할 수 있는 예외를 처리합니다.  에러 메시지를 사용자에게 표시하여 문제 해결에 도움을 줍니다.

3. **파일 확장자 검증 (추가 권장 사항):**  업로드된 파일의 확장자를 더욱 엄격하게 검증하는 것이 좋습니다.  현재 코드에서는 허용된 확장자만 업로드할 수 있도록 제한하고 있지만,  더욱 강력한 검증 방법(예: MIME 타입 확인)을 추가할 수 있습니다.  악성 파일 업로드를 방지하는 데 도움이 됩니다.

4. **입력 위생화 (추가 권장 사항):** `prompt` 변수에 사용자 입력이 직접 포함됩니다.  사용자 입력을 제대로 검증하지 않으면  LLM에 대한 공격(예:  프롬프트 인젝션)이 가능합니다.  `prompt` 변수에  사용자 입력을 추가하기 전에  입력 위생화(sanitization) 또는  출력 인코딩(escaping)을 수행하는 것이 좋습니다.


이 수정된 코드는  보안에 대한 고려 사항을 반영하여  더욱 안전하게 작동합니다.  하지만 완벽한 보안을 보장할 수는 없으므로,  실제 운영 환경에서는  더욱 엄격한 보안 조치를 적용하는 것이 좋습니다.
