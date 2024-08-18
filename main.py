import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def main_screen():
    st.title("50+ 일일 웰니스 대시보드")
    
    # 오늘 날짜 표시
    today = datetime.now().date()
    st.subheader(f"오늘 날짜: {today}")

    # 2열 레이아웃 생성
    col1, col2 = st.columns(2)

    with col1:
        # 오늘의 체크리스트
        st.subheader("오늘의 체크리스트")
        checklist_data = get_checklist_items(st.session_state.username)
        progress = {}
        for category, items in checklist_data.items():
            st.write(f"**{category}**")
            for item in items:
                checked = st.checkbox(item, key=f"main_{category}_{item}")
                if category not in progress:
                    progress[category] = {}
                progress[category][item] = checked

        if st.button("체크리스트 저장"):
            save_daily_progress(st.session_state.username, str(today), progress)
            st.success("오늘의 체크리스트가 저장되었습니다!")

    with col2:
        # 진행 상황 요약
        st.subheader("진행 상황 요약")
        total_items = sum(len(items) for items in checklist_data.values())
        checked_items = sum(sum(category.values()) for category in progress.values())
        progress_percentage = (checked_items / total_items) * 100 if total_items > 0 else 0
        
        st.progress(progress_percentage / 100)
        st.write(f"오늘의 진행률: {progress_percentage:.1f}%")

        # 최근 7일간의 진행 상황
        st.subheader("최근 7일간의 진행 상황")
        end_date = today
        start_date = end_date - timedelta(days=6)
        history_df = get_progress_history(st.session_state.username, str(start_date), str(end_date))
        if not history_df.empty:
            fig = px.line(history_df, x='date', y='completion_rate', color='category', title='카테고리별 진행 상황')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("최근 7일간의 데이터가 없습니다.")

    # 최근 성찰 내용
    st.subheader("최근 성찰")
    recent_reflection = get_recent_reflection(st.session_state.username)
    if recent_reflection:
        st.write(f"**날짜:** {recent_reflection['date']}")
        st.write(f"**성취:** {recent_reflection['achievements']}")
        st.write(f"**개선점:** {recent_reflection['improvements']}")
        st.write(f"**내일의 목표:** {recent_reflection['tomorrow_goals']}")
    else:
        st.info("최근 성찰 내용이 없습니다.")

    # 오늘의 성찰 입력
    st.subheader("오늘의 성찰")
    achievements = st.text_area("오늘의 성취:")
    improvements = st.text_area("개선이 필요한 부분:")
    tomorrow_goals = st.text_area("내일의 주요 목표:")
    
    if st.button("성찰 저장"):
        save_reflection(st.session_state.username, str(today), achievements, improvements, tomorrow_goals)
        st.success("오늘의 성찰이 저장되었습니다!")

    # 빠른 링크
    st.subheader("빠른 링크")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("체크리스트 관리"):
            st.session_state.current_page = "checklist_management"
            st.experimental_rerun()
    with col2:
        if st.button("상세 분석"):
            st.session_state.current_page = "detailed_analysis"
            st.experimental_rerun()
    with col3:
        if st.button("알림 설정"):
            st.session_state.current_page = "notification_settings"
            st.experimental_rerun()
    with col4:
        if st.button("데이터 관리"):
            st.session_state.current_page = "data_management"
            st.experimental_rerun()

# 필요한 추가 함수들
def get_recent_reflection(username):
    # 데이터베이스에서 최근 성찰 내용을 가져오는 함수
    # 이 함수는 database.py에 구현되어야 합니다
    pass

def save_reflection(username, date, achievements, improvements, tomorrow_goals):
    # 성찰 내용을 데이터베이스에 저장하는 함수
    # 이 함수는 database.py에 구현되어야 합니다
    pass

# 메인 실행 로직
if __name__ == "__main__":
    st.set_page_config(page_title="50+ 일일 웰니스 체크리스트", layout="wide")
    if 'username' not in st.session_state or st.session_state.username is None:
        login_register()
    else:
        main_screen()