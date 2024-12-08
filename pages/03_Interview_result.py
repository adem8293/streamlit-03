import streamlit as st
import os

st.title("면접 결과 요약")

# 이전 세션에서 저장된 면접 내용 불러오기
interview_summary = st.session_state.get("interview_summary", None)

if interview_summary:
    st.subheader("면접 요약")
    st.text(interview_summary)

    # 다운로드 버튼
    company_name = st.session_state.get("user_info", {}).get("면접을 볼 회사", "Unknown_Company")
    filename = f"{company_name}_interview_summary.txt"

    with open(os.path.join("interview_contents", filename), "r") as file:
        st.download_button(
            label="면접 요약 다운로드",
            data=file,
            file_name=filename,
            mime="text/plain",
        )
else:
    st.warning("면접 요약 정보가 없습니다. 이전 페이지로 돌아가세요.")

# 홈으로 돌아가는 버튼
if st.button("홈으로 돌아가기"):
    st.switch_page("pages/1_User information.py")
