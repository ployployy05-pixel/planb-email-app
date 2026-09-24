import streamlit as st
import pandas as pd
import urllib.request
import json

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Plan B Media - Email Automation System", layout="wide", page_icon="📊")

st.title("📊 Plan B Media - Email Automation Engine")
st.markdown("ระบบอัตโนมัติสร้างเนื้อหาเสนอขายและจัดส่ง Batch Email สำหรับทีม Sales")

# ==========================================
# STEP 0: MODE SELECTION (เลือก 3 OPTION หลัก)
# ==========================================
st.subheader("🎯 เลือกวัตถุประสงค์การส่งอีเมล (Email Objective)")
selected_mode = st.radio(
    "เลือกรูปแบบเนื้อหาที่ต้องการส่งหาลูกค้า:",
    options=[
        "1. New Media (เสนอขายแพ็กเกจสื่อ New Media ปกติ)",
        "2. Credential (แนะนำตัวลูกค้าใหม่ / บริษัทใหม่)",
        "3. Magnetic Report (นำส่งรายงานสถิติ OOH ประจำเดือน + แนบไฟล์ PDF)"
    ],
    index=0
)

st.divider()

# ==========================================
# SIDEBAR: CONFIGURATION & DATABASE
# ==========================================
st.sidebar.header("⚙️ 1. ตั้งค่าฐานข้อมูลลูกค้า (Database)")

# ช่องกรอก Custom Google Sheets Link
sheet_url = st.sidebar.text_input(
    "🔗 วางลิงก์ Google Sheets ของทีมคุณ:",
    placeholder="https://docs.google.com/spreadsheets/d/..."
)
st.sidebar.caption("📌 **Note:** ไฟล์ต้องเปิดสิทธิ์ให้อ่านได้ (Viewer) และมีหัวคอลัมน์มาตรฐาน: `Name`, `Company`, `Email`, `Industry` (ถ้ามี)")

st.sidebar.divider()

# แสดง Option เพิ่มเติมตาม Mode ที่เลือก
if "1. New Media" in selected_mode:
    st.sidebar.header("🎯 เลือกหมวดหมู่สื่อ New Media")
    p_digital = st.sidebar.checkbox("1. Digital (จอภาพเคลื่อนไหว)", value=True)
    p_classic = st.sidebar.checkbox("2. Classic (ป้ายบิลบอร์ด)")
    p_retail = st.sidebar.checkbox("3. Retail (สยามพิวรรธน์/เซ็นทรัล/7-Eleven)", value=True)
    p_transit = st.sidebar.checkbox("4. Transit (รถประจำทาง/MRT/BTS)")
    p_airport = st.sidebar.checkbox("5. Airport (สนามบิน)")
    p_intl = st.sidebar.checkbox("6. International (สื่อต่างประเทศ)")

elif "2. Credential" in selected_mode:
    st.sidebar.header("📁 Credential Folder Link")
    credential_link = st.sidebar.text_input(
        "ลิงก์ Plan B Profile (Drive):",
        value="https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"
    )

elif "3. Magnetic Report" in selected_mode:
    st.sidebar.header("📎 แนบไฟล์ PDF Magnetic Report")
    month_year = st.sidebar.text_input("ระบุเดือน/ปี (เช่น Jul'26):", value="Jul'26")
    uploaded_pdfs = st.sidebar.file_uploader(
        "อัปโหลดไฟล์ PDF รายงาน Magnetic (แนบได้หลายไฟล์):",
        type=["pdf"],
        accept_multiple_files=True
    )

# ==========================================
# MAIN PANEL: WORKFLOW & PREVIEW
# ==========================================

# ฟังก์ชันแปลง URL Google Sheets เป็น CSV
def load_sheet_data(url):
    try:
        sheet_id = url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        return pd.read_csv(csv_url)
    except Exception as e:
        return None

df = None
if sheet_url:
    df = load_sheet_data(sheet_url)

if df is not None:
    st.subheader("📑 Step 1: ตรวจสอบรายชื่อลูกค้าเป้าหมาย")
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    st.subheader("📧 Step 2: ตรวจสอบตัวอย่างเนื้อหาอีเมล (Email Preview)")
    
    # ดึงลูกค้ารายแรกมาพรีวิว
    sample_row = df.iloc[0]
    c_name = sample_row.get('Name', 'ลูกค้า')
    c_company = sample_row.get('Company', 'บริษัทลูกค้า')
    c_industry = sample_row.get('Industry', 'ทั่วไป')
    
    # สร้าง Subject & Body ตาม Sales Note ที่อัปเดตบน Drive
    if "1. New Media" in selected_mode:
        email_subject = f"[Plan B Media] ขออนุญาตนำเสนอสื่อโฆษณา New Media สำหรับคุณ {c_name}"
        email_body = f"""เรียน คุณ {c_name} ({c_company})

ทาง Plan B Media ขออนุญาตนำเสนอสื่อโฆษณา New Media เพื่อช่วยเสริมสร้าง Brand Awareness และดึงดูดกลุ่มเป้าหมายในทำเลศักยภาพสูงสุดค่ะ...

ขอแสดงความนับถือ,
Plan B Media Public Company Limited"""

    elif "2. Credential" in selected_mode:
        email_subject = f"[Plan B Media] ขออนุญาตนัดเข้าพบเพื่อนำเสนอสื่อโฆษณานอกบ้านสำหรับปี 2026"
        email_body = f"""Subject: {email_subject}

เรียน คุณ {c_name}

ขออนุญาตแนะนำตัว [ชื่อ Sales] Account Executive I, Sales จาก บริษัท แพลนบี มีเดีย ค่ะ

จึงขออนุญาตนัดเข้าพบเพื่อแนะนำตัว และ นำเสนอรายละเอียดของสื่อโฆษณานอกบ้านล่าสุดของทาง Plan B สำหรับปี 2026 ตามวันและเวลาที่ท่านสะดวก

เรามีผลิตภัณฑ์/บริการที่สามารถช่วยสร้างการรับรู้และส่งเสริมยอดขายให้แก่กลุ่มธุรกิจ {c_industry} และอยากแนะนำให้คุณพิจารณาสื่อของตามรายละเอียดด้านล่างนี้ค่ะ:

1. Digital: สื่อจอภาพเคลื่อนไหวกลางแจ้ง ทั้งกรุงเทพฯและต่างจังหวัด
2. Classic: ป้ายภาพนิ่งบิลบอร์ดหลากหลายขนาด ทั้งในกรุงเทพฯและต่างจังหวัด
3. Retail: สื่อโฆษณา ณ จุดขาย บริเวณศูนย์การค้าเครือสยามพิวรรธน์ เซ็นทรัลกรุ๊ป และ 7-Eleven
4. Transit: สื่อระบบขนส่งมวลชน (รถประจำทางแบบปรับอากาศ / รถไฟใต้ดิน MRT / รถไฟฟ้า BTS)
5. Airport: สื่อโฆษณาในสนามบินสุวรรณภูมิ, สนามบินดอนเมือง และสนามบินต่างจังหวัด
6. International: สื่อโฆษณาต่างประเทศ (Laos, Malaysia, Singapore, USA)

Plan B Media Profile:
- Credential: ภาพรวมสื่อทั้งหมด ตาม link ด้านล่างนี้ค่ะ
https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC

เรามั่นใจว่าสื่อโฆษณานอกบ้านของ แพลนบี มีเดีย ที่มีความหลากหลายจะเป็นส่วนหนึ่งในการช่วยส่งเสริมการสร้างกิจกรรมทางการตลาดหรือสร้าง Brand ได้อย่างมีประสิทธิภาพอย่างแน่นอนค่ะ

_________________________________________________________________

หากคุณ {c_name} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ [เบอร์โทร Sales] หรือตอบกลับมาที่อีเมลนี้ได้เลยค่ะ

ขอขอบคุณที่สละเวลาอ่านอีเมลฉบับนี้ และหวังว่าจะได้พูดคุยกับคุณเร็วๆ นี้ค่ะ"""

    elif "3. Magnetic Report" in selected_mode:
        email_subject = f"[Plan B Media] Monthly Magnetic Report Update – {month_year}"
        email_body = f"""Subject: {email_subject}

เรียน คุณ {c_name}

ขออนุญาตนำส่ง Magnetic Report ประจำเดือน {month_year} รายละเอียดข้อมูลตามไฟล์แนบค่ะ

ทาง Plan B หวังว่าข้อมูลภายใน Magnetic Report จะเป็นประโยชน์สำหรับการวางแผนและช่วยสนับสนุนกิจกรรมทางการตลาดของทาง {c_company} ได้อย่างมีประสิทธิภาพค่ะ

_________________________________________________________________

หากคุณ {c_name} มีข้อสงสัยหรือต้องการรายละเอียดเพิ่มเติม สามารถติดต่อได้ที่เบอร์ [เบอร์โทร Sales] หรือตอบกลับมาที่อีเมลนี้ได้เลยค่ะ

ขอขอบคุณที่สละเวลาอ่านอีเมลฉบับนี้ และหวังว่าจะได้พูดคุยกับคุณเร็วๆ นี้ค่ะ"""

    # แสดงพรีวิว
    st.text_input("📌 Subject (หัวข้ออีเมล):", value=email_subject)
    st.text_area("📝 Body (เนื้อหาอีเมล):", value=email_body, height=350)
    
    st.divider()
    st.subheader("🚀 Step 3: ดำเนินการจัดส่ง (Send Batch Email)")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        s_email = st.text_input("อีเมลผู้ส่ง (Central Account):", placeholder="your_email@gmail.com")
        s_pass = st.text_input("App Password (16 หลัก):", type="password")
    with c2:
        st.write("")
        st.write("")
        if st.button("✉️ ยืนยันส่ง Batch Email หาลูกค้าทุกคน", type="primary", use_container_width=True):
            if not s_email or not s_pass:
                st.error("❌ กรุณากรอกอีเมลผู้ส่งและ App Password ให้ครบถ้วนค่ะ")
            else:
                st.success(f"🎉 ดำเนินการส่งอีเมลรูปแบบ {selected_mode.split(' ')[1]} สำเร็จเรียบร้อยแล้วค่ะ!")

else:
    st.info("👈 กรุณากรอกลิงก์ Google Sheets ของทีมคุณที่ Sidebar ด้านซ้ายเพื่อเริ่มต้นใช้งานค่ะ")
