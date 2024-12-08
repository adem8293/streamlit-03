import streamlit as st

# 사용자 정보 및 대화 기록
user_info = st.session_state.get("user_info", None)
interview_messages = st.session_state.get("interview_messages", None)

if user_info is None or interview_messages is None:
    st.error("면접 정보를 찾을 수 없습니다. 다시 시도해주세요.")
    if st.button("네, 사용자 정보 페이지로 이동하겠습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

# GPT-4 기반 OpenAI 클라이언트
client = st.session_state.get("openai_client", None)
if client is None:
    st.error("API Key 정보가 없습니다. 초기화면에서 정보를 입력하세요.")
    if st.button("네, 초기 페이지로 이동하겠습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

st.title("면접 결과 요약 및 점수 확인")
st.subheader(f"면접을 본 회사: {user_info['면접을 볼 회사']}")
st.write("아래는 AI 면접관이 생성한 요약 결과와 점수입니다.")

# 면접 내용 요약 요청
if "interview_summary" not in st.session_state:
    with st.spinner("면접 내용을 요약 중입니다..."):
        # 면접 요약 생성 프롬프트
        summary_prompt = f"""
        Give a summary of the following mock interview in bullet points based on the following transcript. Provide feedback and scores on a scale of 1-10 for relevant criteria such as communication skills, relevance, and adaptability. A separate overall score should also be provided.

        ## Interview Transcript:
        {interview_messages}
        """

        try:
            response = client.Completion.create(
                engine="text-davinci-003",  # GPT-4 또는 다른 engine 선택
                prompt=summary_prompt,
                max_tokens=512,
                temperature=0.7,
            )
            summary = response.choices[0].text.strip()
            st.session_state["interview_summary"] = summary
        except Exception as e:
            st.error(f"요약 생성 중 문제가 발생했습니다: {e}")
            st.stop()

# 면접 요약 및 점수 출력
summary = st.session_state.get("interview_summary", None)
if summary:
    st.markdown("### 면접 요약")
    st.markdown(summary.split("\n\n")[0])  # 면접 요약 부분 출력

    st.markdown("### 점수 평가")
    scores = summary.split("\n\n")[1].strip("## Scores:").strip()  # 점수 부분 추출
    st.write(scores)

# 최종 점수와 피드백 파일 다운로드
downloadable_text = f"""
## Mock Interview Summary for {user_info['면접을 볼 회사']}:

{summary}
"""

st.markdown("### 다운로드 옵션")
st.download_button(
    label="결과 텍스트 다운로드 (.txt)",
    data=downloadable_text,
    file_name=f"{user_info['면접을 볼 회사']}_interview_summary.txt",
    mime="text/plain",
)

if st.button("다시 시작하기"):
    st.session_state.clear()
    st.experimental_rerun()
