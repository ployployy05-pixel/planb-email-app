import streamlit as st
import pandas as pd
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr

# Set Page Config
st.set_page_config(page_title="Plan B Media - New Media Automail", page_icon="📢", layout="wide")

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PIMnucnqJmpCdnMLa13_7nuP9lOiEoXuFgVGlW5AGuw/edit?gid=1224436480#gid=1224436480"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ployployy05-pixel/planb-email-app/main/"

# Credentials & Secrets
GMAIL_USER = st.secrets.get("GMAIL_USER", "wichayada.ph@gmail.com")
GMAIL_APP_PASS = st.secrets.get("EMAIL_PASSWORD", "qnkhnriyjsjtyeug").replace(" ", "")

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
def fetch_image_bytes(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None

# ==========================================
# SIDEBAR (ฝั่งซ้ายมือ): SETTINGS & OPTIONS
# ==========================================
st.sidebar.title("⚙️ ข้อมูลผู้ส่ง (Plan B Media)")
user_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง ({{Sale name}})", value="วิชญาดา (พลอย)")
user_email = st.sidebar.text_input("อีเมลองค์กร (สำหรับลูกค้ารีพลาย)", value="wichayada.ph@planbmedia.co.th")
user_phone = st.sidebar.text_input("เบอร์โทรศัพท์ ({{Tel}})", value="064-542-4441")

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 BATCH EMAIL OPTIONS")

# 🎯 OPTION SELECTION (เลือกรูปแบบการส่งอีเมล 3 Mode)
app_mode = st.sidebar.radio(
    "เลือกรูปแบบเนื้อหาที่ต้องการส่ง:",
    [
        "1️⃣ New Media (เสนอขายแพ็กเกจสื่อเดิม)",
        "2️⃣ Credential (แนะนำตัวลูกค้าใหม่)",
        "3️⃣ Magnetic Report (รายงานสถิติ OOH ประจำเดือน)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Google Connection")
sheet_url_input = st.sidebar.text_input("Google Sheet URL (วางลิงก์ทีมอื่นได้)", value=DEFAULT_SHEET_URL)
st.sidebar.caption("📌 **Note สำหรับทีมอื่น:** เปิดสิทธิ์ Sheet เป็น Viewer และตั้งคอลัมน์: `ชื่อบริษัท`, `ชื่อผู้ติดต่อ`, `อีเมล`")

step = st.sidebar.radio("🔘 ขั้นตอนการทำงาน", [
    "STEP 01 : จัดการรายชื่อลูกค้า",
    "STEP 02 : เลือกเนื้อหา & พรีวิว",
    "STEP 03 : ยืนยันยอด & กดส่งอีเมล"
])

if 'recipients' not in st.session_state:
    st.session_state.recipients = []
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

FOOTER_BANNER_HTML = f"""
<br><br>
<div style="text-align: center; margin-top: 20px;">
    <img src="{GITHUB_RAW_BASE}footer_banner.jpg" style="max-width: 100%; height: auto; border-radius: 6px;" alt="Plan B Media Services">
</div>
"""

# ==========================================
# 1️⃣ MEDIA FOLDERS (NEW MEDIA PACKAGES)
# ==========================================
MEDIA_FOLDERS = {
    "rama 9 connected": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
ขอแนะนำ “RAMA 9 Connected” สื่อโฆษณาดิจิทัลใหม่ล่าสุดใจกลาง CBD พระราม 9 ที่พร้อมให้บริการตั้งแต่วันที่ 1 มีนาคม 2025<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}rama9_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Rama 9 Connected Location">
</div><br>
<b>จุดเด่นของสื่อ:</b><br>
✔ จอ Digital ขนาดใหญ่จำนวน 1 จอ – ตั้งอยู่ในทำเลศักยภาพ บริเวณแยกมารยาทดี จุดตัดระหว่างถนนจตุรทิศและเพชรอุทัย<br>
✔ ใจกลางศูนย์ธุรกิจพระราม 9 – รายล้อมด้วยแหล่งสำคัญ เช่น RCA, โรงพยาบาลพระราม 9, ห้าง Bravo และอาคารสำนักงาน<br>
✔ เข้าถึงกลุ่มเป้าหมายหลากหลาย – ผู้คนสัญจรตลอดทั้งวัน ทั้งกลุ่มคนทำงาน นักท่องเที่ยว และผู้พักอาศัยในพื้นที่<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}rama9_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Rama 9 Connected Showcase">
</div><br>
<b>ข้อเสนอสุดพิเศษ!</b><br>
📌 ราคาพิเศษ เฉพาะช่วงเปิดตัว สามารถยืนยันการจองได้ถึงวันที่ 31 พฤษภาคม 2025 และขึ้นสื่อได้ภายในวันที่ 31 ธันวาคม 2025 (เงื่อนไข: ไม่สามารถเลื่อนหรือยกเลิกหลังการยืนยัน)<br><br>
หากคุณ {{Client name}} สนใจสื่อนี้ หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""
    },
    "The Skyline": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ The Skyline สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ ที่โดดเด่นด้วยทำเลบนถนนทางเข้าสนามบินสุวรรณภูมิ<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}skyline_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The Skyline Location">
</div><br>
หากคุณ {{Client name}} สนใจสื่อ The Skyline หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ"""
    }
}

# ==========================================
# 2️⃣ CREDENTIAL OPTION TEMPLATE
# ==========================================
CREDENTIAL_LINK = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"
CREDENTIAL_SUBJECT = "[Plan B Media] ขออนุญาตนัดเข้าพบเพื่อนำเสนอสื่อโฆษณานอกบ้านสำหรับปี 2026"
CREDENTIAL_DETAIL = f"""เรียน คุณ {{Client name}}<br><br>
ขออนุญาตแนะนำตัว {{Sale name}} จาก บริษัท แพลนบี มีเดีย จำกัด (มหาชน) ค่ะ<br><br>
จึงขออนุญาตนัดเข้าพบเพื่อแนะนำตัว และ นำเสนอรายละเอียดของสื่อโฆษณานอกบ้านล่าสุดของทาง Plan B สำหรับปี 2026 ตามวันและเวลาที่ท่านสะดวก<br><br>
<b>ภาพรวมบริการสื่อโฆษณาของ Plan B Media:</b><br>
1. Digital: สื่อจอภาพเคลื่อนไหวกลางแจ้ง ทั้งกรุงเทพฯและต่างจังหวัด<br>
2. Classic: ป้ายภาพนิ่งบิลบอร์ดหลากหลายขนาด ทั้งในกรุงเทพฯและต่างจังหวัด<br>
3. Retail: สื่อโฆษณา ณ จุดขาย บริเวณศูนย์การค้าเครือสยามพิวรรธน์ เซ็นทรัลกรุ๊ป และ 7-Eleven<br>
4. Transit: สื่อระบบขนส่งมวลชน (รถประจำทางแบบปรับอากาศ / MRT / BTS)<br>
5. Airport: สื่อโฆษณาในสนามบินสุวรรณภูมิ สนามบินดอนเมือง และต่างจังหวัด<br>
6. International: สื่อโฆษณาต่างประเทศ (Laos, Malaysia, Singapore, USA)<br><br>
📌 <b>Plan B Media Profile / Credential:</b><br>
คุณสามารถเลือกเข้าชมภาพรวมสื่อทั้งหมดได้ที่ลิงก์นี้ค่ะ: <a href="{CREDENTIAL_LINK}" target="_blank">{CREDENTIAL_LINK}</a><br><br>
หากคุณ {{Client name}} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือตอบกลับอีเมลนี้ได้เลยค่ะ"""

# ==========================================
# 3️⃣ MAGNETIC REPORT OPTION SYSTEM
# ==========================================
MAGNETIC_FILES = {
    "Jul'26 Magnetic Report (สรุปตัวเลขสถิติประจำเดือน กรกฎาคม 2026)": "https://drive.google.com/drive/u/0/folders/1Mv3Wvpn1_IWOMRoT0tym8ONSWHMLEB9E",
    "Aug'26 Magnetic Report (อยู่ระหว่างเตรียมข้อมูล)": "https://drive.google.com/drive/u/0/folders/1Mv3Wvpn1_IWOMRoT0tym8ONSWHMLEB9E"
}

st.title("📢 PLAN B MEDIA • EMAIL AUTOMATION SYSTEM")

# ---------------------------------------------------------
# STEP 01 : จัดการรายชื่อลูกค้า
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# STEP 02 : เลือกเนื้อหา & พรีวิว (3 OPTIONS DYNAMIC)
# ---------------------------------------------------------
elif step == "STEP 02 : เลือกเนื้อหา & พรีวิว":
    st.subheader("🖼️ STEP 02 : เลือกเนื้อหา & พรีวิวอีเมล")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown(f"#### 🎯 โหมดปัจจุบัน: `{app_mode}`")
        
        # Mode 1: New Media
        if "1️⃣ New Media" in app_mode:
            selected_folder = st.selectbox("เลือกแพ็กเกจสื่อ New Media:", list(MEDIA_FOLDERS.keys()))
            current_subject = MEDIA_FOLDERS[selected_folder]["subject"]
            current_detail = MEDIA_FOLDERS[selected_folder]["detail"]
            
        # Mode 2: Credential
        elif "2️⃣ Credential" in app_mode:
            st.info("💡 โหมดนี้ใช้สำหรับส่งอีเมลแนะนำตัวบริษัท และเสนอเข้าพบลูกค้าใหม่")
            current_subject = CREDENTIAL_SUBJECT
            current_detail = CREDENTIAL_DETAIL
            
        # Mode 3: Magnetic Report
        elif "3️⃣ Magnetic Report" in app_mode:
            selected_magnetic = st.selectbox("เลือกรายงาน Magnetic PDF ในระบบ:", list(MAGNETIC_FILES.keys()))
            mag_link = MAGNETIC_FILES[selected_magnetic]
            
            current_subject = f"[Plan B Media] Monthly Magnetic Report Update"
            current_detail = f"""เรียน คุณ {{Client name}}<br><br>
ขออนุญาตนำส่ง Magnetic Report ({selected_magnetic}) รายละเอียดสถิติ OOH และ Eyeballs ประจำเดือนค่ะ<br><br>
📌 <b>ดาวน์โหลดไฟล์ PDF รายงาน Magnetic ได้ที่นี่:</b><br>
<a href="{mag_link}" target="_blank">{mag_link}</a><br><br>
ทาง Plan B หวังว่าข้อมูล Magnetic Report นี้จะเป็นประโยชน์สำหรับการวางแผนกิจกรรมทางการตลาดของคุณ {{Client name}} ค่ะ<br><br>
หากมีข้อสงสัยเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} ได้ตลอดเวลาค่ะ"""

    with col_right:
        st.markdown("#### 📧 ตัวอย่างอีเมลที่จะถูกจัดส่ง (Preview)")
        
        # พรีวิวแทนค่าตัวแปร
        sample_client = "ลูกค้าผู้มีเกียรติ"
        if st.session_state.recipients:
            sample_client = st.session_state.recipients[0].get("ชื่อผู้ติดต่อ", "ลูกค้าผู้มีเกียรติ")
            
        preview_subj = current_subject.replace("{{Client name}}", sample_client).replace("{{Sale name}}", user_name).replace("{{Tel}}", user_phone)
        preview_body = current_detail.replace("{{Client name}}", sample_client).replace("{{Sale name}}", user_name).replace("{{Tel}}", user_phone) + FOOTER_BANNER_HTML
        
        st.text_input("📌 Subject (หัวข้อ):", value=preview_subj)
        st.components.v1.html(preview_body, height=450, scrolling=True)

# ---------------------------------------------------------
# STEP 03 : ยืนยันยอด & กดส่งอีเมล
# ---------------------------------------------------------
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("🚀 STEP 03 : ยืนยันยอด & กดส่ง Batch Email")
    
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    st.info(f"📬 พร้อมส่งอีเมลหาลูกค้าทั้งหมด **{len(selected_targets)}** รายชื่อ ในโหมด `{app_mode}`")
    
    if st.button("✉️ ยืนยันส่ง Batch Email ทันที", type="primary", use_container_width=True):
        if not selected_targets:
            st.error("❌ ยังไม่ได้เลือกรายชื่อลูกค้าที่จะส่ง กรุณากลับไปที่ STEP 01 ค่ะ")
        else:
            st.success("🎉 ส่งอีเมลหาลูกค้าทุกท่านสำเร็จเรียบร้อยค่ะ!")
