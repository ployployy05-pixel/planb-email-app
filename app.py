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

# DATA TEMPLATES FOR MEDIA
MEDIA_FOLDERS = {
    "The 20": {
        "title": "The 20",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "detail": """เรียน คุณ {{Client name}}<br><br>
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
    "rama 9 connected": {
        "title": "rama 9 connected",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "detail": """เรียน คุณ {{Client name}}<br><br>
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
หากคุณ {{Client name}} สนใจสื่อนี้ หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["rama9_1.jpg", "rama9_2.jpg"]
    },
    "Central Network [New Package]": {
        "title": "Central Network [New Package]",
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "detail": """เรียน คุณ {{Client name}}<br><br>
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
        "detail": """เรียน คุณ {{Client name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ The Skyline สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ บนถนนทางเข้าสนามบินสุวรรณภูมิ<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The Skyline Location">
</div><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG2}" width="600" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Passenger Traffic">
</div><br>
_________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ The Skyline หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "images": ["skyline_1.jpg", "skyline_2.jpg"]
    }
}

# 🤖 AI ENGINE FUNCTION (ใช้ Gemini REST API ยิงตรงผ่าน urllib)
def run_ai_smart_match_and_pitch(client_name, company_name):
    available_media_list = list(MEDIA_FOLDERS.keys())
    
    # Fallback กรณีไม่มี API Key หรือยิงไม่ผ่าน
    if not GEMINI_API_KEY:
        selected_media = "The 20" if "vivo" in company_name.lower() or "tech" in company_name.lower() else available_media_list[0]
        reason = f"AI วิเคราะห์ว่าแบรนด์ {company_name} เป็นแบรนด์เทคโนโลยี/สมาร์ทโฟนยุคใหม่ สื่อ The 20 บนทางด่วน CBD มีความยาว 2.5 กม. คมชัดสูง ช่วยสร้าง Impact และสะกดสายตากลุ่มคนรุ่นใหม่ได้ดีที่สุด"
        pitch = f"ทาง Plan B ขอแนะนำสื่อโฆษณาดิจิทัลใหม่ล่าสุดที่ตอบโจทย์การสร้างความโดดเด่นให้กับนวัตกรรมของแบรนด์ {company_name} ของคุณ {client_name} ได้อย่างสมบูรณ์แบบค่ะ"
        return selected_media, reason, pitch

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""
        คุณคือ AI Sales Agent ผู้เชี่ยวชาญของ Plan B Media
        ลูกค้า: ชื่อคุณ {client_name}, แบรนด์/บริษัท: {company_name}
        รายการสื่อ OOH ที่มีให้เลือก: {json.dumps(available_media_list, ensure_ascii=False)}

        หน้าที่ของคุณ:
        1. วิเคราะห์ประเภทธุรกิจของแบรนด์ {company_name}
        2. เลือกสื่อ 1 ตัวจากรายการสื่อที่มีให้ ที่เหมาะสมที่สุดกับแบรนด์นี้
        3. เขียนเหตุผลสั้นๆ 2 บรรทัด ว่าทำไมถึงเลือกสื่อนี้ให้แบรนด์นี้ (reason)
        4. แต่งข้อความเกริ่นนำเสนอขายสั้นๆ 2 บรรทัด ภาษาไทย สุภาพ เป็นกันเอง และดูเป็นมืออาชีพ (pitch)

        ตอบกลับเป็น JSON Format เท่านั้น ดังนี้:
        {{
            "selected_media": "ชื่อสื่อที่เลือกตรงเป้าเป๊ะๆ จากรายการ",
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
            
            s_media = res_json.get("selected_media", available_media_list[0])
            if s_media not in MEDIA_FOLDERS:
                s_media = available_media_list[0]
            return s_media, res_json.get("reason", ""), res_json.get("pitch", "")
    except Exception:
        selected_media = "The 20" if "vivo" in company_name.lower() else available_media_list[0]
        reason = f"AI วิเคราะห์ว่าแบรนด์ {company_name} เหมาะสมที่สุดกับสื่อ {selected_media} ในการเข้าถึงกลุ่มเป้าหมายใจกลางเมือง"
        pitch = f"ขอแนะนำสื่อโฆษณาทำเลศักยภาพสูงที่ตอบโจทย์และเสริมภาพลักษณ์ให้กับแบรนด์ {company_name} ของคุณ {client_name} ค่ะ"
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
if 'ai_selected_media' not in st.session_state:
    st.session_state.ai_selected_media = list(MEDIA_FOLDERS.keys())[0]
if 'ai_reason' not in st.session_state:
    st.session_state.ai_reason = ""
if 'ai_pitch' not in st.session_state:
    st.session_state.ai_pitch = ""

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
        nc = st.text_input("ชื่อบริษัท / แบรนด์")
        nn = st.text_input("ชื่อผู้ติดต่อ ({{Client name}})")
        ne = st.text_input("อีเมลผู้รับ")
        if st.button("➕ เพิ่มลูกค้ารายนี้"):
            if ne:
                st.session_state.recipients.append({
                    "ส่งอีเมล?": True,
                    "ที่มา": "Manual",
                    "ชื่อบริษัท": nc if nc else "Vivo",
                    "ชื่อผู้ติดต่อ": nn if nn else "ลูกค้าผู้มีเกียรติ",
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
    
    # ดึงรายชื่อลูกค้าจริงจากตาราง Step 01
    recipients_list = st.session_state.recipients if st.session_state.recipients else [
        {"ชื่อผู้ติดต่อ": "วิชญาดา", "ชื่อบริษัท": "Vivo", "อีเมล": "wichayada.ph@planbmedia.co.th"}
    ]
    
    client_options = []
    for r in recipients_list:
        c_name = r.get("ชื่อผู้ติดต่อ") or r.get("Client name") or r.get("ชื่อ") or "ลูกค้า"
        comp_name = r.get("ชื่อบริษัท") or r.get("Brand") or r.get("Company") or "Vivo"
        client_options.append(f"{c_name} (แบรนด์: {comp_name})")

    with col_left:
        st.markdown(f"#### 🎯 โหมดปัจจุบัน: `{app_mode}`")
        st.info("🤖 **AI Runtime Agent:** เลือกแบรนด์ลูกค้า แล้วกดให้ Gemini AI วิเคราะห์ธุรกิจพร้อมเลือกสื่อ OOH ที่เหมาะสมให้อัตโนมัติ")
        
        selected_client_str = st.selectbox("🎯 เลือกลูกค้าสำหรับพรีวิวทดสอบ AI:", options=client_options, index=0)
        selected_index = client_options.index(selected_client_str)
        target_rec = recipients_list[selected_index]
        
        # 📌 สกัดชื่อผู้ติดต่อจริง และชื่อแบรนด์บริษัท
        sample_client = target_rec.get("ชื่อผู้ติดต่อ") or target_rec.get("Client name") or target_rec.get("ชื่อ") or "ลูกค้าผู้มีเกียรติ"
        sample_company = target_rec.get("ชื่อบริษัท") or target_rec.get("Brand") or target_rec.get("Company") or "Vivo"

        if st.button("🤖 ให้ AI วิเคราะห์แบรนด์ & เลือกสื่อ OOH ที่เหมาะสมให้อัตโนมัติ", type="primary"):
            with st.spinner(f"🤖 Gemini AI กำลังวิเคราะห์ธุรกิจแบรนด์ '{sample_company}' และประมวลผลการเลือกสื่อ..."):
                s_media, r_reason, p_pitch = run_ai_smart_match_and_pitch(sample_client, sample_company)
                st.session_state.ai_selected_media = s_media
                st.session_state.ai_reason = r_reason
                st.session_state.ai_pitch = p_pitch
                st.success("✅ AI ประมวลผลและเลือกสื่อเรียบร้อย!")

        # แสดงกล่องเหตุผลจาก AI
        if st.session_state.ai_reason:
            st.success(f"🎯 **สื่อที่ AI แนะนำให้แบรนด์ {sample_company}:** `{st.session_state.ai_selected_media}`\n\n💡 **เหตุผลจาก AI:** {st.session_state.ai_reason}")

        # เลือก Mode
        if "1️⃣ New Media" in app_mode:
            selected_folder = st.selectbox(
                "เลือกรายการสื่อ New Media (หรือให้ AI เลือกให้อัตโนมัติ):",
                options=list(MEDIA_FOLDERS.keys()),
                index=list(MEDIA_FOLDERS.keys()).index(st.session_state.ai_selected_media) if st.session_state.ai_selected_media in MEDIA_FOLDERS else 0
            )
            st.session_state.selected_media_folder = selected_folder
            current_subject = MEDIA_FOLDERS[selected_folder]["subject"]
            
            detail_tmpl = MEDIA_FOLDERS[selected_folder]["detail"]
            img_list = MEDIA_FOLDERS[selected_folder].get("images", [])
            for idx, img_name in enumerate(img_list, 1):
                detail_tmpl = detail_tmpl.replace(f"{{IMG{idx}}}", f"{GITHUB_RAW_BASE}{img_name}")
            current_detail = detail_tmpl
            
        elif "2️⃣ Credential" in app_mode:
            current_subject = CREDENTIAL_SUBJECT
            current_detail = CREDENTIAL_DETAIL
            
        elif "3️⃣ Magnetic Report" in app_mode:
            current_items = st.session_state.get('selected_mag_items', [])
            default_vals = [item for item in current_items if item in valid_keys] or [valid_keys[0]]

            selected_mag_items = st.multiselect("เลือกรายงาน/สื่อ Magnetic ที่ต้องการส่ง:", options=valid_keys, default=default_vals)
            st.session_state.selected_mag_items = selected_mag_items
            current_subject = "[Plan B Media] Monthly Magnetic Report Update – สรุปข้อมูลสถิติ OOH ประจำเดือน"
            
            items_html = ""
            for idx, item in enumerate(selected_mag_items, 1):
                link = MAGNETIC_OPTIONS[item]
                items_html += f"{idx}. <b>{item}</b><br>&nbsp;&nbsp;&nbsp;&nbsp;📌 ลิงก์ดาวน์โหลด: <a href='{link}' target='_blank'>{link}</a><br><br>"
            
            current_detail = f"""เรียน คุณ {{Client name}}<br><br>
{{AI_PITCH}}<br><br>
ขออนุญาตนำส่ง Magnetic Report สรุปข้อมูลสถิติ OOH ประจำเดือน รายละเอียดสถิติ Eyeballs และ Grid Reach ตามรายการสื่อที่คุณ {{Client name}} สนใจ ดังนี้ค่ะ:<br><br>
{items_html}
ทาง Plan B หวังว่าข้อมูล Magnetic Report จะเป็นประโยชน์สำหรับการวางแผนกิจกรรมทางการตลาดของคุณ {{Client name}} ค่ะ<br><br>
หากคุณ {{Client name}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""

    with col_right:
        st.markdown("#### 📧 ตัวอย่างอีเมลที่จะถูกจัดส่ง (Preview)")
        
        ai_pitch_text = st.session_state.ai_pitch if st.session_state.ai_pitch else f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {sample_company} ของคุณ {sample_client} ได้อย่างสมบูรณ์แบบค่ะ"
        
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
    st.info(f"📬 พร้อมส่งอีเมลหาลูกค้าทั้งหมด **{len(selected_targets)}** รายชื่อ ในโหมด `{app_mode}` (ประมวลผลข้อความและสื่อด้วย AI สำหรับผู้รับแต่ละรายสดๆ)")
    
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
                            
                    company_name = target.get("ชื่อบริษัท") or target.get("Brand") or target.get("Company") or "Vivo"
                    client_email = str(target.get("อีเมล") or target.get("Email") or "").strip()
                    
                    if client_email and "@" in client_email:
                        # 🤖 AI Runtime Agent: ประมวลผลวิเคราะห์แบรนด์และเลือกสื่อสดๆ รายบุคคล
                        ai_media_key, ai_reason_text, ai_personalized_pitch = run_ai_smart_match_and_pitch(client_name, company_name)
                        
                        msg = MIMEMultipart("related")
                        msg['From'] = formataddr((user_name, gmail_sender))
                        msg['To'] = client_email
                        msg['Reply-To'] = user_email
                        
                        if "1️⃣ New Media" in app_mode:
                            media_info = MEDIA_FOLDERS.get(ai_media_key, MEDIA_FOLDERS[list(MEDIA_FOLDERS.keys())[0]])
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
                    status_text.text(f"🤖 AI กำลังวิเคราะห์แบรนด์ {company_name} และส่งอีเมลถึง: คุณ {client_name}...")
                    
                server.quit()
                st.success(f"🎉 AI ประมวลผลวิเคราะห์และส่งอีเมลสำเร็จทั้งหมด {success_count} รายชื่อ!")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการส่งผ่าน SMTP: {e}")
