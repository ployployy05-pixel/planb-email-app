import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Email Dispatcher Pro",
    page_icon="📬",
    layout="centered"
)

# ตกแต่ง CSS เพิ่มความสวยงาม
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 48px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
        color: white;
    }
    .email-card {
        background-color: #F8F9FA;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E9ECEF;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar ตกแต่งด้านข้าง
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/732/732200.png", width=70)
    st.title("📌 คำแนะนำการใช้งาน")
    st.info("""
    1. ระบุอีเมลผู้รับให้ถูกต้อง
    2. กรอกหัวข้อและข้อความ
    3. กดปุ่ม **ส่งอีเมล** ด้านล่าง
    """)
    st.divider()
    st.caption("🚀 Powered by Streamlit & Gmail SMTP")

# ส่วนหัวหลัก
st.markdown("<h1 style='text-align: center; color: #1E293B;'>📧 ระบบส่งอีเมลอัตโนมัติ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>บริการส่งอีเมลสะดวกรวดเร็วผ่าน Gmail API</p>", unsafe_allow_html=True)
st.write("")

# ดึงค่า Secrets
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")

# ฟอร์มรับข้อมูลแบบใส่ Card
with st.container():
    st.markdown("<div class='email-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        to_email = st.text_input("📮 อีเมลผู้รับ:", placeholder="example@gmail.com")
    with col2:
        subject = st.text_input("🏷️ หัวข้อเรื่อง:", placeholder="ใส่หัวข้ออีเมลที่นี่")
        
    message_body = st.text_area("📝 ข้อความ:", height=180, placeholder="พิมพ์ข้อความที่คุณต้องการส่งที่นี่...")
    
    st.write("")
    send_btn = st.button("🚀 ส่งอีเมลทันที", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ระบบประมวลผลการส่งอีเมล
if send_btn:
    if not to_email or not subject or not message_body:
        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่องก่อนกดส่งนะคะ")
    elif not GMAIL_USER or not EMAIL_PASSWORD:
        st.error("❌ ยังไม่ได้ตั้งค่า Secrets (GMAIL_USER / EMAIL_PASSWORD)")
    else:
        with st.spinner("กำลังทำการส่งอีเมล กรุณารอสักครู่..."):
            try:
                msg = MIMEMultipart()
                msg['From'] = GMAIL_USER
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message_body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(GMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
                server.quit()

                st.balloons() # เอฟเฟกต์ลูกโป่งลอยฉลอง
                st.success(f"🎉 ส่งอีเมลไปยัง **{to_email}** เรียบร้อยแล้วค่ะ!")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการส่งอีเมล: {e}")
