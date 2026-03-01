import streamlit as st
import pandas as pd
import io
import os
from fpdf import FPDF

# 앱 설정
st.set_page_config(page_title="ERP Enterprise v4", layout="wide")

# --- 1. 데이터 관리 함수 ---
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
if 'orders' not in st.session_state:
    st.session_state.orders = load_data('orders.csv', ["주문ID", "주문일시", "고객명", "제품명", "주문수량", "총액"])
if 'customers' not in st.session_state:
    st.session_state.customers = load_data('customers.csv', ["고객명", "연락처", "메모"])

# --- 2. 원격 접속 권한 및 로그인 ---
def login():
    st.markdown("### 🌐 비즈니스 원격 접속 포털")
    with st.form("login_form"):
        user_id = st.text_input("아이디")
        user_pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("접속하기"):
            # 권한 예시 (추후 데이터베이스 연동 가능)
            if user_id == "admin" and user_pw == "master123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()
            elif user_id == "staff" and user_pw == "staff123":
                st.session_state.logged_in = True
                st.session_state.role = "staff"
                st.rerun()
            else:
                st.error("잘못된 접근 권한입니다.")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# --- 3. PDF 전표 생성 함수 ---
def generate_pdf(order_data):
    pdf = FPDF()
    pdf.add_page()
    # 폰트 설정 (한글 폰트가 경로에 있어야 함, 여기선 기본 폰트 사용)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="SALES RECEIPT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Order ID: {order_data['주문ID']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {order_data['주문일시']}", ln=True)
    pdf.cell(200, 10, txt=f"Customer: {order_data['고객명']}", ln=True)
    pdf.cell(200, 10, txt=f"Product: {order_data['제품명']}", ln=True)
    pdf.cell(200, 10, txt=f"Quantity: {order_data['주문수량']} EA", ln=True)
    pdf.cell(200, 10, txt=f"Total: {order_data['총액']:,} KRW", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. 메인 대시보드 ---
st.sidebar.success(f"접속 중: {st.session_state.role.upper()} 계정")
if st.sidebar.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 대시보드", "📦 재고/입고", "👥 고객관리", "🛒 주문/출고", "📄 전표출력", "📥 내보내기"
])

# --- 탭 1: 주문 및 출고 ---
with tab1:
    st.header("실시간 주문 처리")
    # (이전의 주문 관리 코드 유지...)
    # 생략된 부분은 이전 답변의 주문 로직과 동일합니다.

# --- 탭 2: PDF 전표 발행 (핵심 추가) ---
with tab2:
    st.header("📄 공식 전표 PDF 다운로드")
    if st.session_state.orders.empty:
        st.warning("내역이 없습니다.")
    else:
        selected_order = st.selectbox("전표 대상 선택", st.session_state.orders["주문ID"])
        order_row = st.session_state.orders[st.session_state.orders["주문ID"] == selected_order].iloc[0]
        
        pdf_bytes = generate_pdf(order_row)
        st.download_button(
            label="📥 PDF 전표 다운로드",
            data=pdf_bytes,
            file_name=f"receipt_{selected_order}.pdf",
            mime="application/pdf"
        )

# --- 탭 3: 시스템 설정 (관리자 전용) ---
with tab3:
    st.header("시스템 관리 권한")
    if st.session_state.role == "admin":
        st.write("✅ 당신은 모든 데이터에 접근하고 수정할 수 있는 **관리자**입니다.")
        if st.button("모든 데이터 초기화 (주의)"):
            st.warning("데이터를 삭제하시겠습니까?")
            # 초기화 로직...
    else:

        st.error("⛔ 스태프 계정은 시스템 설정에 접근할 수 없습니다.")
