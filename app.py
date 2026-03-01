import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# 앱 설정
st.set_page_config(page_title="건강식품 ERP Enterprise v5", layout="wide")

# --- 1. 데이터 로드/저장 함수 ---
def load_data(file_name, columns):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame(columns=columns)

def save_data(df, file_name):
    df.to_csv(file_name, index=False, encoding='utf-8-sig')

# 초기 데이터 로드
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_data('inventory.csv', ["제품명", "수량", "가격"])
if 'customers' not in st.session_state:
    st.session_state.customers = load_data('customers.csv', ["고객명", "연락처", "생년월일", "메모"])
if 'orders' not in st.session_state:
    st.session_state.orders = load_data('orders.csv', ["주문ID", "주문일시", "고객명", "제품명", "수량", "할인율", "최종금액"])

# --- 2. 로그인 시스템 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 비즈니스 원격 접속 포털")
    with st.form("login_form"):
        user_id = st.text_input("아이디")
        user_pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("접속하기"):
            if user_id == "admin" and user_pw == "master123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("권한이 없습니다.")
    st.stop()

# --- 3. 메인 메뉴 (6개 탭 구성) ---
st.sidebar.success(f"접속 중: {st.session_state.role.upper()} 계정")
if st.sidebar.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 대시보드", "📦 재고/입고", "👥 고객관리", "🛒 주문/출고", "📄 전표출력", "📥 내보내기"
])

# --- 탭 0: 대시보드 ---
with tab0:
    st.header("📈 판매 현황 요약")
    if not st.session_state.orders.empty:
        total_sales = st.session_state.orders["최종금액"].sum()
        st.metric("총 누적 매출", f"{total_sales:,} 원")
        st.dataframe(st.session_state.orders.tail(5), use_container_width=True)
    else:
        st.write("아직 판매 데이터가 없습니다.")

# --- 탭 1: 재고/입고 (건강식품 등록) ---
with tab1:
    st.header("📦 건강식품 입고 관리")
    with st.form("in_form"):
        c1, c2, c3 = st.columns(3)
        item = c1.text_input("제품명 (예: 홍삼정)")
        qty = c2.number_input("입고 수량", min_value=1)
        prc = c3.number_input("정상 판매가 (단가)", min_value=0)
        if st.form_submit_button("재고 등록"):
            if item in st.session_state.inventory["제품명"].values:
                st.session_state.inventory.loc[st.session_state.inventory["제품명"] == item, "수량"] += qty
            else:
                new_item = pd.DataFrame({"제품명": [item], "수량": [qty], "가격": [prc]})
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
            save_data(st.session_state.inventory, 'inventory.csv')
            st.success("재고가 반영되었습니다.")
            st.rerun()
    st.dataframe(st.session_state.inventory, use_container_width=True)

# --- 탭 2: 고객관리 (생년월일 및 전화 걸기) ---
with tab2:
    st.header("👥 회원 및 단체 관리")
    with st.form("cust_form"):
        c1, c2, c3 = st.columns(3)
        c_name = c1.text_input("성함")
        c_phone = c2.text_input("연락처 (010-0000-0000)")
        c_birth = c3.date_input("생년월일")
        c_memo = st.text_area("메모 (단체명, 특이사항)")
        if st.form_submit_button("고객 등록"):
            new_cust = pd.DataFrame({"고객명": [c_name], "연락처": [c_phone], "생년월일": [str(c_birth)], "메모": [c_memo]})
            st.session_state.customers = pd.concat([st.session_state.customers, new_cust], ignore_index=True)
            save_data(st.session_state.customers, 'customers.csv')
            st.success("회원 정보가 저장되었습니다.")
            st.rerun()
    
    # 전화 걸기 기능이 포함된 표 출력
    st.subheader("회원 명단 (번호를 누르면 전화 연결)")
    if not st.session_state.customers.empty:
        display_df = st.session_state.customers.copy()
        # 전화번호를 HTML 링크로 변환
        display_df['연락처'] = display_df['연락처'].apply(lambda x: f'<a href="tel:{x}">{x}</a>')
        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write("등록된 회원이 없습니다.")

# --- 탭 3: 주문/출고 (할인율 적용) ---
with tab3:
    st.header("🛒 건강식품 판매 (할인 적용)")
    with st.form("out_form"):
        c1, c2, c3, c4 = st.columns(4)
        sel_cust = c1.selectbox("구매자", st.session_state.customers["고객명"] if not st.session_state.customers.empty else ["등록 필요"])
        sel_item = c2.selectbox("제품선택", st.session_state.inventory["제품명"] if not st.session_state.inventory.empty else ["재고 없음"])
        out_qty = c3.number_input("수량", min_value=1)
        discount = c4.slider("할인율 (%)", 0, 50, 0) # 0% ~ 50% 할인 선택 가능
        
        if st.form_submit_button("판매 확정"):
            item_data = st.session_state.inventory[st.session_state.inventory["제품명"] == sel_item]
            if not item_data.empty and item_data.iloc[0]["수량"] >= out_qty:
                original_price = item_data.iloc[0]["가격"]
                # 할인 계산
                final_unit_price = original_price * (1 - discount/100)
                total_amount = int(final_unit_price * out_qty)
                
                # 재고 차감
                st.session_state.inventory.loc[st.session_state.inventory["제품명"] == sel_item, "수량"] -= out_qty
                
                # 주문 기록
                order_id = f"ORD-{pd.Timestamp.now().strftime('%m%d%H%M%S')}"
                new_order = pd.DataFrame({
                    "주문ID": [order_id], "주문일시": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")],
                    "고객명": [sel_cust], "제품명": [sel_item], "수량": [out_qty], 
                    "할인율": [f"{discount}%"], "최종금액": [total_amount]
                })
                st.session_state.orders = pd.concat([st.session_state.orders, new_order], ignore_index=True)
                
                save_data(st.session_state.inventory, 'inventory.csv')
                save_data(st.session_state.orders, 'orders.csv')
                st.success(f"판매 완료! 최종 금액: {total_amount:,}원")
                st.rerun()
            else:
                st.error("재고가 부족합니다.")
