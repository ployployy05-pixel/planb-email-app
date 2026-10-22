import streamlit as st

st.set_page_config(page_title="Plan B Email Generator", layout="wide")

# อ่านไฟล์ HTML Template
try:
    with open("card_template.html", "r", encoding="utf-8") as f:
        html_template = f.read()
except FileNotFoundError:
    html_template = "<h1>ไม่พบไฟล์ card_template.html กรุณาตรวจสอบบน GitHub</h1>"

st.title("📧 Plan B Media - Email Card Generator [Credential]")

# Sidebar สำหรับกรอกข้อมูลลูกค้า
st.sidebar.header("📝 ข้อมูลลูกค้า (Client Info)")
client_name = st.sidebar.text_input("ชื่อลูกค้า / ผู้ติดต่อ", "คุณ P")
client_company = st.sidebar.text_input("ชื่อบริษัทลูกค้า", "P")
credential_drive_link = st.sidebar.text_input(
    "ลิงก์ Google Drive Credential", 
    "https://drive.google.com/drive/folders/1cIs047U-1o39IIn_AawS426Jd-bWq12u"
)

# Render HTML
rendered_html = html_template.format(
    client_name=client_name,
    client_company=client_company,
    credential_drive_link=credential_drive_link
)

# แสดงผล Preview ในหน้า Streamlit
st.components.v1.html(rendered_html, height=1200, scrolling=True)

# ปุ่ม Copy HTML Code
st.subheader("📋 Copy HTML Code สำหรับนำไปใช้ส่งอีเมล")
st.code(rendered_html, language="html")
