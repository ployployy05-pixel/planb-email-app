import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Email Sender", page_icon="✉️")

st.title("✉️ ระบบส่งอีเมลอัตโนมัติ")

# ดึงค่า Secrets
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")

to_email = st.text_input("อีเมลผู้รับ:")
subject = st.text_input("หัวข้อเรื่อง:")
message_body = st.text_area("ข้อความ:", height=150)

if st.button("ส่งอีเมล", type="primary"):
    if not to_email or not subject or not message_body:
        st.warning("กรุณากรอกข้อมูลให้ครบทุกช่องค่ะ")
    elif not GMAIL_USER or not EMAIL_PASSWORD:
        st.error("ยังไม่ได้ตั้งค่า Secrets (GMAIL_USER / EMAIL_PASSWORD)")
    else:
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

            st.success("ส่งอีเมลเรียบร้อยแล้วค่ะ! 🎉")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการส่งอีเมล: {e}")
