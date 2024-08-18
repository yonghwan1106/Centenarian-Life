import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import init_db, get_checklist_items, add_checklist_item, remove_checklist_item, save_daily_progress, get_daily_progress, get_progress_history, save_notification, get_notifications, remove_notification
from auth import register_user, authenticate_user

# 데이터베이스 초기화
init_db()

# 페이지 설정
st.set_page_config(page_title="50+ 일일 웰니스 체크리스트", layout="wide")

# 세션 상태 초기화
if 'username' not in st.session_state:
    st.session_state.username = None

# 로그인/회원가입 함수
def login_register():
    choice = st.radio("로그인 또는 회원가입", ('로그인', '회원가입'))
    username = st.text_input("사용자명")
    password = st.text_input("비밀번호", type="password")
    
    if choice == '로그인':
        if st.button("로그인"):
            if authenticate_user(username, password):
                st.session_state.username = username
                st.success("로그인 성공!")
                st.experimental_rerun()
            else:
                st.error("잘못된 사용자명 또는 비밀번호입니다.")
    else:
        if st.button("회원가입"):
            register_user(username, password)
            st.success("회원가입 성공! 이제 로그인할 수 있습니다.")

# 메인 애플리케이션
def main():
    st.title("50+ 일일 웰니스 체크리스트")
    
    # 날짜 선택
    selected_date = st.date_input("날짜 선택", datetime.now().date())
    
    # 체크리스트 데이터 가져오기
    checklist_data = get_checklist_items(st.session_state.username)
    
    # 이전 진행 상황 가져오기
    previous_progress = get_daily_progress(st.session_state.username, str(selected_date))
    
    # 체크리스트 표시 및 상태 업데이트
    progress = {}
    for category, items in checklist_data.items():
        st.subheader(category)
        progress[category] = {}
        for item in items:
            checked = st.checkbox(item, key=f"{category}_{item}", 
                                  value=previous_progress.get(category, {}).get(item, False))
            progress[category][item] = checked
    
    # 진행 상황 계산
    total_items = sum(len(items) for items in checklist_data.values())
    checked_items = sum(sum(category.values()) for category in progress.values())
    progress_percentage = (checked_items / total_items) * 100 if total_items > 0 else 0
    
    # 진행 상황 표시
    st.subheader("오늘의 진행 상황")
    st.progress(progress_percentage / 100)
    st.write(f"{progress_percentage:.1f}% 완료")
    
    # 카테고리별 완료율 계산
    category_completion = {category: sum(items.values()) / len(items) * 100 for category, items in progress.items() if len(items) > 0}
    
    # 카테고리별 완료율 차트
    df = pd.DataFrame(list(category_completion.items()), columns=['Category', 'Completion Rate'])
    fig = px.bar(df, x='Category', y='Completion Rate', title='카테고리별 완료율')
    st.plotly_chart(fig)
    
    # 일일 성찰
    st.subheader("일일 성찰")
    achievements = st.text_area("오늘의 성취:")
    improvements = st.text_area("개선이 필요한 부분:")
    tomorrow_goals = st.text_area("내일의 주요 목표:")
    
    # 저장 버튼
    if st.button("오늘의 체크리스트 저장"):
        save_daily_progress(st.session_state.username, str(selected_date), progress)
        st.success("오늘의 체크리스트와 성찰이 저장되었습니다!")
    
    # 맞춤형 체크리스트 항목 관리
    st.subheader("체크리스트 항목 관리")
    new_category = st.text_input("새 카테고리")
    new_item = st.text_input("새 항목")
    if st.button("항목 추가"):
        add_checklist_item(st.session_state.username, new_category, new_item)
        st.success("새 항목이 추가되었습니다!")
        st.experimental_rerun()
    
    remove_category = st.selectbox("카테고리 선택", list(checklist_data.keys()))
    remove_item = st.selectbox("삭제할 항목 선택", checklist_data.get(remove_category, []))
    if st.button("항목 삭제"):
        remove_checklist_item(st.session_state.username, remove_category, remove_item)
        st.success("항목이 삭제되었습니다!")
        st.experimental_rerun()
    
    # 날짜별 데이터 조회 및 비교
    st.subheader("진행 상황 분석")
    start_date = st.date_input("시작 날짜", datetime.now().date() - timedelta(days=7))
    end_date = st.date_input("종료 날짜", datetime.now().date())
    if start_date <= end_date:
        history_df = get_progress_history(st.session_state.username, str(start_date), str(end_date))
        fig = px.line(history_df, x='date', y='completion_rate', color='category', title='카테고리별 진행 상황 추이')
        st.plotly_chart(fig)
    else:
        st.error("종료 날짜는 시작 날짜보다 늦어야 합니다.")
    
    # 알림 설정
    st.subheader("알림 설정")
    notification_item = st.selectbox("알림을 설정할 항목", [item for items in checklist_data.values() for item in items])
    notification_time = st.time_input("알림 시간")
    if st.button("알림 설정"):
        save_notification(st.session_state.username, notification_item, str(notification_time))
        st.success("알림이 설정되었습니다!")
    
    # 알림 목록 표시
    notifications = get_notifications(st.session_state.username)
    if notifications:
        st.subheader("설정된 알림")
        for notif in notifications:
            st.write(f"{notif['item']} - {notif['time']}")
            if st.button(f"삭제", key=f"delete_{notif['item']}"):
                remove_notification(st.session_state.username, notif['item'])
                st.experimental_rerun()

# 메인 실행 로직
if st.session_state.username is None:
    login_register()
else:
    st.sidebar.title(f"환영합니다, {st.session_state.username}님!")
    if st.sidebar.button("로그아웃"):
        st.session_state.username = None
        st.experimental_rerun()