import streamlit as st
from openai import OpenAI

# OpenAI 클라이언트 설정
api_key = st.session_state.get("openai_api_key", None)
if not api_key:
    st.error("API 키가 입력되지 않았습니다. 사용자 정보 페이지로 이동해주세요.")
    st.stop()
client = OpenAI(api_key=api_key)

# 페이지 제목
st.title("면접 결과 확인")

# 면접 진행 여부 확인
end_interview = st.session_state.get("interview_ended", False)
if not end_interview:
    if st.button("면접을 진행하지 않았습니다."):
        st.switch_page("pages/2_Mock Interview.py")
    st.stop()

# 사용자 정보 확인
user_info = st.session_state.get("user_info", {})
if not user_info:
    if st.button("사용자 정보가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

# 면접 대화 기록 확인
interview_messages = st.session_state.get("interview_messages", [])
if not interview_messages:
    st.error("면접 대화 기록을 찾을 수 없습니다. 먼저 면접을 진행해주세요.")
    st.stop()

# API 요청 및 면접 요약 처리
if "interview_summary" not in st.session_state:
    with st.spinner("면접 결과를 요약 및 평가 중입니다..."):
        try:
            evaluation_prompt = f"""
            You are an expert interview evaluator. Summarize and score the following mock interview based on the content. Provide the following:
            1. A concise summary of the interview (bullet points are preferred).
            2. Feedback on the candidate's communication, relevance of answers, and adaptability.
            3. Provide individual scores out of 10 for:
              - Communication skills
              - Relevance to the questions asked
              - Adaptability
            4. A final overall score out of 10.
            
            ## Transcript:
            {interview_messages}
            """
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # gpt-4o-mini 모델을 지정
                messages=[
                    {"role": "system", "content": "You are an expert mock interview evaluator."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.7
            )
            summary = completion.choices[0].message.content  # 수정된 부분
            st.session_state["interview_summary"] = summary

        except Exception as e:
            st.error(f"면접 결과 요약 또는 점수 평가 중 오류가 발생했습니다: {e}")
            st.stop()

# 면접 요약 출력
summary = st.session_state["interview_summary"]
st.markdown("### 면접 내용 요약")
for section in summary.split("\n\n"):
    if section.strip():
        st.markdown(section.strip())

# 평가 점수 및 피드백 출력
st.markdown("### 평가 점수 및 피드백")
feedback_start = summary.find("Feedback:")
if feedback_start != -1:
    st.markdown(summary[feedback_start:])

# 결과 다운로드 기능
company_name = user_info.get("면접을 볼 회사", "Unknown Company")
download_button_text = f"""
Mock Interview Summary for {company_name}:

{summary}
"""
st.download_button(
    label="결과 다운로드 (txt)",
    data=download_button_text,
    file_name=f"{company_name}_interview_summary.txt",
    mime="text/plain"
)

# 다시 시작 버튼
if st.button("다시 시작하기"):
    st.session_state.clear()
    st.experimental_rerun()
