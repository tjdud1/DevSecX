import streamlit as st
from LLM_requests import LMStudioLLM  # LMStudioLLM이 langcha 패키지에 있다고 가정
from bandit_result import run_bandit_cli
import os
#streamlit run app.py --server.port 3389

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
    # 파일 경로 생성: uploads 폴더에 원본 파일 이름으로 저장
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    # 파일 저장 (바이너리 쓰기)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    #취약점 분석 모듈
    banddit_result=run_bandit_cli(file_path)
    st.text_area("취약점분석 모듈 실행결과",value=banddit_result, height=200)
    
    '''# 업로드된 파일 내용을 읽어서 디코딩
    file_contents = uploaded_file.read().decode("utf-8")
    st.subheader("업로드된 코드")
    st.code(file_contents, language='python')'''
    
    # 파일 내용을 프롬프트에 추가
    prompt = banddit_result + "\n<this code vulnerability scan please>"
    st.subheader("생성된 프롬프트")
    st.text_area("프롬프트 미리보기", value=prompt, height=200)
    
    # 취약점 진단 버튼
    if st.button("취약점 진단 실행"):
        with st.spinner("진단 중입니다..."):
            output = llm.invoke(prompt)
        st.success("진단이 완료되었습니다!")
        st.subheader("진단 결과")
        st.code(output)
