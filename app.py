import streamlit as st
from typing import TypedDict, NotRequired
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

class ReflectionData(TypedDict):
    date: str
    achievements: str
    improvements: str
    tomorrow_goals: str

class ProgressData(TypedDict):
    date: str
    category: str
    completion_rate: float

def main_screen() -> None:
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

def display_checklist() -> None:
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

def display_progress_summary() -> None:
    st.subheader("진행 상황 요약")
    progress: dict[str, dict[str, bool]] = get_daily_progress(st.session_state.username, f"{datetime.now():%Y-%m-%d}")
    
    total_items: int = sum(len(items) for items in progress.values())
    checked_items: int = sum(sum(item for item in category.values()) for category in progress.values())
    progress_percentage: float = (checked_items / total_items * 100) if total_items > 0 else 0
    
    st.progress(progress_percentage / 100)
    st.write(f"오늘의 진행률: {progress_percentage:.1f}%")

    display_weekly_progress()

def display_weekly_progress() -> None:
    st.subheader("최근 7일간의 진행 상황")
    end_date: datetime = datetime.now()
    start_date: datetime = end_date - timedelta(days=6)
    history_df: pd.DataFrame = get_progress_history(st.session_state.username, f"{start_date:%Y-%m-%d}", f"{end_date:%Y-%m-%d}")
    
    if not history_df.empty:
        fig = px.line(history_df, x='date', y='completion_rate', color='category', title='카테고리별 진행 상황')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("최근 7일간의 데이터가 없습니다.")

def display_reflection() -> None:
    st.subheader("최근 성찰")
    recent_reflection: NotRequired[ReflectionData] = get_recent_reflection(st.session_state.username)
    
    if recent_reflection:
        st.write(f"**날짜:** {recent_reflection['date']}")
        st.write(f"**성취:** {recent_reflection['achievements']}")
        st.write(f"**개선점:** {recent_reflection['improvements']}")
        st.write(f"**내일의 목표:** {recent_reflection['tomorrow_goals']}")
    else:
        st.info("최근 성찰 내용이 없습니다.")

    st.subheader("오늘의 성찰")
    achievements: str = st.text_area("오늘의 성취:")
    improvements: str = st.text_area("개선이 필요한 부분:")
    tomorrow_goals: str = st.text_area("내일의 주요 목표:")
    
    if st.button("성찰 저장"):
        save_reflection(st.session_state.username, f"{datetime.now():%Y-%m-%d}", achievements, improvements, tomorrow_goals)
        st.success("오늘의 성찰이 저장되었습니다!")

def display_quick_links() -> None:
    st.subheader("빠른 링크")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("체크리스트 관리"):
            st.session_state.current_page = "checklist_management"
    with col2:
        if st.button("상세 분석"):
            st.session_state.current_page = "detailed_analysis"
    with col3:
        if st.button("알림 설정"):
            st.session_state.current_page = "notification_settings"
    with col4:
        if st.button("데이터 관리"):
            st.session_state.current_page = "data_management"
    
    if st.session_state.current_page != "main":
        st.experimental_rerun()

# 데이터베이스 관련 함수들 (실제 구현 필요)
def get_checklist_items(username: str) -> dict[str, list[str]]:
    # 데이터베이스에서 체크리스트 항목을 가져오는 함수
    pass

def save_daily_progress(username: str, date: str, progress: dict[str, dict[str, bool]]) -> None:
    # 일일 진행 상황을 데이터베이스에 저장하는 함수
    pass

def get_daily_progress(username: str, date: str) -> dict[str, dict[str, bool]]:
    # 데이터베이스에서 일일 진행 상황을 가져오는 함수
    pass

def get_progress_history(username: str, start_date: str, end_date: str) -> pd.DataFrame:
    # 데이터베이스에서 진행 상황 히스토리를 가져오는 함수
    pass

def get_recent_reflection(username: str) -> NotRequired[ReflectionData]:
    # 데이터베이스에서 최근 성찰 내용을 가져오는 함수
    pass

def save_reflection(username: str, date: str, achievements: str, improvements: str, tomorrow_goals: str) -> None:
    # 성찰 내용을 데이터베이스에 저장하는 함수
    pass

if __name__ == "__main__":
    if 'username' not in st.session_state or st.session_state.username is None:
        st.error("로그인이 필요합니다.")
    else:
        main_screen()