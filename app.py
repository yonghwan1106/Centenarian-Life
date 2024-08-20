import streamlit as st
from database import init_db, get_checklist_items, add_checklist_item, remove_checklist_item, save_daily_progress, get_daily_progress, get_progress_history, save_notification, get_notifications, remove_notification, save_reflection, get_recent_reflection
from auth import register_user, authenticate_user
from typing import TypedDict, NotRequired, List, Dict
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
                st.session_state.page = "main"
                st.success("로그인 성공!")
            else:
                st.error("잘못된 사용자 이름 또는 비밀번호입니다.")
    with col2:
        if st.button("회원가입"):
            st.session_state.page = "register"

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
            else:
                st.error(message)
    if st.button("로그인 페이지로 돌아가기"):
        st.session_state.page = "login"

def main_screen():
    st.set_page_config(page_title="50+ 일일 웰니스 대시보드", layout="wide")
    st.title("50+ 일일 웰니스 체크리스트 및 계획")
    
    today: datetime = datetime.now()
    st.subheader(f"오늘 날짜: {today:%Y년 %m월 %d일}")

    display_checklist()
    display_progress_summary()
    display_reflection()
    display_quick_links()

def display_checklist():
    checklist_data: Dict[str, List[str]] = {
        "건강 관리": [
            "아침 체조 또는 스트레칭 (10-15분)",
            "30분 이상 중강도 운동 (걷기, 수영, 자전거 등)",
            "8잔 이상의 물 섭취",
            "균형 잡힌 식사 3회 (채소, 단백질, 전곡류 포함)",
            "복용 약물 체크 및 섭취",
            "혈압/혈당 측정 (해당 시)",
            "충분한 수면 (7-8시간 목표)"
        ],
        "재정 관리": [
            "일일 지출 기록",
            "예산 대비 지출 확인",
            "투자 포트폴리오 점검 (주 1회)",
            "재정 목표 진행 상황 검토 (월 1회)"
        ],
        "관계 유지": [
            "가족/친구와 연락 (전화, 문자, 이메일 등)",
            "대면 만남 계획 또는 실행 (주 1-2회)",
            "새로운 사회적 연결 모색 (동호회, 봉사활동 등)"
        ],
        "지속적 학습과 성장": [
            "새로운 기술/지식 학습 (30분-1시간)",
            "독서 (30분 이상)",
            "온라인 강좌 또는 워크샵 참여 (주 1-2회)"
        ],
        "취미 및 여가 활동": [
            "즐거운 취미 활동 (1시간 이상)",
            "새로운 경험 계획 (월 1회 이상)",
            "문화 활동 참여 (영화, 전시회 등, 월 1-2회)"
        ],
        "사회적 참여와 기여": [
            "지역 사회 활동 또는 봉사 계획/참여 (주 1회 이상)",
            "멘토링 또는 지식 공유 활동 (해당 시)"
        ],
        "정신적 웰빙": [
            "명상 또는 마음 챙김 실천 (15-20분)",
            "감사일기 작성",
            "스트레스 관리 기법 실천 (심호흡, 점진적 근육 이완 등)"
        ],
        "긍정적 마인드셋": [
            "하루 3가지 긍정적인 일 찾기",
            "자기 긍정 확언 실천",
            "개인 성장 목표 점검 및 조정"
        ],
        "일과 삶의 균형": [
            "업무 시간과 개인 시간 구분 짓기",
            "휴식과 회복 시간 확보",
            "주간 일정 검토 및 조정"
        ],
        "주거 환경 관리": [
            "간단한 집안 정리정돈 (15-20분)",
            "환기 및 실내 공기질 관리",
            "안전 점검 (화재경보기, 잠금장치 등, 월 1회)"
        ]
    }
    
    progress: Dict[str, Dict[str, bool]] = {}
    
    for category, items in checklist_data.items():
        st.subheader(f"{category}")
        progress[category] = {}
        for item in items:
            key = f"{category}_{item}"
            checked = st.checkbox(item, key=key)
            progress[category][item] = checked

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
        st.session_state.page = "login"

def checklist_management():
    st.title("체크리스트 관리")
    # 체크리스트 관리 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"

def detailed_analysis():
    st.title("상세 분석")
    # 상세 분석 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"

def notification_settings():
    st.title("알림 설정")
    # 알림 설정 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"

def data_management():
    st.title("데이터 관리")
    # 데이터 관리 기능 구현
    if st.button("메인 화면으로 돌아가기"):
        st.session_state.page = "main"

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "login"

    # 페이지 전환 로직
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