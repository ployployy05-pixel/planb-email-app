import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="PLAN B MEDIA • AUTOMATION SYSTEM EMAIL",
    page_icon="📧",
    layout="wide"
)

st.title("📢 PLAN B MEDIA • AUTOMATION SYSTEM EMAIL")
st.caption("🤖 Powered by Google Gemini 1.5 Flash API | AI Integration Level 4 System")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ ข้อมูลผู้ส่ง (Plan B Media)")

sender_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง", value="วิชญาดา (พลอย)")
sender_email = st.sidebar.text_input("อีเมลองค์กร", value="wichayada.ph@planbmedia.co.th")
sender_phone = st.sidebar.text_input("เบอร์โทรศัพท์", value="064-542-4441")

gmail_sender = st.sidebar.text_input("บัญชี Gmail ที่ใช้ส่ง", value="wichayada.ph@gmail.com")
sender_password = st.sidebar.text_input("Google App Password", value="", type="password")

sheet_url = st.sidebar.text_input("Google Sheet URL", value="https://docs.google.com/spreadsheet")

step_choice = st.sidebar.radio(
    "เลือกขั้นตอน:",
    ["STEP 01 : จัดการรายชื่อลูกค้า", "STEP 02 : เลือกเนื้อหา & พรีวิว", "STEP 03 : ยืนยันยอด & กดส่งอีเมล"]
)

email_type = st.sidebar.selectbox(
    "เลือกประเภทอีเมลที่ต้องการส่ง:",
    ["1️⃣ New Media (เสนอขายแพ็กเกจ)", "2️⃣ Proposal Follow-up", "3️⃣ Monthly Report"]
)

# --- HELPER FUNCTION: STANDARD SMTP EMAIL SENDER ---
def send_batch_email(sender_email_addr, password, to_email, subject, body_html, cc_email=None):
    msg = MIMEMultipart('alternative')
    msg['From'] = f"{sender_name} <{sender_email_addr}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    if cc_email:
        msg['Cc'] = cc_email

    msg.attach(MIMEText(body_html, 'html'))

    recipients = [to_email]
    if cc_email:
        recipients.append(cc_email)

    # Clean space from app password
    clean_password = str(password).replace(" ", "").strip()
    clean_sender = str(sender_email_addr).strip()

    # Connection strategy: Try Port 587 (TLS) first, then Port 465 (SSL)
    server = None
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(clean_sender, clean_password)
        server.sendmail(clean_sender, recipients, msg.as_string())
        server.quit()
        return True, "ส่งสำเร็จเรียบร้อย (ผ่าน Port 587)"
    except Exception as e_tls:
        if server:
            try:
                server.quit()
            except Exception:
                pass
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20)
            server.login(clean_sender, clean_password)
            server.sendmail(clean_sender, recipients, msg.as_string())
            server.quit()
            return True, "ส่งสำเร็จเรียบร้อย (ผ่าน Port 465)"
        except Exception as e_ssl:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass
            return False, f"TLS: {str(e_tls)} | SSL: {str(e_ssl)}"

# --- MAIN APP LOGIC ---
if "STEP 01" in step_choice:
    st.subheader("📋 STEP 01 : Customer List Management")
    st.info("จัดการรายชื่อลูกค้า และตรวจสอบความถูกต้องของข้อมูลจาก Google Sheets")

elif "STEP 02" in step_choice:
    st.subheader("📝 STEP 02 : Select Content & Preview")
    st.info("เลือก template เนื้อหา และตรวจสอบพรีวิวข้อความที่จะจัดส่ง")

elif "STEP 03" in step_choice:
    st.subheader("🚀 STEP 03 : Review & Batch Sending [New]")

    col1, col2, col3 = st.columns(3)
    col1.metric("✉️ จำนวนผู้รับหลัก (To)", "1 ราย")
    col2.metric("📑 มีการ CC อีเมล", "0 ราย")
    col3.metric("🎯 โหมดที่ใช้ส่ง", "New")

    st.markdown("---")
    st.subheader("📋 ตารางสรุปรายชื่อที่จะจัดส่งใน Batch นี้")

    data = [{
        "ลำดับ": 1,
        "แบรนด์ / บริษัท": "P",
        "ผู้ติดต่อ": "-",
        "อีเมลผู้รับ (To)": "wichayada.ph@planbmedia.co.th",
        "CC Email": "-",
        "สื่อ OOH ที่ AI เลือก": "The 20"
    }]
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 ยืนยันส่งอีเมลหาลูกค้า 1 รายนี้ทันที (Send Batch Emails)", type="primary", use_container_width=True):
        if not sender_password:
            st.error("❌ กรุณากรอก Google App Password ในช่อง Sidebar ก่อนกดส่ง")
        else:
            with st.spinner("กำลังเชื่อมต่อเซิร์ฟเวอร์ SMTP และจัดส่งอีเมล..."):
                target_email = "wichayada.ph@planbmedia.co.th"
                subject = "[Plan B Media] ข้อเสนอแพ็กเกจสื่อโฆษณา OOH พิเศษสำหรับคุณ"
                html_body = f"""
                <h3>เรียน ทีมงาน Plan B Media</h3>
                <p>ทางเราขอนำเสนอแพ็กเกจสื่อโฆษณา <b>The 20</b> สำหรับแคมเปญใหม่ค่ะ</p>
                <br>
                <p>ขอบคุณค่ะ<br><b>{sender_name}</b><br>เบอร์โทร: {sender_phone}</p>
                """
                
                success, log_msg = send_batch_email(
                    sender_email_addr=gmail_sender,
                    password=sender_password,
                    to_email=target_email,
                    subject=subject,
                    body_html=html_body
                )

                if success:
                    st.balloons()
                    st.success(f"✅ {log_msg}")
                else:
                    st.error(f"❌ เกิดข้อผิดพลาดในการส่งอีเมล: {log_msg}")
