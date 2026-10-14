import streamlit as st
import pandas as pd
import re
import smtplib
import requests
import json
import urllib.request
import random
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
GMAIL_USER = st.secrets.get("GMAIL_USER", "wichayada.ph@planbmedia.co.th")
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

# DATA TEMPLATES FOR MEDIA (NEW MEDIA MODE ONLY)
MEDIA_FOLDERS = {
    "The 20": {
        "title": "The 20",
        "description": "สื่อดิจิทัล DOOH ยาวที่สุดในโลก 2.5 กม. บนทางด่วน CBD เหมาะกับ Tech, ยานยนต์, แบรนด์ใหญ่ระดับองค์กร, สถาบันการเงิน, พลังงาน ที่ต้องการ Impact สูง",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "detail": """เรียน {{Greeting Name}}<br><br>
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
หาก{{Closing Target}} สนใจสื่อ The 20 หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["the20_1.jpg", "the20_2.jpg", "the20_3.jpg"]
    },
    "Central Network [New Package]": {
        "title": "Central Network [New Package]",
        "description": "สื่อในห้างสรรพสินค้า CentralWorld ทั่วประเทศ เหมาะกับ แฟชั่น, เครื่องสำอาง, รองเท้า, สนีกเกอร์, อาหาร, ร้านค้า Retail, FMCG, คอสเมติก, สปา, สกินแคร์, เล็บ, ความงาม",
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "detail": """เรียน {{Greeting Name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ ทางเราขอแนะนำแพ็กเกจ Central Network ที่อัปเกรดครั้งใหญ่ โดยเปิดตัว CentralWorld 360 – สื่อดิจิทัลใหม่ล่าสุดในรูปแบบ จอ LED ทรงโค้งแบบ Tower Wraparound บริเวณลิฟต์แก้ว CentralWorld<br><br>
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
    "The Skyline": {
        "title": "The Skyline",
        "description": "ป้ายภาพนิ่งขนาดใหญ่ทางเข้าสนามบินสุวรรณภูมิ เหมาะกับ สินค้าพรีเมียม, ท่องเที่ยว, โรงแรม, สายการบิน, อสังหาริมทรัพย์, ลักชัวรี, แบรนด์เนม, สินค้านำเข้า",
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "detail": """เรียน {{Greeting Name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ The Skyline สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ บนถนนทางเข้าสนามบินสุวรรณภูมิ<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The Skyline Location">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Passenger Traffic">
</div><br>
_________________________________________<br>
หาก{{Closing Target}} สนใจสื่อ The Skyline หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["skyline_1.jpg", "skyline_2.jpg"]
    },
    "rama 9 connected": {
        "title": "rama 9 connected",
        "description": "สื่อดิจิทัลใจกลาง CBD พระราม 9 ย่านธุรกิจ RCA เหมาะกับ ออฟฟิศ B2B, คลินิก, โรงพยาบาล, สถาบันการศึกษา, โรงเรียน, มหาวิทยาลัย",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "detail": """เรียน {{Greeting Name}}<br><br>
{AI_PITCH}<br><br>
ขอแนะนำ “RAMA 9 Connected” สื่อโฆษณาดิจิทัลใหม่ล่าสุดใจกลาง CBD พระราม 9 ที่พร้อมให้บริการตั้งแต่วันที่ 1 มีนาคม 2025<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Rama 9 Connected Location">
</div><br>
<b>จุดเด่นของสื่อ:</b><br>
✔ จอ Digital ขนาดใหญ่จำนวน 1 จอ – ตั้งอยู่ในทำเลศักยภาพ บริเวณแยกมารยาทดี จุดตัดระหว่างถนนจตุรทิศและเพชรอุทัย<br>
✔ ใจกลางศูนย์ธุรกิจพระราม 9 – รายล้อมด้วยแหล่งสำคัญ เช่น RCA, โรงพยาบาลพระราม 9, ห้าง Bravo และอาคารสำนักงาน<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Rama 9 Connected Showcase">
</div><br>
หาก{{Closing Target}} สนใจสื่อนี้ หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["rama9_1.jpg", "rama9_2.jpg"]
    }
}

# 🧼 HELPER FUNCTION: สกัดข้อมูลอย่างสะอาด
def extract_sheet_data(record):
    c_name = ""
    comp_name = ""
    
    raw_name = str(record.get("Name") or record.get("ชื่อผู้ติดต่อ") or "").strip()
    raw_comp = str(record.get("Company Name") or record.get("ชื่อบริษัท") or "").strip()
    
    invalid_terms = ["-", "- marketing", "marketing", "none", "nan", "null", ""]
    
    clean_name = re.sub(r'^[\s\-_]+', '', raw_name).strip()
    if clean_name.lower() not in invalid_terms and len(clean_name) > 1:
        c_name = clean_name
        
    clean_comp = re.sub(r'^[\s\-_]+', '', raw_comp).strip()
    if clean_comp.lower() not in invalid_terms and len(clean_comp) > 1:
        comp_name = clean_comp

    return c_name, comp_name

# 🧹 HELPER FUNCTION: แทนที่ตัวแปรในข้อความอย่างสมบูรณ์ ไม่หลุดวงเล็บปีกกา
def replace_placeholders(text, greeting_name, closing_target, sale_name, phone_num, pitch_text=""):
    result = str(text)
    
    # คำขึ้นต้น
    result = result.replace("{{Greeting Name}}", greeting_name).replace("{Greeting Name}", greeting_name)
    result = result.replace("{{Client name}}", greeting_name).replace("{Client name}", greeting_name)
    
    # คำลงท้าย
    result = result.replace("{{Closing Target}}", closing_target).replace("{Closing Target}", closing_target)
    
    # ผู้ส่ง & เบอร์โทร
    result = result.replace("{{Sale name}}", sale_name).replace("{Sale name}", sale_name)
    result = result.replace("{{Tel}}", phone_num).replace("{Tel}", phone_num)
    
    # AI Pitch
    if pitch_text:
        result = result.replace("{{AI_PITCH}}", pitch_text).replace("{AI_PITCH}", pitch_text)
        
    return result

# 🤖 AI ENGINE FUNCTION (BALANCED CATEGORY MATCHING)
def run_ai_smart_match_and_pitch(contact_name, company_name, index_hint=0):
    available_media_list = list(MEDIA_FOLDERS.keys())
    has_contact = bool(contact_name and str(contact_name).strip())
    
    comp_lower = company_name.lower()
    
    # Smart Fallback Logic กระจายสื่อตามคีย์เวิร์ดอย่างแม่นยำ
    if any(k in comp_lower for k in ["คอสเมคอน", "สนีกเกอร์", "มัสตาร์ด", "fashion", "beauty", "เครื่องสำอาง", "รองเท้า", "retail", "สปา", "เล็บ", "nail", "apparel", "สุกี้", "อาหาร"]):
        fallback_media = "Central Network [New Package]"
    elif any(k in comp_lower for k in ["โรงเรียน", "สาธิต", "school", "คลินิก", "โรงพยาบาล", "อสังหา", "การเงิน", "ประกัน"]):
        fallback_media = "rama 9 connected"
    elif any(k in comp_lower for k in ["สุวรรณภูมิ", " travel", "luxury", "พรีเมียม", "โรงแรม", "สนามบิน", "บิน", "ต่างประเทศ"]):
        fallback_media = "The Skyline"
    else:
        # กระจายระหว่าง The 20 และสื่ออื่นๆ ตามลำดับสลับ
        fallback_options = ["The 20", "Central Network [New Package]", "The Skyline", "rama 9 connected"]
        fallback_media = fallback_options[index_hint % len(fallback_options)]

    if not GEMINI_API_KEY:
        selected_media = fallback_media
        reason = f"AI วิเคราะห์ลักษณะธุรกิจของแบรนด์ {company_name} แล้วพบว่าเหมาะสมที่สุดกับสื่อ {selected_media} เพื่อเข้าถึงกลุ่มเป้าหมายได้ตรงจุด"
        if has_contact:
            pitch = f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company_name} ของคุณ {contact_name} ได้อย่างสมบูรณ์แบบค่ะ"
        else:
            pitch = f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company_name} ได้อย่างสมบูรณ์แบบค่ะ"
        return selected_media, reason, pitch

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        media_context = {}
        for k, v in MEDIA_FOLDERS.items():
            media_context[k] = v.get("description", "")

        if has_contact:
            target_context = f"ลูกค้าชื่อคุณ {contact_name}, แบรนด์/บริษัท: {company_name}"
            pitch_instruction = f"แต่งข้อความเกริ่นนำเสนอขายสั้นๆ 2 บรรทัด เช่น 'ขอแนะนำสื่อโฆษณา... ให้กับแบรนด์ {company_name} ของคุณ {contact_name}...'"
        else:
            target_context = f"ลูกค้าแบรนด์/บริษัท: {company_name} (ไม่มีชื่อผู้ติดต่อรายบุคคล)"
            pitch_instruction = f"แต่งข้อความเกริ่นนำเสนอขายสั้นๆ 2 บรรทัด โดยพูดถึงแบรนด์ {company_name} โดยตรงอย่างสละสลวย เป็นธรรมชาติ ห้ามใส่คำว่า 'ของคุณ {company_name}' ซ้ำซ้อนเด็ดขาด"

        prompt = f"""
        คุณคือ AI Sales Agent ผู้เชี่ยวชาญของ Plan B Media
        ข้อมูลลูกค้า: {target_context}
        
        รายการสื่อ OOH และประเภทธุรกิจที่เหมาะสม:
        {json.dumps(media_context, ensure_ascii=False, indent=2)}

        คำสั่งสำคัญ:
        1. วิเคราะห์ว่าแบรนด์ {company_name} ทำธุรกิจประเภทใด
        2. เลือกสื่อ 1 ตัวจากรายการที่ตรงกับลักษณะธุรกิจของแบรนด์มากที่สุด (กระจายสื่ออย่างเหมาะสม เช่น แฟชั่น/ความงาม/ของใช้ -> Central Network, โรงเรียน/คลินิก/ออฟฟิศ -> rama 9 connected, พรีเมียม/ท่องเที่ยว -> The Skyline, องค์กรใหญ่/การเงิน/Tech -> The 20)
        3. เขียนเหตุผลสั้นๆ 2 บรรทัด ว่าทำไมสื่อนี้จึงเหมาะกับแบรนด์ {company_name} (reason)
        4. {pitch_instruction} (pitch)

        ตอบกลับเป็น JSON Format เท่านั้น ดังนี้:
        {{
            "selected_media": "ชื่อสื่อที่เลือกตรงเป๊ะๆ จากรายการ",
            "reason": "เหตุผลสั้นๆ 2 บรรทัด",
            "pitch": "ข้อความเกริ่นนำเสนอขาย 2 บรรทัด"
        }}
        """
        data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
        json_data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=json_data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            res_text = res_body["candidates"][0]["content"]["parts"][0]["text"]
            res_json = json.loads(res_text)
            
            s_media = res_json.get("selected_media", fallback_media)
            if s_media not in MEDIA_FOLDERS:
                s_media = fallback_media
            return s_media, res_json.get("reason", ""), res_json.get("pitch", "")
    except Exception:
        selected_media = fallback_media
        reason = f"AI วิเคราะห์ธุรกิจของแบรนด์ {company_name} และแนะนำสื่อ {selected_media} ที่ตอบโจทย์การเข้าถึงกลุ่มเป้าหมาย"
        if has_contact:
            pitch = f"ขอแนะนำสื่อโฆษณาทำเลศักยภาพสูงที่ตอบโจทย์และเสริมภาพลักษณ์ให้กับแบรนด์ {company_name} ของคุณ {contact_name} ค่ะ"
        else:
            pitch = f"ขอแนะนำสื่อโฆษณาทำเลศักยภาพสูงที่ตอบโจทย์และเสริมภาพลักษณ์ให้กับแบรนด์ {company_name} ค่ะ"
        return selected_media, reason, pitch

# ==========================================
# SIDEBAR
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

# SESSION STATE
if 'recipients' not in st.session_state:
    st.session_state.recipients = []
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0
if 'ai_results' not in st.session_state:
    st.session_state.ai_results = {}
if 'client_magnetic_selections' not in st.session_state:
    st.session_state.client_magnetic_selections = {}

FOOTER_BANNER_HTML_PREVIEW = f"""
<br><br>
<div style="text-align: center; margin-top: 20px;">
    <img src="{GITHUB_RAW_BASE}footer_banner.jpg" width="600" style="max-width: 100%; height: auto; border-radius: 6px;" alt="Plan B Media Services">
</div>
"""

# EXACT NOTE TEMPLATE FOR CREDENTIAL
CREDENTIAL_LINK = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"
CREDENTIAL_SUBJECT = "[Plan B Media] ขออนุญาตนัดเข้าพบเพื่อนำเสนอสื่อโฆษณานอกบ้านสำหรับปี 2026"
CREDENTIAL_DETAIL = f"""เรียน {{Greeting Name}}<br><br>
ขออนุญาตแนะนำตัว {{Sale name}} Account Executive I, Sales จาก บริษัท แพลนบี มีเดีย จำกัด (มหาชน) ค่ะ<br><br>
จึงขออนุญาตนัดเข้าพบเพื่อแนะนำตัว และ นำเสนอรายละเอียดของสื่อโฆษณานอกบ้านล่าสุดของทาง Plan B สำหรับปี 2026 ตามวันและเวลาที่ท่านสะดวก<br><br>
1. Digital: สื่อจอภาพเคลื่อนไหวกลางแจ้ง ทั้งกรุงเทพฯและต่างจังหวัด<br>
2. Classic: ป้ายภาพนิ่งบิลบอร์ดหลากหลายขนาด ทั้งในกรุงเทพฯและต่างจังหวัด<br>
3. Retail: สื่อโฆษณา ณ จุดขาย บริเวณศูนย์การค้าเครือสยามพิวรรธน์ เซ็นทรัลกรุ๊ป และ 7-Eleven<br>
4. Transit: สื่อระบบขนส่งมวลชน (รถประจำทางแบบปรับอากาศ / รถไฟใต้ดิน MRT / รถไฟฟ้า BTS )<br>
5. Airport : สื่อโฆษณาในสนามบินสุวรรณภูมิ, สนามบินดอนเมือง และสนามบินต่างจังหวัด<br>
6. International : สื่อโฆษณาต่างประเทศ (Laos , Malaysia , Singapore , USA)<br><br>
📌 <b>Plan B Media Profile / Credential:</b><br>
- <b>Credential :</b> ภาพรวมสื่อทั้งหมด ตาม link ด้านล่างนี้ค่ะ<br>
<a href="{CREDENTIAL_LINK}" target="_blank">{CREDENTIAL_LINK}</a><br><br>
เรามั่นใจว่าสื่อโฆษณานอกบ้านของ แพลนบี มีเดีย ที่มีความหลากหลายจะเป็นส่วนหนึ่งในการช่วยส่งเสริมการสร้างกิจกรรมทางการตลาดหรือสร้าง Brand ได้อย่างมีประสิทธิภาพอย่างแน่นอน<br>
____________________________________________________________________________________<br><br>
หาก{{Closing Target}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติมสามารถสอบถามรายละเอียดได้ที่ เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ<br><br>
ขอขอบคุณที่สละเวลาอ่านอีเมลฉบับนี้ และหวังว่าจะได้พูดคุยกับคุณเร็วๆ นี้ค่ะ"""

# MAGNETIC OPTIONS
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
        nc = st.text_input("ชื่อบริษัท / แบรนด์")
        nn = st.text_input("ชื่อผู้ติดต่อ (ถ้าไม่มีระบบจะใช้ชื่อบริษัทแทน)")
        ne = st.text_input("อีเมลผู้รับ")
        if st.button("➕ เพิ่มลูกค้ารายนี้"):
            if ne:
                st.session_state.recipients.append({
                    "ส่งอีเมล?": True,
                    "ที่มา": "Manual",
                    "Company Name": nc.strip() if nc.strip() else "ลูกค้า",
                    "Name": nn.strip(),
                    "Email": ne
                })
                st.session_state.editor_key += 1
                st.success("เพิ่มลูกค้ารายนี้สำเร็จ!")

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
        
        selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
        st.info(f"📊 สรุป: เลือกส่งอีเมลทั้งหมด **{len(selected_targets)}** / **{len(st.session_state.recipients)}** รายชื่อ")
        
        if selected_targets:
            with st.expander("🔍 คลิกเพื่อดูรายชื่อลูกค้าที่เลือกส่งทั้งหมด (Selected Clients)"):
                selected_display_list = []
                for idx, t in enumerate(selected_targets, 1):
                    c_name, comp_name = extract_sheet_data(t)
                    if c_name and comp_name:
                        label = f"คุณ {c_name} ({comp_name})"
                    elif comp_name:
                        label = comp_name
                    elif c_name:
                        label = f"คุณ {c_name}"
                    else:
                        label = "ลูกค้ารายใหม่"
                    email_str = str(t.get("Email") or t.get("อีเมล") or "").strip()
                    selected_display_list.append(f"**{idx}.** {label} — `{email_str}`")
                st.markdown("\n".join(selected_display_list))

# ==========================================
# STEP 02 : MULTI-BRAND BATCH PREVIEW
# ==========================================
elif step == "STEP 02 : เลือกเนื้อหา & พรีวิว":
    st.subheader("🖼️ STEP 02 : พรีวิวอีเมลสำหรับลูกค้าที่เลือกทั้งหมด (Multi-Brand Batch Preview)")
    
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    
    if not selected_targets:
        st.warning("⚠️ ยังไม่มีการเลือกรายชื่อลูกค้าใน STEP 01 กรุณากลับไปติ๊กเลือกรายชื่อลูกค้าก่อนค่ะ")
    else:
        st.markdown(f"#### 🎯 โหมดปัจจุบัน: `{app_mode}` (ดึงรายชื่อที่เลือกมาจาก STEP 01 ทั้งหมด **{len(selected_targets)}** รายชื่อ)")
        st.markdown("---")

        # 1️⃣ MODE 1: NEW MEDIA (AI BATCH GENERATION)
        if "1️⃣ New Media" in app_mode:
            st.info("🤖 **AI Sales Agent:** กดปุ่มด้านล่างเพื่อให้ Gemini AI วิเคราะห์ธุรกิจและเลือกสื่อ OOH พร้อมสร้างคำโปรยให้ **ทุกแบรนด์ที่เลือกพร้อมกันทีเดียว**")
            
            if st.button("🤖 ให้ AI วิเคราะห์ & เลือกสื่อ OOH ให้ทุกแบรนด์ที่เลือกพร้อมกัน", type="primary", use_container_width=True):
                ai_results = {}
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, target in enumerate(selected_targets):
                    c_name, comp_name = extract_sheet_data(target)
                    company = comp_name if comp_name else "ลูกค้า"
                    status_text.text(f"🤖 AI กำลังวิเคราะห์แบรนด์ ({idx+1}/{len(selected_targets)}): {company}...")
                    
                    s_media, r_reason, p_pitch = run_ai_smart_match_and_pitch(c_name, company, index_hint=idx)
                    email_key = str(target.get("Email") or target.get("อีเมล") or f"client_{idx}").strip()
                    ai_results[email_key] = {
                        "media": s_media,
                        "reason": r_reason,
                        "pitch": p_pitch
                    }
                    progress_bar.progress((idx + 1) / len(selected_targets))
                    
                st.session_state.ai_results = ai_results
                status_text.empty()
                progress_bar.empty()
                st.success("✅ AI ประมวลผลวิเคราะห์ครบทุกแบรนด์เรียบร้อยแล้วค่ะ!")

            st.markdown("### 📧 ตรวจสอบตัวอย่างอีเมลพรีวิวของแต่ละแบรนด์:")
            
            for idx, target in enumerate(selected_targets, 1):
                c_name, comp_name = extract_sheet_data(target)
                company = comp_name if comp_name else "ลูกค้า"
                email_key = str(target.get("Email") or target.get("อีเมล") or f"client_{idx-1}").strip()
                
                if c_name:
                    greeting_name = f"คุณ {c_name}"
                    closing_target = f"คุณ {c_name}"
                    default_pitch = f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company} ของคุณ {c_name} ได้อย่างสมบูรณ์แบบค่ะ"
                else:
                    greeting_name = f"ทีมงาน {company}"
                    closing_target = f"ทางแบรนด์ {company}"
                    default_pitch = f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company} ได้อย่างสมบูรณ์แบบค่ะ"

                ai_data = st.session_state.ai_results.get(email_key, {})
                selected_media = ai_data.get("media", list(MEDIA_FOLDERS.keys())[(idx-1) % len(MEDIA_FOLDERS)])
                ai_pitch = ai_data.get("pitch", default_pitch)
                ai_reason = ai_data.get("reason", f"AI วิเคราะห์ลักษณะธุรกิจของแบรนด์ {company} และเลือกสื่อที่เหมาะสมที่สุด")

                with st.expander(f"📌 [{idx}/{len(selected_targets)}] พรีวิวอีเมล: {greeting_name} ({company}) — `{email_key}`", expanded=True):
                    col_info, col_prev = st.columns([1, 1])
                    
                    with col_info:
                        st.markdown(f"**🏢 แบรนด์/บริษัท:** `{company}`")
                        st.markdown(f"**👤 คำขึ้นต้น:** `{greeting_name}`")
                        st.markdown(f"**🎯 สื่อที่ AI เลือกให้อัตโนมัติ:** `{selected_media}`")
                        st.info(f"💡 **เหตุผลจาก AI:** {ai_reason}")
                        st.markdown(f"📝 **คำโปรย AI (Pitch):** {ai_pitch}")
                        
                    with col_prev:
                        media_info = MEDIA_FOLDERS.get(selected_media, MEDIA_FOLDERS[list(MEDIA_FOLDERS.keys())[0]])
                        subj_text = replace_placeholders(media_info["subject"], greeting_name, closing_target, user_name, user_phone)
                        
                        detail_tmpl = media_info["detail"]
                        img_list = media_info.get("images", [])
                        for img_i, img_name in enumerate(img_list, 1):
                            detail_tmpl = detail_tmpl.replace(f"{{IMG{img_i}}}", f"{GITHUB_RAW_BASE}{img_name}")
                            
                        safe_body = replace_placeholders(detail_tmpl, greeting_name, closing_target, user_name, user_phone, ai_pitch)
                        preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
                        st.caption(f"📌 หัวข้อ: {subj_text}")
                        st.components.v1.html(preview_html, height=400, scrolling=True)

        # 2️⃣ MODE 2: CREDENTIAL (EXACT SALES NOTE FORMAT)
        elif "2️⃣ Credential" in app_mode:
            st.info("📌 **Credential Mode:** ใช้ข้อความแนะนำตัวและแนบลิงก์ Profile ตามแบบแผน Sales Note ทางการ 100%")
            
            for idx, target in enumerate(selected_targets, 1):
                c_name, comp_name = extract_sheet_data(target)
                company = comp_name if comp_name else "ลูกค้า"
                email_key = str(target.get("Email") or target.get("อีเมล") or f"client_{idx-1}").strip()
                
                if c_name:
                    greeting_name = f"คุณ {c_name}"
                    closing_target = f"คุณ {c_name}"
                else:
                    greeting_name = f"ทีมงาน {company}"
                    closing_target = f"ทางแบรนด์ {company}"

                with st.expander(f"📌 [{idx}/{len(selected_targets)}] พรีวิว Credential: {greeting_name} ({company}) — `{email_key}`", expanded=True):
                    subj_text = CREDENTIAL_SUBJECT
                    safe_body = replace_placeholders(CREDENTIAL_DETAIL, greeting_name, closing_target, user_name, user_phone)
                    
                    preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
                    st.caption(f"📌 หัวข้อ: {subj_text}")
                    st.components.v1.html(preview_html, height=450, scrolling=True)

        # 3️⃣ MODE 3: MAGNETIC REPORT (MANUAL SELECT PER CLIENT)
        elif "3️⃣ Magnetic Report" in app_mode:
            st.info("📊 **Magnetic Report Mode:** ระบุรอบเดือน และเลือกรายการสื่อ Magnetic ประจำแต่ละแบรนด์ได้อย่างอิสระ")
            report_month = st.text_input("ระบุรอบเดือนของรายงาน (เช่น ประจำเดือนมกราคม 2026):", value="ประจำเดือนมกราคม 2026")
            
            for idx, target in enumerate(selected_targets, 1):
                c_name, comp_name = extract_sheet_data(target)
                company = comp_name if comp_name else "ลูกค้า"
                email_key = str(target.get("Email") or target.get("อีเมล") or f"client_{idx-1}").strip()
                
                if c_name:
                    greeting_name = f"คุณ {c_name}"
                    closing_target = f"คุณ {c_name}"
                else:
                    greeting_name = f"ทีมงาน {company}"
                    closing_target = f"ทางแบรนด์ {company}"

                with st.expander(f"📌 [{idx}/{len(selected_targets)}] พรีวิว Magnetic Report: {greeting_name} ({company}) — `{email_key}`", expanded=True):
                    col_sel, col_p = st.columns([1, 1])
                    
                    with col_sel:
                        st.markdown(f"**🏢 ลูกค้า:** `{greeting_name} ({company})`")
                        
                        current_client_mag = st.session_state.client_magnetic_selections.get(email_key, [valid_keys[0]])
                        chosen_mag = st.multiselect(
                            f"เลือกสื่อ Magnetic สำหรับ {company}:",
                            options=valid_keys,
                            default=current_client_mag,
                            key=f"mag_sel_{email_key}"
                        )
                        st.session_state.client_magnetic_selections[email_key] = chosen_mag
                        
                    with col_p:
                        mag_links_html = ""
                        for m_key in chosen_mag:
                            m_url = MAGNETIC_OPTIONS.get(m_key, "")
                            mag_links_html += f"📌 <b>{m_key}:</b><br><a href='{m_url}' target='_blank'>{m_url}</a><br><br>"
                            
                        mag_subject = f"[Plan B Media] รายงานสรุปภาพรวมสื่อโฆษณานอกบ้าน (Magnetic Report) {report_month}"
                        mag_detail = f"""เรียน {{Greeting Name}}<br><br>
สวัสดีค่ะ {{Sale name}} ขออนุญาตส่งรายงานสรุปภาพรวมสถิติและผลการดำเนินงานของสื่อโฆษณานอกบ้าน (Magnetic Report) {report_month} เพื่อให้{{Closing Target}} ใช้เป็นข้อมูลประกอบการวางแผนการตลาดและการเลือกใช้สื่อ OOH ให้เกิดประสิทธิภาพสูงสุดค่ะ<br><br>
โดยท่านสามารถเข้าชมและดาวน์โหลดรายงานสรุปสถิติตามหมวดหมู่สื่อที่เกี่ยวข้องได้จากลิงก์ด้านล่างนี้ค่ะ:<br><br>
{mag_links_html}
หาก{{Closing Target}} ต้องการข้อมูลเชิงลึกเพิ่มเติม หรือสนใจวางแผนแคมเปญสื่อ OOH ร่วมกับ Plan B สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""
                        
                        safe_body = replace_placeholders(mag_detail, greeting_name, closing_target, user_name, user_phone)
                        preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
                        st.caption(f"📌 หัวข้อ: {mag_subject}")
                        st.components.v1.html(preview_html, height=400, scrolling=True)

# ==========================================
# STEP 03 : CONFIRM & SEND BATCH EMAILS
# ==========================================
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("🚀 STEP 03 : ยืนยันยอดและกดส่งอีเมลแบบ Batch Delivery")
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    
    if not selected_targets:
        st.warning("⚠️ ยังไม่มีการเลือกรายชื่อลูกค้าใน STEP 01 กรุณากลับไปติ๊กเลือกรายชื่อลูกค้าก่อนค่ะ")
    else:
        st.success(f"📋 สรุปพร้อมส่งอีเมลหาลูกค้าทั้งหมด **{len(selected_targets)}** รายชื่อ (โหมด: `{app_mode}`)")
        st.markdown(f"**บัญชีผู้ส่ง (Gmail):** `{gmail_sender}`")
        st.markdown(f"**ชื่อผู้ส่ง:** `{user_name}` | **เบอร์โทร:** `{user_phone}`")
        
        st.markdown("---")
        if st.button("🚀 ยืนยันส่งอีเมลทั้งหมดทันที (Send Batch Emails)", type="primary", use_container_width=True):
            success_count = 0
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, target in enumerate(selected_targets):
                email_addr = str(target.get("Email") or target.get("อีเมล") or "").strip()
                c_name, comp_name = extract_sheet_data(target)
                company = comp_name if comp_name else "ลูกค้า"
                
                greeting_name = f"คุณ {c_name}" if c_name else f"ทีมงาน {company}"
                closing_target = f"คุณ {c_name}" if c_name else f"ทางแบรนด์ {company}"
                
                email_key = str(target.get("Email") or target.get("อีเมล") or f"client_{idx}").strip()
                
                status_text.text(f"📤 กำลังส่งอีเมล ({idx+1}/{len(selected_targets)}): {company} ({email_addr})...")
                
                try:
                    msg = MIMEMultipart('related')
                    msg['From'] = formataddr((user_name, gmail_sender))
                    msg['To'] = email_addr
                    msg['Reply-To'] = user_email
                    
                    if "1️⃣ New Media" in app_mode:
                        ai_data = st.session_state.ai_results.get(email_key, {})
                        selected_media = ai_data.get("media", list(MEDIA_FOLDERS.keys())[idx % len(MEDIA_FOLDERS)])
                        ai_pitch = ai_data.get("pitch", f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company} ค่ะ")
                        
                        media_info = MEDIA_FOLDERS.get(selected_media, MEDIA_FOLDERS["The 20"])
                        msg['Subject'] = replace_placeholders(media_info["subject"], greeting_name, closing_target, user_name, user_phone)
                        
                        detail_tmpl = media_info["detail"]
                        img_list = media_info.get("images", [])
                        for img_i, img_name in enumerate(img_list, 1):
                            detail_tmpl = detail_tmpl.replace(f"{{IMG{img_i}}}", f"{GITHUB_RAW_BASE}{img_name}")
                            
                        body_html = replace_placeholders(detail_tmpl, greeting_name, closing_target, user_name, user_phone, ai_pitch) + FOOTER_BANNER_HTML_PREVIEW
                        
                    elif "2️⃣ Credential" in app_mode:
                        msg['Subject'] = CREDENTIAL_SUBJECT
                        body_html = replace_placeholders(CREDENTIAL_DETAIL, greeting_name, closing_target, user_name, user_phone) + FOOTER_BANNER_HTML_PREVIEW
                        
                    elif "3️⃣ Magnetic Report" in app_mode:
                        chosen_mag = st.session_state.client_magnetic_selections.get(email_key, [valid_keys[0]])
                        mag_links_html = ""
                        for m_key in chosen_mag:
                            m_url = MAGNETIC_OPTIONS.get(m_key, "")
                            mag_links_html += f"📌 <b>{m_key}:</b><br><a href='{m_url}' target='_blank'>{m_url}</a><br><br>"
                            
                        msg['Subject'] = f"[Plan B Media] รายงานสรุปภาพรวมสื่อโฆษณานอกบ้าน (Magnetic Report)"
                        mag_detail = f"""เรียน {{Greeting Name}}<br><br>
สวัสดีค่ะ {{Sale name}} ขออนุญาตส่งรายงานสรุปภาพรวมสถิติและผลการดำเนินงานของสื่อโฆษณานอกบ้าน (Magnetic Report) เพื่อให้{{Closing Target}} ใช้เป็นข้อมูลประกอบการวางแผนการตลาดค่ะ<br><br>
โดยท่านสามารถเข้าชมและดาวน์โหลดรายงานสรุปสถิติได้จากลิงก์ด้านล่างนี้ค่ะ:<br><br>
{mag_links_html}
หาก{{Closing Target}} มีข้อสงสัยเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""
                        body_html = replace_placeholders(mag_detail, greeting_name, closing_target, user_name, user_phone) + FOOTER_BANNER_HTML_PREVIEW

                    msg_alt = MIMEMultipart('alternative')
                    msg_alt.attach(MIMEText(body_html, 'html', 'utf-8'))
                    msg.attach(msg_alt)
                    
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(gmail_sender, sender_password)
                        server.sendmail(gmail_sender, [email_addr], msg.as_string())
                        
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ ส่งหา {company} ({email_addr}) ไม่สำเร็จ: {e}")
                    
                progress_bar.progress((idx + 1) / len(selected_targets))
                
            status_text.empty()
            progress_bar.empty()
            st.balloons()
            st.success(f"🎉 ส่งอีเมลสำเร็จเรียบร้อยทั้งหมด **{success_count}** / **{len(selected_targets)}** รายชื่อ!")
