import streamlit as st
import pandas as pd
import os

# 1. 기본 설정
st.set_page_config(page_title="ERP v7", layout="wide")

# 2. 데이터 관리 함수
def load_data(file_name, columns):
    if os.path.exists(file_name): return pd.read_csv(file_name)
    return pd.DataFrame(columns=columns)

def save_data(df, file_name):
    df.to_csv(file_name, index=False, encoding='utf-8-sig')

# 3. 데이터 초기화
if 'inventory' not in st.session_state: st.session_state.inventory = load_data('inventory.csv', ["제품명", "수량", "가격"])
if 'customers' not in st.session_state: st.session_state.customers = load_data('customers.csv', ["고객명", "연락처", "생년월일", "메모"])
if 'orders' not in st.session_state: st.session_state.orders = load_data('orders.csv', ["주문ID", "주문일시", "고객명", "제품명", "수량", "할인율", "최종금액"])
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# 4. 로그인 체크
if not st.session_state.logged_in:
    st.title("🔐 관리자 로그인")
    u_id = st.text_input("아이디")
    u_pw = st.text_input("비밀번호", type="password")
    if st.button("접속하기", use_container_width=True):
        if u_id == "admin" and u_pw == "master123":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# 5. 메인 메뉴 (이 순서가 중요합니다!)
st.sidebar.write("접속: 관리자")
tabs = st.tabs(["📦 재고/입고", "👥 고객관리", "🛒 주문/출고", "📊 현황보기"])

# --- [📦 재고/입고] 탭 ---
with tabs[0]:
    st.subheader("건강식품 입고 등록")
    # 입력창이 바로 보이도록 설정
    with st.form("inv_form"):
        name = st.text_input("제품명 (예: 홍삼)")
        stock = st.number_input("입고 수량", min_value=0, step=1)
        price = st.number_input("판매 단가", min_value=0, step=100)
        if st.form_submit_button("입고 완료"):
            new_inv = pd.DataFrame({"제품명": [name], "수량": [stock], "가격": [price]})
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_inv], ignore_index=True)
            save_data(st.session_state.inventory, 'inventory.csv')
            st.success("등록되었습니다!")
            st.rerun()
    st.write("현재 재고 목록")
    st.dataframe(st.session_state.inventory, use_container_width=True)

# --- [👥 고객관리] 탭 ---
with tabs[1]:
    st.subheader("모임 회원 등록")
    with st.form("cust_form"):
        c_name = st.text_input("이름")
        c_phone = st.text_input("전화번호 (010-0000-0000)")
        c_birth = st.text_input("생일 (예: 800101)")
        c_memo = st.text_area("특이사항 (모임명)")
        if st.form_submit_button("회원 저장"):
            new_c = pd.DataFrame({"고객명": [c_name], "연락처": [c_phone], "생년월일": [c_birth], "메모": [c_memo]})
            st.session_state.customers = pd.concat([st.session_state.customers, new_c], ignore_index=True)
            save_data(st.session_state.customers, 'customers.csv')
            st.success("저장되었습니다!")
            st.rerun()
    st.write("회원 명단")
    st.dataframe(st.session_state.customers, use_container_width=True)

# --- [🛒 주문/출고] 탭 ---
with tabs[2]:
    st.subheader("판매 처리 (할인)")
    if st.session_state.inventory.empty:
        st.warning("재고를 먼저 등록하세요.")
    else:
        with st.form("order_form"):
            s_cust = st.selectbox("고객", st.session_state.customers["고객명"] if not st.session_state.customers.empty else ["미등록"])
            s_item = st.selectbox("제품", st.session_state.inventory["제품명"])
            s_qty = st.number_input("판매 수량", min_value=1)
            s_dc = st.slider("할인율 (%)", 0, 50, 0)
            if st.form_submit_button("판매 확정"):
                st.success("판매가 완료되었습니다!")

# --- [📊 현황보기] 탭 ---
with tabs[3]:
    st.subheader("매출 통계")
    st.dataframe(st.session_state.orders, use_container_width=True)
