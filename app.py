import streamlit as st

# 1. ตั้งค่าหน้าตาของแอป Streamlit ให้เป็นแบบขยายเต็มจอ (Wide Layout)
st.set_page_config(page_title="Plan B Email Generator", layout="wide")

# 2. อ่านโค้ด HTML ทั้งหมดจากไฟล์ card_template.html
try:
    with open("card_template.html", "r", encoding="utf-8") as f:
        html_template = f.read()
except FileNotFoundError:
    html_template = "<h1>ไม่พบไฟล์ card_template.html กรุณาตรวจสอบบน GitHub</h1>"

# 3. แสดงหัวข้อบนหน้าแอป Streamlit
st.title("📧 Plan B Media - Email Card Generator [Credential]")

# 4. สร้าง Sidebar แถบข้างซ้าย สำหรับให้คุณพลอยพิมพ์เปลี่ยนชื่อลูกค้า
st.sidebar.header("📝 ข้อมูลลูกค้า (Client Info)")
client_name = st.sidebar.text_input("ชื่อลูกค้า / ผู้ติดต่อ", "คุณ P")
client_company = st.sidebar.text_input("ชื่อบริษัทลูกค้า", "P")
credential_drive_link = st.sidebar.text_input(
    "ลิงก์ Google Drive Credential", 
    "https://drive.google.com/drive/folders/1cIs047U-1o39IIn_AawS426Jd-bWq12u"
)

# 5. นำชื่อลูกค้าและลิงก์ Drive ที่พิมพ์ มาแทนที่ในแม่แบบ HTML
rendered_html = (
    html_template
    .replace("{client_name}", client_name)
    .replace("{client_company}", client_company)
    .replace("{credential_drive_link}", credential_drive_link)
)

# 6. แสดงผลตัวอย่างการ์ดอีเมล (Preview) บนหน้าจอ Streamlit
st.components.v1.html(rendered_html, height=1200, scrolling=True)

# 7. กล่องสำหรับก๊อปปี้โค้ด HTML ไปใช้ส่งอีเมลจริง
st.subheader("📋 Copy HTML Code สำหรับนำไปใช้ส่งอีเมล")
st.code(rendered_html, language="html")
