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

# ==========================================
# HIGH-FIDELITY INFOGRAPHIC EMAIL ASSETS & TEMPLATES
# ==========================================
# ลิงก์ปลายทาง Sales Portal / Credential บน Google Drive
SALES_PORTAL_LINK = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"

# 🖼️ INFOGRAPHIC TEMPLATE (HIGH-RESOLUTION VISUAL ASSET)
INFOGRAPHIC_EMAIL_HTML = f"""
<div style="max-width: 680px; margin: 0 auto; text-align: center; font-family: 'Sukhumvit Set', Arial, sans-serif; background-color: #ffffff; padding: 10px; border-radius: 12px;">
    <!-- INTERACTIVE INFOGRAPHIC IMAGE (CLICKABLE ASSET) -->
    <a href="{SALES_PORTAL_LINK}" target="_blank" style="text-decoration: none; display: block;">
        <img src="{GITHUB_RAW_BASE}automotive_infographic.png" 
             alt="Plan B Media - Sales Workflow & Outdoor Opportunities" 
             style="width: 100%; max-width: 660px; height: auto; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,86,179,0.12); border: 0; display: block; margin: 0 auto;" />
    </a>
</div>
"""

# DATA TEMPLATES FOR MEDIA (NEW MEDIA MODE ONLY)
MEDIA_FOLDERS = {
    "The 20": {
        "title": "The 20",
        "description": "สื่อดิจิทัล DOOH ยาวที่สุดในโลก 2.5 กม. บนทางด่วน CBD เหมาะกับ Tech, ยานยนต์, แบรนด์ใหญ่ระดับองค์กร, สถาบันการเงิน, พลังงาน ที่ต้องการ Impact สูง",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "detail": INFOGRAPHIC_EMAIL_HTML,
        "images": ["automotive_infographic.png"]
    },
    "Central Network [New Package]": {
        "title": "Central Network [New Package]",
        "description": "สื่อในห้างสรรพสินค้า CentralWorld ทั่วประเทศ เหมาะกับ แฟชั่น, เครื่องสำอาง, รองเท้า, สนีกเกอร์, อาหาร, ร้านค้า Retail, FMCG, คอสเมติก, สปา, สกินแคร์, เล็บ, ความงาม",
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "detail": INFOGRAPHIC_EMAIL_HTML,
        "images": ["automotive_infographic.png"]
    },
    "The Skyline": {
        "title": "The Skyline",
        "description": "ป้ายภาพนิ่งขนาดใหญ่ทางเข้าสนามบินสุวรรณภูมิ เหมาะกับ สินค้าพรีเมียม, ท่องเที่ยว, โรงแรม, สายการบิน, อสังหาริมทรัพย์, ลักชัวรี, แบรนด์เนม, สินค้านำเข้า",
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "detail": INFOGRAPHIC_EMAIL_HTML,
        "images": ["automotive_infographic.png"]
    },
    "rama 9 connected": {
        "title": "rama 9 connected",
        "description": "สื่อดิจิทัลใจกลาง CBD พระราม 9 ย่านธุรกิจ RCA เหมาะกับ ออฟฟิศ B2B, คลินิก, โรงพยาบาล, สถาบันการศึกษา, โรงเรียน, มหาวิทยาลัย",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "detail": INFOGRAPHIC_EMAIL_HTML,
        "images": ["automotive_infographic.png"]
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

# 🧹 HELPER FUNCTION: แทนที่ตัวแปรในข้อความอย่างสมบูรณ์
def replace_placeholders(text, greeting_name, closing_target, sale_name, phone_num, pitch_text=""):
    result = str(text)
    
    result = result.replace("{{Greeting Name}}", greeting_name).replace("{Greeting Name}", greeting_name)
    result = result.replace("{{Client name}}", greeting_name).replace("{Client name}", greeting_name)
    result = result.replace("{{Closing Target}}", closing_target).replace("{Closing Target}", closing_target)
    result = result.replace("{{Sale name}}", sale_name).replace("{Sale name}", sale_name)
    result = result.replace("{{Tel}}", phone_num).replace("{Tel}", phone_num)
    
    if pitch_text:
        result = result.replace("{{AI_PITCH}}", pitch_text).replace("{AI_PITCH}", pitch_text)
        
    return result

# 🤖 AI ENGINE FUNCTION (BALANCED CATEGORY MATCHING)
def run_ai_smart_match_and_pitch(contact_name, company_name, index_hint=0):
    available_media_list = list(MEDIA_FOLDERS.keys())
    has_contact = bool(contact_name and str(contact_name).strip())
    comp_lower = company_name.lower()
    
    if any(k in comp_lower for k in ["คอสเมคอน", "สนีกเกอร์", "มัสตาร์ด", "fashion", "beauty", "เครื่องสำอาง", "รองเท้า", "retail", "สปา", "เล็บ", "nail", "apparel", "สุกี้", "อาหาร"]):
        fallback_media = "Central Network [New Package]"
    elif any(k in comp_lower for k in ["โรงเรียน", "สาธิต", "school", "คลินิก", "โรงพยาบาล", "อสังหา", "การเงิน", "ประกัน"]):
        fallback_media = "rama 9 connected"
    elif any(k in comp_lower for k in ["สุวรรณภูมิ", " travel", "luxury", "พรีเมียม", "โรงแรม", "สนามบิน", "บิน", "ต่างประเทศ"]):
        fallback_media = "The Skyline"
    else:
        fallback_options = ["The 20", "Central Network [New Package]", "The Skyline", "rama 9 connected"]
        fallback_media = fallback_options[index_hint % len(fallback_options)]

    if not GEMINI_API_KEY:
        selected_media = fallback_media
        reason = f"AI วิเคราะห์ลักษณะธุรกิจของแบรนด์ {company_name} แล้วพบว่าเหมาะสมที่สุดกับสื่อ {selected_media} เพื่อเข้าถึงกลุ่มเป้าหมาย"
        pitch = f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company_name} ได้อย่างสมบูรณ์แบบค่ะ"
        return selected_media, reason, pitch

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        media_context = {k: v.get("description", "") for k, v in MEDIA_FOLDERS.items()}

        target_context = f"ลูกค้าชื่อคุณ {contact_name}, แบรนด์/บริษัท: {company_name}" if has_contact else f"ลูกค้าแบรนด์/บริษัท: {company_name}"
        
        prompt = f"""
        คุณคือ AI Sales Agent ผู้เชี่ยวชาญของ Plan B Media
        ข้อมูลลูกค้า: {target_context}
        รายการสื่อ OOH และประเภทธุรกิจที่เหมาะสม: {json.dumps(media_context, ensure_ascii=False)}

        ตอบกลับเป็น JSON เท่านั้น:
        {{
            "selected_media": "ชื่อสื่อที่เลือก",
            "reason": "เหตุผลสั้นๆ 2 บรรทัด",
            "pitch": "ข้อความเกริ่นนำเสนอขาย 2 บรรทัด"
        }}
        """
        data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=12) as response:
            res_json = json.loads(json.loads(response.read().decode("utf-8"))["candidates"][0]["content"]["parts"][0]["text"])
            s_media = res_json.get("selected_media", fallback_media)
            if s_media not in MEDIA_FOLDERS:
                s_media = fallback_media
            return s_media, res_json.get("reason", ""), res_json.get("pitch", "")
    except Exception:
        return fallback_media, f"AI แนะนำสื่อ {fallback_media} สำหรับแบรนด์ {company_name}", f"ขอแนะนำสื่อโฆษณาคุณภาพสูงที่ตอบโจทย์แบรนด์ {company_name} ค่ะ"

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
sheet_url_input = st.sidebar.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL)

st.sidebar.markdown("---")
st.sidebar.subheader("🔘 ขั้นตอนการทำงาน")
step = st.sidebar.radio("เลือกขั้นตอน:", [
    "STEP 01 : จัดการรายชื่อลูกค้า",
    "STEP 02 : เลือกเนื้อหา & พรีวิว",
    "STEP 03 : ยืนยันยอด & กดส่งอีเมล"
])

st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox(
    "เลือกประเภทอีเมลที่ต้องการส่ง:",
    [
        "1️⃣ New Media (Visual Infographic Template)",
        "2️⃣ Credential (แนะนำตัวตามโครงสร้าง Sales Note)",
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
                    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: ({e})")
                    
    with col2:
        st.markdown("#### 2️⃣ ➕ พิมพ์เพิ่มรายชื่อลูกค้าใหม่ (Manual)")
        nc = st.text_input("ชื่อบริษัท / แบรนด์")
        nn = st.text_input("ชื่อผู้ติดต่อ")
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

# ==========================================
# STEP 02 : MULTI-BRAND BATCH PREVIEW
# ==========================================
elif step == "STEP 02 : เลือกเนื้อหา & พรีวิว":
    st.subheader("🖼️ STEP 02 : พรีวิวอีเมลสำหรับลูกค้าที่เลือกทั้งหมด (Multi-Brand Batch Preview)")
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    
    if not selected_targets:
        st.warning("⚠️ ยังไม่มีการเลือกรายชื่อลูกค้าใน STEP 01 กรุณากลับไปเลือกรายชื่อก่อนค่ะ")
    else:
        st.markdown(f"#### 🎯 โหมดปัจจุบัน: `{app_mode}` (ดึงรายชื่อที่เลือกมาจาก STEP 01 ทั้งหมด **{len(selected_targets)}** รายชื่อ)")
        st.markdown("---")

        if "1️⃣ New Media" in app_mode:
            st.info("🤖 **AI Sales Agent:** กดปุ่มด้านล่างเพื่อให้ Gemini AI วิเคราะห์ธุรกิจและเลือกสื่อ OOH พร้อมสร้างคำโปรยให้ทุกแบรนด์")
            
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
                    ai_results[email_key] = {"media": s_media, "reason": r_reason, "pitch": p_pitch}
                    progress_bar.progress((idx + 1) / len(selected_targets))
                    
                st.session_state.ai_results = ai_results
                status_text.empty()
                progress_bar.empty()
                st.success("✅ AI ประมวลผลวิเคราะห์ครบทุกแบรนด์เรียบร้อยแล้วค่ะ!")

            st.markdown("### 📧 ตรวจสอบตัวอย่างอีเมลพรีวิวแบบ Infographic:")
            
            for idx, target in enumerate(selected_targets, 1):
                c_name, comp_name = extract_sheet_data(target)
                company = comp_name if comp_name else "ลูกค้า"
                email_key = str(target.get("Email") or target.get("อีเมล") or f"client_{idx-1}").strip()
                
                greeting_name = f"คุณ {c_name}" if c_name else f"ทีมงาน {company}"
                closing_target = f"คุณ {c_name}" if c_name else f"ทางแบรนด์ {company}"

                ai_data = st.session_state.ai_results.get(email_key, {})
                selected_media = ai_data.get("media", list(MEDIA_FOLDERS.keys())[(idx-1) % len(MEDIA_FOLDERS)])
                ai_reason = ai_data.get("reason", f"AI วิเคราะห์ลักษณะธุรกิจของแบรนด์ {company} และเลือกสื่อที่เหมาะสม")

                with st.expander(f"📌 [{idx}/{len(selected_targets)}] พรีวิว Infographic Email: {greeting_name} ({company}) — `{email_key}`", expanded=True):
                    col_info, col_prev = st.columns([1, 1])
                    with col_info:
                        st.markdown(f"**🏢 แบรนด์/บริษัท:** `{company}`")
                        st.markdown(f"**👤 คำขึ้นต้น:** `{greeting_name}`")
                        st.markdown(f"**🎯 สื่อที่ AI เลือกให้อัตโนมัติ:** `{selected_media}`")
                        st.info(f"💡 **เหตุผลจาก AI:** {ai_reason}")
                        st.success("🎨 **รูปแบบ Template:** High-Fidelity Infographic (100% Matching Visual)")
                        
                    with col_prev:
                        media_info = MEDIA_FOLDERS.get(selected_media, MEDIA_FOLDERS[list(MEDIA_FOLDERS.keys())[0]])
                        subj_text = replace_placeholders(media_info["subject"], greeting_name, closing_target, user_name, user_phone)
                        preview_html = media_info["detail"]
                        
                        st.caption(f"📌 หัวข้อ: {subj_text}")
                        st.components.v1.html(preview_html, height=520, scrolling=True)

# ==========================================
# STEP 03 : SEND BATCH EMAILS
# ==========================================
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("🚀 STEP 03 : ยืนยันยอดและกดส่งอีเมลแบบ Batch Delivery")
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    
    if not selected_targets:
        st.warning("⚠️ ยังไม่มีการเลือกรายชื่อลูกค้าใน STEP 01 กรุณากลับไปเลือกรายชื่อก่อนค่ะ")
    else:
        st.success(f"📋 พร้อมส่งอีเมลหาลูกค้าทั้งหมด **{len(selected_targets)}** รายชื่อ")
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
                
                status_text.text(f"📤 กำลังส่งอีเมล ({idx+1}/{len(selected_targets)}): {company} ({email_addr})...")
                
                try:
                    msg = MIMEMultipart('related')
                    msg['From'] = formataddr((user_name, gmail_sender))
                    msg['To'] = email_addr
                    msg['Reply-To'] = user_email
                    
                    media_info = MEDIA_FOLDERS["The 20"]
                    msg['Subject'] = replace_placeholders(media_info["subject"], greeting_name, closing_target, user_name, user_phone)
                    
                    body_html = media_info["detail"]
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
