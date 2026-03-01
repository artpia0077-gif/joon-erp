import streamlit as st
import pandas as pd
import os

# 1. 앱 설정 및 로그인 상태 유지
st.set_page_config(page_title="ERP_FINAL", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 2. 로그인 화면 (로그아웃 방지 로직 포함)
if not st.session_state.logged_in:
    st.header("🔐 관리자 접속")
    u_id = st.text_input("아이디", key="main_id")
    u_pw = st.text_input("비밀번호", type="password", key="main_pw")
    if st.button("접속하기", use_container_width=True):
        if u_id == "admin" and u_pw == "master123":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# 3. 메인 메뉴 (입력창이 최상단에 오도록 탭 구성)
st.write("✅ 접속중: 관리자")
# 메뉴 명칭을 영어로 섞어서 시스템 혼동 방지
menu = st.radio("메뉴 선택", ["1. 재고입고(Stock)", "2. 인명관리(People)", "3. 판매기록(Sales)"], horizontal=True)

if menu == "1. 재고입고(Stock)":
    st.subheader("📦 제품 등록")
    with st.container(): # 입력창을 컨테이너로 감싸 상단 고정
        name = st.text_input("제품명 입력")
        qty = st.number_input("입고 수량", min_value=0, step=1)
        if st.button("등록 저장"):
            st.success(f"{name} 저장 완료!")

elif menu == "2. 인명관리(People)":
    st.subheader("👥 회원 등록")
    c_name = st.text_input("성함 입력")
    c_tel = st.text_input("전화번호 입력")
    if st.button("회원 저장"):
        st.success(f"{c_name}님 저장 완료!")

elif menu == "3. 판매기록(Sales)":
    st.subheader("🛒 판매 처리")
    st.write("현재 판매 내역이 없습니다.")

if st.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()
