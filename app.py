import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pandas as pd
import streamlit as st

# ==========================================
# 1. การตั้งค่าหน้าตาเว็บ (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="Plan B Media • Automation System Email",
    page_icon="✉️",
    layout="wide",
)

# ==========================================
# 2. แถบตั้งค่าด้านซ้าย (Sidebar Configuration)
# ==========================================
st.sidebar.header("⚙️ ข้อมูลผู้ส่ง (Plan B Media)")

sender_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง", value="วิชญาดา (พลอย)")
sender_email = st.sidebar.text_input(
    "อีเมลองค์กร", value="wichayada.ph@planbmedia.co.th"
)
sender_phone = st.sidebar.text_input("เบอร์โทรศัพท์", value="064-542-4441")

st.sidebar.markdown("---")
st.sidebar.header("🔑 Gmail OAuth 2.0 Credentials")

client_id = st.sidebar.text_input(
    "Google Client ID",
    type="password",
    help="วาง Client ID ที่ได้จาก Google Cloud Console (Desktop App)",
)

client_secret = st.sidebar.text_input(
    "Google Client Secret",
    type="password",
    help="วาง Client Secret ที่ได้จาก Google Cloud Console",
)

refresh_token = st.sidebar.text_input(
    "Refresh Token",
    value="1//04EXnnYDt12VjCgYIARAAGAQSSQF-L9IrKPOhl9XbvnQ1ztXN8tzT9QAlnSx5EX3XpBIm-f3IueKK5CDcHJJQtUyf-dmvNLRc0LtStd-g16OOxYwBUgz0kEg6SGE",
    type="password",
    help=" Refresh Token ที่ดึงมาจาก OAuth Playground",
)

st.sidebar.markdown("---")
step_option = st.sidebar.radio(
    "เลือกขั้นตอน:",
    [
        "STEP 01 : จัดการรายชื่อลูกค้า",
        "STEP 02 : เลือกเนื้อหา & พรีวิว",
        "STEP 03 : ยืนยันยอด & กดส่งอีเมล",
    ],
    index=2,
)

media_type = st.sidebar.selectbox(
    "เลือกประเภทอีเมลที่ต้องการส่ง:", ["1. New Media (เสนอขายแพ็กเกจ)"]
)


# ==========================================
# 3. ฟังก์ชันส่งอีเมลด้วย Gmail API (OAuth 2.0)
# ==========================================
def send_email_via_gmail_api(
    client_id, client_secret, refresh_token, sender_email, to_email, subject, body
):
    try:
        # สร้าง Credentials object จาก Refresh Token
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )

        # สร้าง Service เชื่อมต่อกับ Gmail API
        service = build("gmail", "v1", credentials=creds)

        # สร้างโครงสร้างข้อมูลอีเมล (MIME)
        message = MIMEMultipart()
        message["to"] = to_email
        message["from"] = f"{sender_name} <{sender_email}>"
        message["subject"] = subject
        message.attach(MIMEText(body, "html"))

        # แปลงข้อมูลเป็น Base64 แบบ URL Safe ตามข้อกำหนดของ Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body_payload = {"raw": raw_message}

        # ยิงส่งอีเมลผ่าน API
        service.users().messages().send(userId="me", body=body_payload).execute()
        return True, "ส่งอีเมลสำเร็จแล้ว!"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการส่งอีเมล: {str(e)}"


# ==========================================
# 4. ส่วนแสดงผลเนื้อหาหลัก (Main Content Area)
# ==========================================
st.title("📣 PLAN B MEDIA • AUTOMATION SYSTEM EMAIL")
st.caption(
    "Powered by Google Gemini 1.5 Flash API | AI Integration Level 4 System"
)

if "STEP 03" in step_option:
    st.header("🚀 STEP 03 : Review & Batch Sending [New]")

    # แสดง KPI Cards ด้านบน
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนผู้รับหลัก (To)", "1 ราย")
    col2.metric("มีการ CC อีเมล", "0 ราย")
    col3.metric("โหมดที่ใช้ส่ง", "New Media")

    st.markdown("---")
    st.subheader("📋 ตารางสรุปรายชื่อที่จะจัดส่งใน Batch นี้")

    # ตารางจำลองรายชื่อผู้รับ
    sample_data = {
        "ลำดับ": [0],
        "แบรนด์ / บริษัท": ["P"],
        "ผู้ติดต่อ": ["-"],
        "อีเมลผู้รับ (To)": ["wichayada.ph@planbmedia.co.th"],
        "CC Email": ["-"],
        "สื่อ OOH ที่ AI เลือก": ["The 20"],
    }
    df = pd.DataFrame(sample_data)
    st.dataframe(df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ปุ่มกดส่งอีเมล
    if st.button(
        "🚀 ยืนยันส่งอีเมลหาลูกค้า 1 รายนี้ทันที (Send Batch Emails)",
        use_container_width=True,
        type="primary",
    ):
        if not client_id or not client_secret or not refresh_token:
            st.error(
                "❌ กรุณากรอก Client ID, Client Secret และ Refresh Token ใน Sidebar ด้านซ้ายให้ครบถ้วนก่อนส่งค่ะ"
            )
        else:
            with st.spinner("กำลังส่งอีเมลผ่าน Gmail API..."):
                # รายละเอียดอีเมลทดสอบ
                to_email = "wichayada.ph@planbmedia.co.th"
                subject = "เสนอขายแพ็กเกจสื่อโฆษณา Plan B Media"
                email_body = f"""
                <h3>เรียน ผู้สมัคร/ลูกค้า</h3>
                <p>นี่คืออีเมลทดสอบระบบส่งอัตโนมัติ Plan B Media Automation System</p>
                <p><b>ผู้ส่ง:</b> {sender_name} ({sender_phone})</p>
                """

                # เรียกใช้งานฟังก์ชันส่งอีเมล
                success, msg = send_email_via_gmail_api(
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=refresh_token,
                    sender_email=sender_email,
                    to_email=to_email,
                    subject=subject,
                    body=email_body,
                )

                if success:
                    st.success("✅ ส่งอีเมลสำเร็จเรียบร้อยแล้ว!")
                else:
                    st.error(f"❌ {msg}")
