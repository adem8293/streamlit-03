import streamlit as st
import openai

# 사용자 정보 및 대화 기록 확인
user_info = st.session_state.get("user_info", None)
interview_messages = st.session_state.get("interview_messages", None)

if user_info is None or interview_messages is None:
    st.error("면접 정보를 찾을 수 없습니다. 다시 시도해주세요.")
    if st.button("사용자 정보 입력 페이지로 이동"):
        st.switch_page("pages/1_User information.py")
    st.stop()

# API Key 확인
api_key = st.session_state.get("api_key", None)
if api_key is None:
    st.error("OpenAI API Key가 설정되지 않았습니다.")
    if st.button("초기 화면으로 이동"):
        st.switch_page("pages/1_User information.py")
    st.stop()

# OpenAI API Key 설정
openai.api_key = api_key

st.title("면접 결과 요약 및 점수 확인")
st.subheader(f"면접 본 회사: {user_info['면접을 볼 회사']}")

st.write("아래는 AI 모의 면접관이 생성한 요약 및 평가 결과입니다. 잠시 기다려 주세요.")

# 면접 요약 생성
if "interview_summary" not in st.session_state:
    with st.spinner("면접 요약 및 평가 생성 중..."):
        try:
            # 면접 대화 기록을 기반으로 요약 생성 요청
            summary_prompt = f"""
            Based on the following interview transcript, provide:
            1. A summary of the interview (in bullet points).
            2. Feedback on the candidate's communication skills, relevance, and adaptability.
            3. A score from 1-10 for the following criteria: communication, relevance, and adaptability.
            4. An overall score on a scale of 1-10.

            ## Interview Transcript:
            {interview_messages}
            """

            # OpenAI 새로운 인터페이스 호출
            response = openai.ChatCompletion.create(
                model="gpt-4",  # 사용할 모델 ("gpt-4" 또는 "gpt-3.5-turbo")
                messages=[
                    {"role": "system", "content": "You are an expert mock interview evaluator."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.7
            )

            # 응답 내용 저장
            summary = response["choices"][0]["message"]["content"]
            st.session_state["interview_summary"] = summary

        except Exception as e:
            st.error(f"면접 요약 생성 중 오류가 발생했습니다: {e}")
            st.stop()

# 요약 및 점수 표시
summary = st.session_state.get("interview_summary", None)
if summary:
    st.markdown("### 면접 요약")
    st.markdown(summary.split("\n\n")[0])

    st.markdown("### 피드백과 점수")
    st.markdown(summary.split("\n\n")[1])

# 최종 다운로드 옵션
downloadable_text = f"""
## Mock Interview Summary for {user_info['면접을 볼 회사']}:

{summary}
"""

st.markdown("### 다운로드 옵션")
st.download_button(
    label="결과 다운로드 (txt)",
    data=downloadable_text,
    file_name=f"{user_info['면접을 볼 회사']}_summary.txt",
    mime="text/plain"
)

if st.button("다시 시작하기"):
    st.session_state.clear()
    st.experimental_rerun()
