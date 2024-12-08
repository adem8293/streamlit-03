import streamlit as st
from openai import OpenAIError
import openai

# 타이틀 설정
st.title("면접 결과 요약 및 점수 매기기")

# 면접 데이터 로드 (st.session_state에서 추출)
interview_messages = st.session_state.get("interview_messages", None)

if interview_messages is None or len(interview_messages) < 2:
    st.error("면접 데이터가 부족하거나 면접이 종료되지 않았습니다.")
    st.stop()

# 질문-답변 추출
qa_pairs = [
    {"question": msg["content"], "answer": interview_messages[i + 1]["content"]}
    for i, msg in enumerate(interview_messages)
    if msg["role"] == "assistant" and i + 1 < len(interview_messages)
]

# 면접 요약 버튼
if st.button("면접 요약 보기"):
    try:
        # 면접 내용 합치기
        conversation = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in interview_messages]
        )

        # OpenAI API 호출: 대화 요약
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "다음 대화를 요약하고 면접자의 주요 답변을 분석하세요."},
                {"role": "user", "content": conversation}
            ]
        )
        summary = response.choices[0].message["content"]

        # 결과 표시
        st.markdown("### 면접 요약")
        st.write(summary)

        # 요약 내용을 session_state에 저장
        st.session_state["interview_summary"] = summary

    except OpenAIError as e:
        st.error(f"요약 생성 중 오류가 발생했습니다: {e}")

# 점수 매기기 버튼
if st.button("점수 계산"):
    try:
        scores = []

        for qa in qa_pairs:
            # OpenAI API 호출: 답변 평가
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "답변을 평가하고 점수를 0에서 10점 사이로 매기세요."},
                    {"role": "user", "content": f"질문: {qa['question']}\n답변: {qa['answer']}"}
                ]
            )
            score_text = response.choices[0].message["content"]
            score = int(score_text.split(":")[-1].strip())  # 점수 추출
            scores.append(score)

        # 평균 점수 계산
        final_score = sum(scores) / len(scores)

        # 결과 표시
        st.markdown("### 면접 점수")
        st.write(f"최종 점수: {final_score:.2f}/10")

        # 세부 점수 표시
        for idx, qa in enumerate(qa_pairs):
            st.markdown(f"#### 질문 {idx + 1}")
            st.write(f"**질문**: {qa['question']}")
            st.write(f"**답변**: {qa['answer']}")
            st.write(f"**점수**: {scores[idx]}/10")

        # 점수를 session_state에 저장
        st.session_state["final_score"] = final_score

    except OpenAIError as e:
        st.error(f"점수 계산 중 오류가 발생했습니다: {e}")

# 면접 결과 다운로드
if "interview_summary" in st.session_state and "final_score" in st.session_state:
    if st.button("면접 결과 다운로드"):
        summary = st.session_state["interview_summary"]
        final_score = st.session_state["final_score"]

        result_text = f"""면접 요약
---------------------
{summary}

최종 점수: {final_score:.2f}/10
"""
        # 파일로 저장
        st.download_button(
            label="다운로드",
            data=result_text,
            file_name="interview_result.txt",
            mime="text/plain"
        )
