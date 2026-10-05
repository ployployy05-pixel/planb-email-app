import streamlit as st
import pandas as pd
import re
import smtplib
import requests
import json
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Plan B Media - Automation System Email", page_icon="📢", layout="wide")

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PIMnucnqJmpCdnMLa13_7nuP9lOiEoXuFgVGlW5AGuw/edit?gid=1224436480#gid=1224436480"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ployployy05-pixel/planb-email-app/main/"

# Credentials & Secrets
GMAIL_USER = st.secrets.get("GMAIL_USER", "wichayada.ph@gmail.com")
GMAIL_APP_PASS = st.secrets.get("EMAIL_PASSWORD", "qnkhnriyjsjtyeug").replace(" ", "")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def get_csv_url(sheet_url):
    try:
        sheet_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        sheet_id = sheet_id_match.group(1) if sheet_id_match else sheet_url
        gid_match = re.search(r'gid=([0-9]+)', sheet_url)
        gid = gid_match.group(1) if gid_match else "0"
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    except Exception:
        return None

# ฟังก์ชันดึงรูปภาพจาก GitHub และแปลงเป็น MIMEImage (CID) สำหรับ Outlook
@st.cache_data(show_spinner=False)
def fetch_image_bytes(filename):
    try:
        url = f"{GITHUB_RAW_BASE}{filename}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None

# 🤖 AI RUNTIME FUNCTION (สกัดชื่อและบริษัทตรง 100%)
def generate_ai_personalized_text(client_name, company_name, media_title):
    if not GEMINI_API_KEY:
        display_company = f" {company_name}" if company_name and company_name != "บริษัทลูกค้า" else ""
        return f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง เหมาะอย่างยิ่งสำหรับแบรนด์{display_company} ของคุณ {client_name} ในการสร้างการรับรู้และความประทับใจให้กับกลุ่มเป้าหมายยุคใหม่ค่ะ"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        prompt_text = f"""
        คุณคือ AI Sales Specialist ของบริษัท Plan B Media จำกัด (มหาชน)
        ช่วยแต่งข้อความเกริ่นนำเสนอขายสื่อ OOH สั้นๆ 2 บรรทัด ภาษาไทย สุภาพ เป็นกันเอง และดูเป็นมืออาชีพ
        - ชื่อผู้ติดต่อ: {client_name}
        - ชื่อบริษัท/แบรนด์ลูกค้า: {company_name}
        - สื่อที่เสนอขาย: {media_title}
        เน้นวิเคราะห์ว่าทำไมสื่อ {media_title} ถึงเหมาะกับแบรนด์ {company_name} อย่างยิ่ง (ไม่ต้องใส่เครื่องหมายคำพูด)
        """
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}
        json_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=json_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            generated = result["candidates"][0]["content"]["parts"][0]["text"]
            return generated.strip().replace("\n", "<br>")
    except Exception:
        display_company = f" {company_name}" if company_name and company_name != "บริษัทลูกค้า" else ""
        return f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง เหมาะอย่างยิ่งสำหรับแบรนด์{display_company} ของคุณ {client_name} ในการสร้างการรับรู้และความประทับใจให้กับกลุ่มเป้าหมายค่ะ"

# ==========================================
# SIDEBAR (ฝั่งซ้ายมือ): CONTROL CENTER
# ==========================================
st.sidebar.title("⚙️ ข้อมูลผู้ส่ง (Plan B Media)")
user_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง ({{Sale name}})", value="วิชญาดา (พลอย)")
user_email = st.sidebar.text_input("อีเมลองค์กร (สำหรับลูกค้ารีพลาย)", value="wichayada.ph@planbmedia.co.th")
user_phone = st.sidebar.text_input("เบอร์โทรศัพท์ ({{Tel}})", value="064-542-4441")

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 ตั้งค่าบัญชี Google SMTP Engine")
gmail_sender = st.sidebar.text_input("บัญชี Gmail ที่ใช้ส่ง", value=GMAIL_USER)
sender_password = st.sidebar.text_input("Google App Password (16 หลัก)", value=GMAIL_APP_PASS, type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Google Connection")
sheet_url_input = st.sidebar.text_input("Google Sheet URL (วางลิงก์ทีมอื่นได้)", value=DEFAULT_SHEET_URL)

st.sidebar.markdown("---")
st.sidebar.subheader("🔘 ขั้นตอนการทำงาน")
step = st.sidebar.radio("เลือกขั้นตอน:", [
    "STEP 01 : จัดการรายชื่อลูกค้า",
    "STEP 02 : เลือกเนื้อหา & พรีวิว",
    "STEP 03 : ยืนยันยอด & กดส่งอีเมล"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 รูปแบบเนื้อหาอีเมล")
app_mode = st.sidebar.selectbox(
    "เลือกประเภทอีเมลที่ต้องการส่ง:",
    [
        "1️⃣ New Media (เสนอขายแพ็กเกจสื่อเดิม)",
        "2️⃣ Credential (แนะนำตัวลูกค้าใหม่)",
        "3️⃣ Magnetic Report (รายงานสถิติ OOH ประจำเดือน)"
    ],
    index=0
)

# Session State Initialization
if 'recipients' not in st.session_state:
    st.session_state.recipients = []
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0
if 'ai_generated_pitch' not in st.session_state:
    st.session_state.ai_generated_pitch = ""

# 🖼️ Banner HTML
FOOTER_BANNER_HTML_PREVIEW = f"""
<br><br>
<div style="text-align: center; margin-top: 20px;">
    <img src="{GITHUB_RAW_BASE}footer_banner.jpg" width="600" style="max-width: 100%; height: auto; border-radius: 6px;" alt="Plan B Media Services">
</div>
"""

FOOTER_BANNER_HTML_SEND = """
<br><br>
<div style="text-align: center; margin-top: 20px;">
    <img src="cid:footer_banner" width="600" style="max-width: 100%; height: auto; border-radius: 6px;" alt="Plan B Media Services">
</div>
"""

# ==========================================
# DATA TEMPLATES
# ==========================================

MEDIA_FOLDERS = {
    "rama 9 connected": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
ขอแนะนำ “RAMA 9 Connected” สื่อโฆษณาดิจิทัลใหม่ล่าสุดใจกลาง CBD พระราม 9 ที่พร้อมให้บริการตั้งแต่วันที่ 1 มีนาคม 2025<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Rama 9 Connected Location">
</div><br>
<b>จุดเด่นของสื่อ:</b><br>
✔ จอ Digital ขนาดใหญ่จำนวน 1 จอ – ตั้งอยู่ในทำเลศักยภาพ บริเวณแยกมารยาทดี จุดตัดระหว่างถนนจตุรทิศและเพชรอุทัย<br>
✔ ใจกลางศูนย์ธุรกิจพระราม 9 – รายล้อมด้วยแหล่งสำคัญ เช่น RCA, โรงพยาบาลพระราม 9, ห้าง Bravo และอาคารสำนักงาน<br>
✔ เข้าถึงกลุ่มเป้าหมายหลากหลาย – ผู้คนสัญจรตลอดทั้งวัน ทั้งกลุ่มคนทำงาน นักท่องเที่ยว และผู้พักอาศัยในพื้นที่<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Rama 9 Connected Showcase">
</div><br>
<b>ข้อเสนอสุดพิเศษ!</b><br>
📌 ราคาพิเศษ เฉพาะช่วงเปิดตัว สามารถยืนยันการจองได้ถึงวันที่ 31 พฤษภาคม 2025 และขึ้นสื่อได้ภายในวันที่ 31 ธันวาคม 2025 (เงื่อนไข: ไม่สามารถเลื่อนหรือยกเลิกหลังการยืนยัน)<br><br>
หากคุณ {{Client name}} สนใจสื่อนี้ หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["rama9_1.jpg", "rama9_2.jpg"]
    },
    "The Skyline": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ The Skyline สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ ที่โดดเด่นด้วยทำเลบนถนนทางเข้าสนามบินสุวรรณภูมิ โดยมีให้เลือกถึง 2 ตำแหน่ง คือ :<br>
• <b>The Skyline A</b> : ตั้งอยู่ทางฝั่งซ้ายของเส้นทาง เหมาะสำหรับการสร้างความประทับใจแรกพบ<br>
• <b>The Skyline B</b> : ครอบคลุมเส้นทางจราจร มั่นใจได้ว่าผู้โดยสารทุกคนจะต้องมองเห็น<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The Skyline Location">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Passenger Traffic">
</div><br>
_________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ The Skyline หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["skyline_1.jpg", "skyline_2.jpg"]
    },
    "The 20": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "detail": """เรียน คุณ {{Client name}},<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ The 20 สื่อดิจิทัลใหม่ล่าสุด จาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยสื่อนี้ได้พลิกโฉม ป้ายโฆษณา Serie Poles เดิม ให้กลายเป็น จอ LED กว่า 74 จอ ที่เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The 20 Coverage">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The 20 Storytelling">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG3}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The 20 Ad Sets">
</div><br>
______________________________________________________________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ The 20 หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["the20_1.jpg", "the20_2.jpg", "the20_3.jpg"]
    },
    "Nextopia Siam Paragon": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: “NEXTOPIA” สื่อใหม่ล่าสุด สร้างประสบการณ์ให้แบรนด์ 360° พร้อมยกระดับภาพลักษณ์",
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
{{Sale name}} ขอแนะนำ NEXTOPIA สื่อโฆษณาดิจิทัลสุดล้ำแห่งใหม่ ใจกลางศูนย์การค้า Siam Paragon ตั้งอยู่ในโซนใหม่ “NEXTOPIA” ซึ่งเป็นพื้นที่ที่รวมแบรนด์สินค้ารักษ์โลก<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Nextopia Sphere">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Nextopia 3D Content">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG3}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Nextopia Showcase">
</div><br>
_______________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ NEXTOPIA หรือบริการของเราเพิ่มเติมสามารถติดต่อได้ที่เบอร์ {{Tel}} หรือเพียงตอบกลับอีเมลนี้ได้เลยค่ะ<br>
ขอบคุณค่ะ {{Sale name}}""",
        "images": ["nextopia_1.jpg", "nextopia_2.jpg", "nextopia_3.jpg"]
    },
    "Central Network": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: กระตุ้นการตัดสินใจซื้อ ด้วยสื่อ ณ จุดขายในห้าง Central ทั่วประเทศ",
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ Central Network สื่อจอดิจิทัลภายในห้างสรรพสินค้าเซ็นทรัลทั่วประเทศ ที่มีเครือข่ายทั้งหมด 283 จอ ครอบคลุม 14 สาขาทั้งในกทม. และต่างจังหวัด<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Network Branches">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Network Positions">
</div><br>
------------------------------------------------------------------------<br>
หากคุณ {{Client name}} สนใจสื่อ Central Network หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["central_net_1.jpg", "central_net_2.jpg"]
    },
    "Central Network [New Package]": {
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ ทางเราขอแนะนำแพ็กเกจ Central Network ที่อัปเกรดครั้งใหญ่ โดยเปิดตัว CentralWorld 360 – สื่อดิจิทัลใหม่ล่าสุดในรูปแบบ จอ LED ทรงโค้งแบบ Tower Wraparound<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="CentralWorld 360 Miss Dior">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="CentralWorld 360 NARS">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG3}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="CentralWorld VDO Wall">
</div><br>
หากท่านสนใจข้อมูลเพิ่มเติม สามารถติดต่อกลับได้ทางอีเมลนี้ หรือเบอร์ {{Tel}} ได้ตลอดเวลาค่ะ""",
        "images": ["central_w360_1.jpg", "central_w360_2.jpg", "central_w360_3.jpg"]
    },
    "Central Park": {
        "subject": "[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ",
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ ทางเรามีความยินดีนำเสนอ "Central Park" จอดิจิทัลใหม่ล่าสุด บนโครงการมิกซ์ยูสระดับโลก Dusit Central Park บริเวณหัวมุมถนนสีลม – พระราม 4<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Dusit Central Park Overview">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Park Tissot Screen">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG3}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Park Entrance Screen">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG4}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Park Hourglass Screen">
</div><br>
______________________________________________________________________________________________<br>
หากท่านสนใจข้อมูลเพิ่มเติม สามารถติดต่อกลับได้ทางอีเมลนี้ หรือติดต่อที่เบอร์ {{Tel}} ได้ตลอดเวลาค่ะ""",
        "images": ["central_park_1.jpg", "central_park_2.jpg", "central_park_3.jpg", "central_park_4.jpg"]
    },
    "PlanB TV Nationwide [New Pack]": {
        "subject": "[Plan B Media] ปรับแพ็กเกจ Plan B TV Nationwide ใหม่ ให้เข้าถึงกลุ่มเป้าหมายมากขึ้น คุ้มค่ายิ่งกว่าเดิม",
        "detail": """เรียน คุณ {{Client name}},<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ คุณ {{Client name}} ทางเราขอแจ้งให้ทราบเกี่ยวกับการปรับแพ็กเกจ Plan B TV Nationwide ใหม่<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="PlanB TV Nationwide">
</div><br>
<b>แพ็กเกจใหม่ของ PBTV Nationwide แบ่งเป็น:</b><br>
• Pack Full จำนวน 120 จอ<br>
• Pack Red / Blue จำนวน อย่างละ 57 จอ<br><br>
หากลูกค้าสะดวก ทางเรายินดีอธิบายรายละเอียดเพิ่มเติมเกี่ยวกับแพ็กเกจนี้ เพื่อช่วยให้คุณเลือกใช้สื่อได้อย่างคุ้มค่าที่สุดค่ะ<br>
ขอบคุณค่ะ""",
        "images": ["Plan%20B%20TV%20Nationwide.jpg"]
    }
}

CREDENTIAL_LINK = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"
CREDENTIAL_SUBJECT = "[Plan B Media] ขออนุญาตนัดเข้าพบเพื่อนำเสนอสื่อโฆษณานอกบ้านสำหรับปี 2026"
CREDENTIAL_DETAIL = f"""เรียน คุณ {{Client name}}<br><br>
{{AI_PITCH}}<br><br>
ขออนุญาตแนะนำตัว {{Sale name}} จาก บริษัท แพลนบี มีเดีย จำกัด (มหาชน) ค่ะ<br><br>
📌 <b>Plan B Media Profile / Credential:</b><br>
คุณสามารถเลือกเข้าชมภาพรวมสื่อทั้งหมดได้ที่ลิงก์นี้ค่ะ: <a href="{CREDENTIAL_LINK}" target="_blank">{CREDENTIAL_LINK}</a><br><br>
หากคุณ {{Client name}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือตอบกลับอีเมลนี้ได้เลยค่ะ"""

MAGNETIC_OPTIONS = {
    "[Classic] Magnetic Cookies P11 (Static Poles ONLY)": "https://drive.google.com/drive/u/0/folders/1Xa3CUD5VlAqw23w-T4hbpwSP_y6p1UCT",
    "[Digital] Rama 9 Connected": "https://drive.google.com/drive/u/0/folders/1E8SfEFV2k7kmFBbiaj0atsQJrgwIB7Ij",
    "[Retail] Central Network": "https://drive.google.com/drive/u/0/folders/1jKRJBAlKcpauiUaNxTC0CuzK67_D6uOU",
    "[Airport] Suvarnabhumi Airport Network": "https://drive.google.com/drive/u/0/folders/1bPOrmVULWEdrDD3bPm_w-l-D3vCuQqX-",
    "[Unipole] Unipole Landmark Network": "https://drive.google.com/drive/u/0/folders/1f3-qvyU3l7uNbdi_lYtVbi9nreWgYmdH",
    "📂 รวมรายงาน Magnetic สื่อทุกหมวดหมู่ (Complete Folder)": "https://drive.google.com/drive/u/0/folders/1yThQkzFIknZZO1m4umZQK_iMxT4i-CPc"
}

valid_keys = list(MAGNETIC_OPTIONS.keys())

st.title("📢 PLAN B MEDIA • AUTOMATION SYSTEM EMAIL")

# ==========================================
# STEP 01 : MANAGING RECIPIENTS
# ==========================================
if step == "STEP 01 : จัดการรายชื่อลูกค้า":
    st.subheader("👥 STEP 01 : จัดการรายชื่อลูกค้าผู้รับ")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### 1️⃣ ดึงรายชื่อจาก Google Sheets")
        if st.button("🔄 โหลดรายชื่อจาก Google Sheet Real-time"):
            target_url = sheet_url_input if sheet_url_input else DEFAULT_SHEET_URL
            csv_url = get_csv_url(target_url)
            
            if not csv_url:
                st.error("❌ รูปแบบ Google Sheet URL ไม่ถูกต้อง")
            else:
                try:
                    df = pd.read_csv(csv_url).dropna(how='all')
                    new_records = []
                    for _, row in df.iterrows():
                        rec = row.to_dict()
                        rec['ส่งอีเมล?'] = True
                        rec['ที่มา'] = 'Google Sheets'
                        new_records.append(rec)
                    st.session_state.recipients = new_records
                    st.session_state.editor_key += 1
                    st.success(f"✅ ดึงรายชื่อสำเร็จ {len(new_records)} รายชื่อ!")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: โปรดเช็กสิทธิ์ Google Sheet ({e})")
                    
    with col2:
        st.markdown("#### 2️⃣ ➕ พิมพ์เพิ่มรายชื่อลูกค้าใหม่ (Manual)")
        nc = st.text_input("ชื่อบริษัท")
        nn = st.text_input("ชื่อผู้ติดต่อ / ลูกค้า ({{Client name}})")
        ne = st.text_input("อีเมลผู้รับ")
        if st.button("➕ เพิ่มลูกค้ารายนี้"):
            if ne:
                st.session_state.recipients.append({
                    "ส่งอีเมล?": True,
                    "ที่มา": "Manual",
                    "ชื่อบริษัท": nc,
                    "ชื่อผู้ติดต่อ": nn,
                    "อีเมล": ne
                })
                st.session_state.editor_key += 1
                st.success(f"เพิ่มคุณ {nn} ({ne}) สำเร็จ!")

    st.markdown("---")
    st.markdown("#### 3️⃣ ตารางลูกค้ารวมทั้งหมด")

    if st.session_state.recipients:
        btn_col1, btn_col2, _ = st.columns([2, 2, 4])
        with btn_col1:
            if st.button("☑️ เลือกส่งทั้งหมด", use_container_width=True):
                for r in st.session_state.recipients:
                    r['ส่งอีเมล?'] = True
                st.session_state.editor_key += 1
                st.rerun()
                
        with btn_col2:
            if st.button("❌ ไม่เลือกทั้งหมด / ล้างรายการ", use_container_width=True):
                for r in st.session_state.recipients:
                    r['ส่งอีเมล?'] = False
                st.session_state.editor_key += 1
                st.rerun()

        df_rec = pd.DataFrame(st.session_state.recipients)
        
        if 'ส่งอีเมล?' not in df_rec.columns:
            df_rec.insert(0, 'ส่งอีเมล?', True)
            
        priority = ['ส่งอีเมล?', 'ที่มา']
        others = [c for c in df_rec.columns if c not in priority]
        df_rec = df_rec[priority + others]
        
        edited_df = st.data_editor(
            df_rec,
            column_config={
                "ส่งอีเมล?": st.column_config.CheckboxColumn("เลือกส่ง?", default=True),
                "ที่มา": st.column_config.TextColumn("ที่มาข้อมูล", disabled=True),
            },
            disabled=[c for c in df_rec.columns if c != "ส่งอีเมล?"],
            hide_index=True,
            use_container_width=True,
            key=f"editor_{st.session_state.editor_key}"
        )
        
        st.session_state.recipients = edited_df.to_dict('records')
        
        selected_count = sum(1 for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True)
        st.info(f"📊 สรุป: เลือกส่งอีเมลทั้งหมด **{selected_count}** / **{len(st.session_state.recipients)}** รายชื่อ")

# ==========================================
# STEP 02 : MEDIA SELECTION & AI PREVIEW
# ==========================================
elif step == "STEP 02 : เลือกเนื้อหา & พรีวิว":
    st.subheader("🖼️ STEP 02 : เลือกเนื้อหา & พรีวิวอีเมล (พร้อมระบบ AI)")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown(f"#### 🎯 โหมดปัจจุบัน: `{app_mode}`")
        
        # 📌 เลือกชื่อลูกค้าที่จะพรีวิวสดๆ (เช่น Vivo)
        st.info("🤖 **AI Runtime Feature:** เลือกลูกค้าจากตาราง แล้วกดให้ AI วิเคราะห์ธุรกิจพร้อมเจนข้อความสดๆ")
        
        recipients_list = st.session_state.recipients if st.session_state.recipients else [{"ชื่อผู้ติดต่อ": "สมชาย", "ชื่อบริษัท": "Vivo"}]
        client_options = []
        for r in recipients_list:
            c_name = r.get("ชื่อผู้ติดต่อ") or r.get("Client name") or "ลูกค้า"
            comp_name = r.get("ชื่อบริษัท") or r.get("Brand") or r.get("Company") or ""
            client_options.append(f"{c_name} ({comp_name})" if comp_name else c_name)
            
        selected_client_str = st.selectbox("🎯 เลือกลูกค้าที่ต้องการทดสอบพรีวิว AI:", options=client_options, index=0)
        
        # ดึงค่าจริงจากที่เลือก
        selected_index = client_options.index(selected_client_str)
        target_rec = recipients_list[selected_index]
        sample_client = target_rec.get("ชื่อผู้ติดต่อ") or target_rec.get("Client name") or "ลูกค้า"
        sample_company = target_rec.get("ชื่อบริษัท") or target_rec.get("Brand") or target_rec.get("Company") or "Vivo"

        if st.button("✨ ให้ AI วิเคราะห์ลูกค้าคนนี้ & เจนคำโปรยเสนอขาย", type="primary"):
            with st.spinner(f"🤖 Gemini AI กำลังวิเคราะห์แบรนด์ {sample_company} และประมวลผลข้อความ..."):
                st.session_state.ai_generated_pitch = generate_ai_personalized_text(sample_client, sample_company, app_mode)
                st.success("✅ AI ประมวลผลข้อความเรียบร้อย!")

        # 1️⃣ Mode 1: New Media
        if "1️⃣ New Media" in app_mode:
            selected_folder = st.selectbox("เลือกรายการสื่อ New Media:", options=list(MEDIA_FOLDERS.keys()), index=0)
            st.session_state.selected_media_folder = selected_folder
            current_subject = MEDIA_FOLDERS[selected_folder]["subject"]
            
            detail_tmpl = MEDIA_FOLDERS[selected_folder]["detail"]
            img_list = MEDIA_FOLDERS[selected_folder].get("images", [])
            for idx, img_name in enumerate(img_list, 1):
                detail_tmpl = detail_tmpl.replace(f"{{IMG{idx}}}", f"{GITHUB_RAW_BASE}{img_name}")
            current_detail = detail_tmpl
            
        # 2️⃣ Mode 2: Credential
        elif "2️⃣ Credential" in app_mode:
            current_subject = CREDENTIAL_SUBJECT
            current_detail = CREDENTIAL_DETAIL
            
        # 3️⃣ Mode 3: Magnetic Report
        elif "3️⃣ Magnetic Report" in app_mode:
            current_items = st.session_state.get('selected_mag_items', [])
            if not isinstance(current_items, list):
                current_items = []
                
            default_vals = [item for item in current_items if item in valid_keys]
            if not default_vals:
                default_vals = [valid_keys[0]]

            selected_mag_items = st.multiselect("เลือกรายงาน/สื่อ Magnetic ที่ต้องการส่ง:", options=valid_keys, default=default_vals)
            st.session_state.selected_mag_items = selected_mag_items
            current_subject = "[Plan B Media] Monthly Magnetic Report Update – สรุปข้อมูลสถิติ OOH ประจำเดือน"
            
            if selected_mag_items:
                items_html = ""
                for idx, item in enumerate(selected_mag_items, 1):
                    link = MAGNETIC_OPTIONS[item]
                    items_html += f"{idx}. <b>{item}</b><br>&nbsp;&nbsp;&nbsp;&nbsp;📌 ลิงก์ดาวน์โหลด: <a href='{link}' target='_blank'>{link}</a><br><br>"
                
                current_detail = f"""เรียน คุณ {{Client name}}<br><br>
{{AI_PITCH}}<br><br>
ขออนุญาตนำส่ง Magnetic Report สรุปข้อมูลสถิติ OOH ประจำเดือน รายละเอียดสถิติ Eyeballs และ Grid Reach ของสื่อที่คุณ {{Client name}} สนใจ ตามรายการด้านล่างนี้ค่ะ:<br><br>
{items_html}
ทาง Plan B หวังว่าข้อมูล Magnetic Report จะเป็นประโยชน์สำหรับการวางแผนกิจกรรมทางการตลาดของคุณ {{Client name}} ค่ะ<br><br>
หากคุณ {{Client name}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""

    with col_right:
        st.markdown("#### 📧 ตัวอย่างอีเมลที่จะถูกจัดส่ง (Preview)")
        
        # ข้อความ AI Pitch
        if st.session_state.ai_generated_pitch:
            ai_pitch_text = st.session_state.ai_generated_pitch
        else:
            ai_pitch_text = f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง เหมาะอย่างยิ่งสำหรับแบรนด์ {sample_company} ของคุณ {sample_client} ในการสร้างการรับรู้และความประทับใจให้กับกลุ่มเป้าหมายค่ะ"
        
        safe_subj = str(current_subject).replace("{{Client name}}", sample_client).replace("{Client name}", sample_client)
        safe_body = str(current_detail).replace("{{Client name}}", sample_client).replace("{Client name}", sample_client)
        safe_body = safe_body.replace("{AI_PITCH}", ai_pitch_text).replace("{{AI_PITCH}}", ai_pitch_text)
        safe_body = safe_body.replace("{{Sale name}}", str(user_name)).replace("{Sale name}", str(user_name))
        safe_body = safe_body.replace("{{Tel}}", str(user_phone)).replace("{Tel}", str(user_phone))
        
        preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
        
        st.text_input("📌 Subject (หัวข้อ):", value=safe_subj)
        st.components.v1.html(preview_html, height=450, scrolling=True)

# ==========================================
# STEP 03 : BATCH EMAIL SENDING WITH AI
# ==========================================
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("🚀 STEP 03 : ยืนยันยอด & กดส่ง Batch Email")
    
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    st.info(f"📬 พร้อมส่งอีเมลหาลูกค้าทั้งหมด **{len(selected_targets)}** รายชื่อ ในโหมด `{app_mode}` (ประมวลผลข้อความด้วย AI สำหรับผู้รับแต่ละราย)")
    
    if st.button("✉️ ยืนยันส่ง Batch Email ทันที", type="primary", use_container_width=True):
        if not selected_targets:
            st.error("❌ ยังไม่ได้เลือกรายชื่อลูกค้าที่จะส่ง กรุณากลับไปที่ STEP 01 ค่ะ")
        elif not gmail_sender or not sender_password:
            st.error("❌ กรุณาระบุ บัญชี Gmail และ Google App Password ที่ Sidebar ฝั่งซ้ายมือให้ครบถ้วนก่อนส่งค่ะ")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            success_count = 0
            fail_count = 0
            
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(gmail_sender, sender_password)
                banner_bytes = fetch_image_bytes("footer_banner.jpg")
                
                for idx, target in enumerate(selected_targets):
                    client_name = "ลูกค้าผู้มีเกียรติ"
                    for key in ["ชื่อผู้ติดต่อ", "Client name", "ชื่อ", "Name"]:
                        val = target.get(key)
                        if val and str(val).strip():
                            client_name = str(val).strip()
                            break
                            
                    company_name = target.get("ชื่อบริษัท") or target.get("Brand") or target.get("Company") or "บริษัทลูกค้า"
                    client_email = str(target.get("อีเมล") or target.get("Email") or "").strip()
                    
                    if client_email and "@" in client_email:
                        # 🤖 AI Runtime: เจนคำโปรย Personalized สดๆ รายบริษัท
                        ai_personalized_pitch = generate_ai_personalized_text(client_name, company_name, app_mode)
                        
                        msg = MIMEMultipart("related")
                        msg['From'] = formataddr((user_name, gmail_sender))
                        msg['To'] = client_email
                        msg['Reply-To'] = user_email
                        
                        if "1️⃣ New Media" in app_mode:
                            media_info = MEDIA_FOLDERS[st.session_state.selected_media_folder]
                            subject_tmpl = media_info["subject"]
                            detail_tmpl = media_info["detail"]
                            img_list = media_info.get("images", [])
                            for i, _ in enumerate(img_list, 1):
                                detail_tmpl = detail_tmpl.replace(f"{{IMG{i}}}", f"cid:media_img_{i}")
                        elif "2️⃣ Credential" in app_mode:
                            subject_tmpl = CREDENTIAL_SUBJECT
                            detail_tmpl = CREDENTIAL_DETAIL
                            img_list = []
                        else:
                            chosen_items = st.session_state.get('selected_mag_items', [valid_keys[0]])
                            items_html = ""
                            for i, item in enumerate(chosen_items, 1):
                                link = MAGNETIC_OPTIONS.get(item, MAGNETIC_OPTIONS[valid_keys[0]])
                                items_html += f"{i}. <b>{item}</b><br>&nbsp;&nbsp;&nbsp;&nbsp;📌 ลิงก์ดาวน์โหลด: <a href='{link}' target='_blank'>{link}</a><br><br>"
                            subject_tmpl = "[Plan B Media] Monthly Magnetic Report Update – สรุปข้อมูลสถิติ OOH ประจำเดือน"
                            detail_tmpl = f"เรียน คุณ {{Client name}}<br><br>{{AI_PITCH}}<br><br>ขออนุญาตนำส่ง Magnetic Report สรุปข้อมูลสถิติ OOH ประจำเดือน ดังนี้ค่ะ:<br><br>{items_html}"
                            img_list = []

                        sub_text = str(subject_tmpl).replace("{{Client name}}", client_name).replace("{Client name}", client_name)
                        sub_text = sub_text.replace("{{Sale name}}", str(user_name)).replace("{{Tel}}", str(user_phone))
                        msg['Subject'] = sub_text
                        
                        body_html = str(detail_tmpl).replace("{AI_PITCH}", ai_personalized_pitch).replace("{{AI_PITCH}}", ai_personalized_pitch)
                        body_html = body_html.replace("{{Client name}}", client_name).replace("{Client name}", client_name)
                        body_html = body_html.replace("{{Sale name}}", str(user_name)).replace("{Sale name}", str(user_name))
                        body_html = body_html.replace("{{Tel}}", str(user_phone)).replace("{Tel}", str(user_phone))
                        
                        full_html = body_html + FOOTER_BANNER_HTML_SEND
                        
                        msg_alt = MIMEMultipart("alternative")
                        msg_alt.attach(MIMEText(full_html, 'html'))
                        msg.attach(msg_alt)
                        
                        if "1️⃣ New Media" in app_mode and img_list:
                            for img_idx, img_filename in enumerate(img_list, 1):
                                img_bytes = fetch_image_bytes(img_filename)
                                if img_bytes:
                                    img_part = MIMEImage(img_bytes)
                                    img_part.add_header('Content-ID', f'<media_img_{img_idx}>')
                                    img_part.add_header('Content-Disposition', 'inline', filename=img_filename)
                                    msg.attach(img_part)
                                    
                        if banner_bytes:
                            banner_part = MIMEImage(banner_bytes)
                            banner_part.add_header('Content-ID', '<footer_banner>')
                            banner_part.add_header('Content-Disposition', 'inline', filename='footer_banner.jpg')
                            msg.attach(banner_part)
                        
                        server.sendmail(gmail_sender, [client_email], msg.as_string())
                        success_count += 1
                    else:
                        fail_count += 1
                        
                    progress_bar.progress((idx + 1) / len(selected_targets))
                    status_text.text(f"🤖 AI กำลังประมวลผลข้อความและส่งอีเมลถึง: {client_name} ({company_name})...")
                    
                server.quit()
                st.success(f"🎉 AI ประมวลผลและส่งอีเมลสำเร็จทั้งหมด {success_count} รายชื่อ!")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการส่งผ่าน SMTP: {e}")
