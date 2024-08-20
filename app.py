import streamlit as st
from database import init_db, get_checklist_items, add_checklist_item, remove_checklist_item, save_daily_progress, get_daily_progress, get_progress_history, save_notification, get_notifications, remove_notification
from auth import register_user, authenticate_user
from typing import TypedDict, NotRequired
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

# 데이터베이스 초기화
init_db()

class ReflectionData(TypedDict):
    date: str
    achievements: str
    improvements: str
    tomorrow_goals: str

class ProgressData(TypedDict):
    date: str
    category: str
    completion_rate: float

def login_page():
    st.title("로그인")
    username = st.text_input("사용자 이름")
    password = st.text_input("비밀번호", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인"):
            if authenticate_user(username, password):
                st.session_state.username = username
                st.success("로그인 성공!")
                st.session_state.page = "main"
                st.experimental_rerun()
            else:
                st.error("잘못된 사용자 이름 또는 비밀번호입니다.")
    with col2:
        if st.button("회원가입"):
            st.session_state.page = "register"
            st.experimental_rerun()

def register_page():
    st.title("회원가입")
    username = st.text_input("사용자 이름")
    password = st.text_input("비밀번호", type="password")
    confirm_password = st.text_input("비밀번호 확인", type="password")
    if st.button("가입하기"):
        if password != confirm_password:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            success, message = register_user(username, password)
            if success:
                st.success(message)
                st.session_state.page = "login"
                st.experimental_rerun()
            else:
                st.error(message)
    if st.button("로그인 페이지로 돌아가기"):
        st.session_state.page = "login"
        st.experimental_rerun()

def main_screen():
    st.set_page_config(page_title="50+ 일일 웰니스 대시보드", layout="wide")
    st.title("50+ 일일 웰니스 대시보드")
    
    today: datetime = datetime.now()
    st.subheader(f"오늘 날짜: {today:%Y년 %m월 %d일}")

    col1, col2 = st.columns(2)

    with col1:
        display_checklist()

    with col2:
        display_progress_summary()

    display_reflection()
    display_quick_links()

def display_checklist():
    st.subheader("오늘의 체크리스트")
    checklist_data: dict[str, list[str]] = get_checklist_items(st.session_state.username)
    progress: dict[str, dict[str, bool]] = {}
    
    for category, items in checklist_data.items():
        st.write(f"**{category}**")
        progress[category] = {
            item: st.checkbox(item, key=f"main_{category}_{item}")
            for item in items
        }

    if st.button("체크리스트 저장"):
        save_daily_progress(st.session_state.username, f"{datetime.now():%Y-%m-%d}", progress)
        st.success("오늘의 체크리스트가 저장되었습니다!")

def display_progress_summary():
    st.subheader("진행 상황 요약")
    progress: dict[str, dict[str, bool]] = get_daily_progress(st.session_state.username, f"{datetime.now():%Y-%m-%d}")
    
    total_items: int = sum(len(items) for items in progress.values())
    checked_items: int = sum(sum(item for item in category.values()) for category in progress.values())
    progress_percentage: float = (checked_items / total_items * 100) if total_items > 0 else 0
    
    st.progress(progress_percentage / 100)
    st.write(f"오늘의 진행률: {progress_percentage:.1f}%")

    display_weekly_progress()

def display_weekly_progress():
    st.subheader("최근 7일간의 진행 상황")
    end_date: datetime = datetime.now()
    start_date: datetime = end_date - timedelta(days=6)
    history: List[ProgressData] = get_progress_history(st.session_state.username, f"{start_date:%Y-%m-%d}", f"{end_date:%Y-%m-%d}")
    
    if history:
        df = pd.DataFrame(history)
        fig = px.line(df, x='date', y='completion_rate', color='category', title='카테고리별 진행 상황')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("최근 7일간의 데이터가 없습니다.")

def display_reflection():
    st.subheader("오늘의 성찰")
    achievements: str = st.text_area("오늘의 성취:")
    improvements: str = st.text_area("개선이 필요한 부분:")
    tomorrow_goals: str = st.text_area("내일의 주요 목표:")
    
    if st.button("성찰 저장"):
        save_reflection(st.session_state.username, f"{datetime.now():%Y-%m-%d}", achievements, improvements, tomorrow_goals)
        st.success("오늘의 성찰이 저장되었습니다!")

    st.subheader("최근 성찰")
    recent_reflection: NotRequired[ReflectionData] = get_recent_reflection(st.session_state.username)
    
    if recent_reflection:
        st.write(f"**날짜:** {recent_reflection['date']}")
        st.write(f"**성취:** {recent_reflection['achievements']}")
        st.write(f"**개선점:** {recent_reflection['improvements']}")
        st.write(f"**내일의 목표:** {recent_reflection['tomorrow_goals']}")
    else:
        st.info("최근 성찰 내용이 없습니다.")

def display_quick_links():
    st.subheader("빠른 링크")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("체크리스트 관리"):
            st.session_state.page = "checklist_management"
    with col2:
        if st.button("상세 분석"):
            st.session_state.page = "detailed_analysis"
    with col3:
        if st.button("알림 설정"):
            st.session_state.page = "notification_settings"
    with col4:
        if st.button("데이터 관리"):
            st.session_state.page = "data_management"
    
    if st.button("로그아웃"):
        st.session_state.clear()
        st.experimental_rerun()

def checklist_management():
    st.title("체크리스트 관리")
    # 체크리스트 관리 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"
        st.experimental_rerun()

def detailed_analysis():
    st.title("상세 분석")
    # 상세 분석 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"
        st.experimental_rerun()

def notification_settings():
    st.title("알림 설정")
    # 알림 설정 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"
        st.experimental_rerun()

def data_management():
    st.title("데이터 관리")
    # 데이터 관리 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"
        st.experimental_rerun()

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
    elif st.session_state.page == "main":
        if 'username' in st.session_state:
            main_screen()
        else:
            st.error("로그인이 필요합니다.")
            st.session_state.page = "login"
            st.experimental_rerun()
    elif st.session_state.page == "checklist_management":
        checklist_management()
    elif st.session_state.page == "detailed_analysis":
        detailed_analysis()
    elif st.session_state.page == "notification_settings":
        notification_settings()
    elif st.session_state.page == "data_management":
        data_management()

if __name__ == "__main__":
    main()