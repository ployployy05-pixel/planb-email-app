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
        "description": "จอ LED ดิจิทัลยาวที่สุดในโลก 2.5 กม. บนทางด่วนเฉลิมมหานคร CBD เหมาะกับ Tech, ยานยนต์, แบรนด์ใหญ่ที่ต้องการ Impact สูง",
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
    "rama 9 connected": {
        "title": "rama 9 connected",
        "description": "สื่อดิจิทัลใจกลาง CBD พระราม 9 ย่านธุรกิจ RCA ออฟฟิศ B2B การเงิน อสังหาฯ",
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
    },
    "Central Network [New Package]": {
        "title": "Central Network [New Package]",
        "description": "สื่อในห้างสรรพสินค้า CentralWorld ทั่วประเทศ เหมาะกับ แฟชั่น เครื่องสำอาง รองเท้า สนีกเกอร์ อาหาร ร้านค้า Retail FMCG",
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
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "description": "ป้ายภาพนิ่งขนาดใหญ่ทางเข้าสนามบินสุวรรณภูมิ เหมาะกับสินค้าพรีเมียม ท่องเที่ยว ท่องเที่ยวต่างประเทศ ลักชัวรี",
        "detail": """เรียน {{Greeting Name}}<br><br>
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

# 🤖 AI ENGINE FUNCTION (FOR NEW MEDIA MODE ONLY)
def run_ai_smart_match_and_pitch(contact_name, company_name):
    available_media_list = list(MEDIA_FOLDERS.keys())
    has_contact = bool(contact_name and str(contact_name).strip())
    
    comp_lower = company_name.lower()
    if any(k in comp_lower for k in ["คอสเมคอน", "สนีกเกอร์", "มัสตาร์ด", "fashion", "beauty", "เครื่องสำอาง", "รองเท้า", "retail"]):
        fallback_media = "Central Network [New Package]"
    elif any(k in comp_lower for k in ["สุกี้", "ร้านอาหาร", " food", "คอร์ป"]):
        fallback_media = "Central Network [New Package]"
    elif any(k in comp_lower for k in ["อสังหา", "การเงิน", "ประกัน", "อาคาร"]):
        fallback_media = "rama 9 connected"
    elif any(k in comp_lower for k in ["สุวรรณภูมิ", " travel", "luxury", "พรีเมียม"]):
        fallback_media = "The Skyline"
    else:
        fallback_media = "The 20"

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
        
        รายการสื่อ OOH และจุดเด่นประจำสื่อ:
        {json.dumps(media_context, ensure_ascii=False, indent=2)}

        คำสั่งสำคัญ:
        1. วิเคราะห์ว่าแบรนด์ {company_name} ทำธุรกิจประเภทใด
        2. พิจารณาเลือกสื่อเพียง 1 ตัวจากรายการสื่อด้านบนที่เข้ากับประเภทธุรกิจของแบรนด์นี้มากที่สุด
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

# NOTE TEMPLATES (EXACT SALES NOTE FORMAT)
CREDENTIAL_LINK = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"
CREDENTIAL_SUBJECT = "[Plan B Media] ขออนุญาตนัดเข้าพบเพื่อนำเสนอสื่อโฆษณานอกบ้านสำหรับปี 2026"
CREDENTIAL_DETAIL = f"""เรียน {{Greeting Name}}<br><br>
ขออนุญาตแนะนำตัว {{Sale name}} จาก บริษัท แพลนบี มีเดีย จำกัด (มหาชน) ค่ะ<br><br>
📌 <b>Plan B Media Profile / Credential:</b><br>
คุณสามารถเลือกเข้าชมภาพรวมสื่อทั้งหมดได้ที่ลิงก์นี้ค่ะ: <a href="{CREDENTIAL_LINK}" target="_blank">{CREDENTIAL_LINK}</a><br><br>
หาก{{Closing Target}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือตอบกลับอีเมลนี้ได้เลยค่ะ"""

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
                    
                    s_media, r_reason, p_pitch = run_ai_smart_match_and_pitch(c_name, company)
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
                selected_media = ai_data.get("media", list(MEDIA_FOLDERS.keys())[0])
                ai_pitch = ai_data.get("pitch", default_pitch)
                ai_reason = ai_data.get("reason", "AI วิเคราะห์สื่อที่เหมาะสมที่สุดสำหรับแบรนด์นี้")

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
                        subj_text = str(media_info["subject"]).replace("{{Greeting Name}}", greeting_name).replace("{{Client name}}", greeting_name)
                        
                        detail_tmpl = media_info["detail"]
                        img_list = media_info.get("images", [])
                        for img_i, img_name in enumerate(img_list, 1):
                            detail_tmpl = detail_tmpl.replace(f"{{IMG{img_i}}}", f"{GITHUB_RAW_BASE}{img_name}")
                            
                        safe_body = str(detail_tmpl).replace("{AI_PITCH}", ai_pitch).replace("{{AI_PITCH}}", ai_pitch)
                        safe_body = safe_body.replace("{{Greeting Name}}", greeting_name).replace("{{Closing Target}}", closing_target)
                        safe_body = safe_body.replace("{{Sale name}}", str(user_name)).replace("{Sale name}", str(user_name))
                        safe_body = safe_body.replace("{{Tel}}", str(user_phone)).replace("{Tel}", str(user_phone))
                        
                        preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
                        st.caption(f"📌 หัวข้อ: {subj_text}")
                        st.components.v1.html(preview_html, height=400, scrolling=True)

        # 2️⃣ MODE 2: CREDENTIAL (EXACT SALES NOTE - ALL CLIENTS)
        elif "2️⃣ Credential" in app_mode:
            st.info("📌 **Credential Mode:** ใช้ข้อความแนะนำตัวและแนบลิงก์ Profile ตามแบบแผน Note ทางการ (ไม่ต้องใช้ AI)")
            
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
                    safe_body = str(CREDENTIAL_DETAIL).replace("{{Greeting Name}}", greeting_name).replace("{{Closing Target}}", closing_target)
                    safe_body = safe_body.replace("{{Sale name}}", str(user_name)).replace("{Sale name}", str(user_name))
                    safe_body = safe_body.replace("{{Tel}}", str(user_phone)).replace("{Tel}", str(user_phone))
                    
                    preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
                    st.caption(f"📌 หัวข้อ: {subj_text}")
                    st.components.v1.html(preview_html, height=350, scrolling=True)

        # 3️⃣ MODE 3: MAGNETIC REPORT (MANUAL SELECT - ALL CLIENTS)
        elif "3️⃣ Magnetic Report" in app_mode:
            st.info("📊 **Magnetic Report Mode:** เลือกประเภทรายงานและระบุรอบเดือนที่จะจัดส่งให้ลูกค้าทุกคนที่เลือก")
            report_month = st.text_input("ระบุรอบเดือนของรายงาน (เช่น ประจำเดือนมกราคม 2026):", value="ประจำเดือนมกราคม 2026")
            
            current_items = st.session_state.get('selected_mag_items', [])
            default_vals = [item for item in current_items if item in valid_keys] or [valid_keys[0]]

            selected_mag_items = st.multiselect("เลือกรายงาน/สื่อ Magnetic ที่ต้องการส่งให้ทุกแบรนด์:", options=valid_keys, default=default_vals)
            st.session_state.selected_mag_items = selected_mag_items
            
            items_html = ""
            for i_idx, item in enumerate(selected_mag_items, 1):
                link = MAGNETIC_OPTIONS[item]
                items_html += f"{i_idx}. <b>{item}</b><br>&nbsp;&nbsp;&nbsp;&nbsp;📌 ลิงก์ดาวน์โหลด: <a href='{link}' target='_blank'>{link}</a><br><br>"
            
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
                    subj_text = f"[Plan B Media] Monthly Magnetic Report Update – สรุปข้อมูลสถิติ OOH {report_month}"
                    mag_tmpl = f"""เรียน {{Greeting Name}}<br><br>
ขออนุญาตนำส่ง Magnetic Report สรุปข้อมูลสถิติ OOH {report_month} รายละเอียดสถิติ Eyeballs และ Grid Reach ตามรายการสื่อที่{{Closing Target}} สนใจ ดังนี้ค่ะ:<br><br>
{items_html}
ทาง Plan B หวังว่าข้อมูล Magnetic Report จะเป็นประโยชน์สำหรับการวางแผนกิจกรรมทางการตลาดของ{{Closing Target}} ค่ะ<br><br>
หาก{{Closing Target}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""
                    
                    safe_body = str(mag_tmpl).replace("{{Greeting Name}}", greeting_name).replace("{{Closing Target}}", closing_target)
                    safe_body = safe_body.replace("{{Sale name}}", str(user_name)).replace("{Sale name}", str(user_name))
                    safe_body = safe_body.replace("{{Tel}}", str(user_phone)).replace("{Tel}", str(user_phone))
                    
                    preview_html = safe_body + FOOTER_BANNER_HTML_PREVIEW
                    st.caption(f"📌 หัวข้อ: {subj_text}")
                    st.components.v1.html(preview_html, height=350, scrolling=True)

# ==========================================
# STEP 03 : BATCH EMAIL SENDING
# ==========================================
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("🚀 STEP 03 : ยืนยันยอด & กดส่ง Batch Email")
    
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    st.info(f"📬 พร้อมส่งอีเมลหาลูกค้าที่เลือกไว้ทั้งหมด **{len(selected_targets)}** รายชื่อ ในโหมด `{app_mode}`")
    
    if selected_targets:
        with st.expander("📋 ตรวจสอบรายชื่อลูกค้าที่จะจัดส่งในรอบนี้อีกครั้ง"):
            for idx, t in enumerate(selected_targets, 1):
                c_name, comp_name = extract_sheet_data(t)
                target_label = f"คุณ {c_name} ({comp_name})" if c_name and comp_name else (comp_name if comp_name else f"คุณ {c_name}")
                st.write(f"{idx}. **{target_label}** — {t.get('Email') or t.get('อีเมล')}")

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
                    contact_name, company_name = extract_sheet_data(target)
                    if not company_name:
                        company_name = "ลูกค้า"
                    
                    if contact_name:
                        greeting_name = f"คุณ {contact_name}"
                        closing_target = f"คุณ {contact_name}"
                    else:
                        greeting_name = f"ทีมงาน {company_name}"
                        closing_target = f"ทางแบรนด์ {company_name}"

                    client_email = str(target.get("Email") or target.get("อีเมล") or "").strip()
                    
                    if client_email and "@" in client_email:
                        msg = MIMEMultipart("related")
                        msg['From'] = formataddr((user_name, gmail_sender))
                        msg['To'] = client_email
                        msg['Reply-To'] = user_email
                        
                        # MODE 1: NEW MEDIA
                        if "1️⃣ New Media" in app_mode:
                            ai_data = st.session_state.ai_results.get(client_email, {})
                            if ai_data:
                                ai_media_key = ai_data.get("media")
                                ai_personalized_pitch = ai_data.get("pitch")
                            else:
                                ai_media_key, _, ai_personalized_pitch = run_ai_smart_match_and_pitch(contact_name, company_name)

                            media_info = MEDIA_FOLDERS.get(ai_media_key, MEDIA_FOLDERS[list(MEDIA_FOLDERS.keys())[0]])
                            subject_tmpl = media_info["subject"]
                            detail_tmpl = media_info["detail"]
                            img_list = media_info.get("images", [])
                            for i, _ in enumerate(img_list, 1):
                                detail_tmpl = detail_tmpl.replace(f"{{IMG{i}}}", f"cid:media_img_{i}")
                            
                            body_html = str(detail_tmpl).replace("{AI_PITCH}", ai_personalized_pitch).replace("{{AI_PITCH}}", ai_personalized_pitch)

                        # MODE 2: CREDENTIAL
                        elif "2️⃣ Credential" in app_mode:
                            subject_tmpl = CREDENTIAL_SUBJECT
                            detail_tmpl = CREDENTIAL_DETAIL
                            img_list = []
                            body_html = str(detail_tmpl)

                        # MODE 3: MAGNETIC REPORT
                        else:
                            chosen_items = st.session_state.get('selected_mag_items', [valid_keys[0]])
                            items_html = ""
                            for i, item in enumerate(chosen_items, 1):
                                link = MAGNETIC_OPTIONS.get(item, MAGNETIC_OPTIONS[valid_keys[0]])
                                items_html += f"{i}. <b>{item}</b><br>&nbsp;&nbsp;&nbsp;&nbsp;📌 ลิงก์ดาวน์โหลด: <a href='{link}' target='_blank'>{link}</a><br><br>"
                            subject_tmpl = "[Plan B Media] Monthly Magnetic Report Update – สรุปข้อมูลสถิติ OOH ประจำเดือน"
                            detail_tmpl = f"เรียน {{Greeting Name}}<br><br>ขออนุญาตนำส่ง Magnetic Report สรุปข้อมูลสถิติ OOH ประจำเดือน รายละเอียดสถิติ Eyeballs และ Grid Reach ตามรายการสื่อที่{{Closing Target}} สนใจ ดังนี้ค่ะ:<br><br>{items_html}ทาง Plan B หวังว่าข้อมูล Magnetic Report จะเป็นประโยชน์สำหรับการวางแผนกิจกรรมทางการตลาดของ{{Closing Target}} ค่ะ<br><br>หาก{{Closing Target}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"
                            img_list = []
                            body_html = str(detail_tmpl)

                        sub_text = str(subject_tmpl).replace("{{Greeting Name}}", greeting_name).replace("{{Client name}}", greeting_name)
                        sub_text = sub_text.replace("{{Sale name}}", str(user_name)).replace("{{Tel}}", str(user_phone))
                        msg['Subject'] = sub_text
                        
                        body_html = body_html.replace("{{Greeting Name}}", greeting_name).replace("{{Closing Target}}", closing_target)
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
                    status_text.text(f"🚀 กำลังส่งอีเมลถึง: {greeting_name} ({company_name})...")
                    
                server.quit()
                st.success(f"🎉 ส่งอีเมลสำเร็จทั้งหมด {success_count} รายชื่อ!")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการส่งผ่าน SMTP: {e}")
