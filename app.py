import streamlit as st
import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

st.set_page_config(page_title="Plan B Media - New Media Automail", page_icon="📢", layout="wide")

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PIMnucnqJmpCdnMLa13_7nuP9lOiEoXuFgVGlW5AGuw/edit?gid=1224436480#gid=1224436480"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/wichayadaph-hash/planb-email-app/main/"

# ดึง Secrets
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

# Sidebar
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
sheet_url_input = st.sidebar.text_input("Google Sheet URL (รายชื่อลูกค้า)", value=DEFAULT_SHEET_URL)

step = st.sidebar.radio("🔘 ขั้นตอนการทำงาน", [
    "STEP 01 : จัดการรายชื่อลูกค้า",
    "STEP 02 : เลือก New Media & พรีวิว",
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

หากคุณ {{Client name}} สนใจสื่อนี้ หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "banner_color": "#1b4332"
    },
    "The Skyline": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ The Skyline สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ ที่โดดเด่นด้วยทำเลบนถนนทางเข้าสนามบินสุวรรณภูมิ โดยมีให้เลือกถึง 2 ตำแหน่ง คือ :<br>
• <b>The Skyline A</b> : ตั้งอยู่ทางฝั่งซ้ายของเส้นทาง เหมาะสำหรับการสร้างความประทับใจแรกพบ<br>
• <b>The Skyline B</b> : ครอบคลุมเส้นทางจราจร มั่นใจได้ว่าผู้โดยสารทุกคนจะต้องมองเห็น<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}skyline_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The Skyline Location">
</div><br>

The Skyline เป็นสื่อที่ตอบโจทย์การเข้าถึงกลุ่มลูกค้าระดับพรีเมียม ไม่ว่าจะเป็นกลุ่มนักท่องเที่ยวทั้งชาวไทยและต่างชาติ กลุ่มนักธุรกิจ และกลุ่มผู้โดยสารในสนามบิน กว่า 85% เป็นกลุ่มที่มีศักยภาพในการจับจ่ายใช้สอย นอกจากนี้ ยังช่วยเพิ่มโอกาสในการเข้าถึงกลุ่มผู้ชมจำนวนมาก เนื่องจากคาดว่าจะมีผู้โดยสารสูงถึง 65 ล้านคนในปี 2025<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}skyline_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Passenger Traffic">
</div><br>

_________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ The Skyline หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "banner_color": "#003366"
    },
    "The 20": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "detail": f"""เรียน คุณ {{Client name}},<br><br>
สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ The 20 สื่อดิจิทัลใหม่ล่าสุด จาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยสื่อนี้ได้พลิกโฉม ป้ายโฆษณา Serie Poles เดิม ให้กลายเป็น จอ LED กว่า 74 จอ ที่เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD ที่สามารถมองเห็นได้ทั้งขาเข้าและขาออกมุ่งหน้าสู่ ถนนวิภาวดี และ ถนนพระราม 4<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}the20_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The 20 Coverage">
</div><br>

พร้อมคุณภาพจอที่คมชัดขึ้นกว่าเดิมถึง 2 เท่า มองเห็นชัดเจนจากระยะไกล สะกดทุกสายตา พร้อมช่วยยกระดับการสื่อสารของแบรนด์ ด้วย Storytelling ที่ทรงพลัง ให้ลูกค้าสามารถดีไซน์โฆษณาได้หลากหลายรูปแบบ เพิ่มลูกเล่นได้ไม่จำกัด ตลอด 74 จอ สร้างความ impact และจดจำ พร้อมตอบโจทย์ได้ทุกแคมเปญ<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}the20_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The 20 Storytelling">
</div><br>

นอกจากนี้ เรามีทีม Sunbeam (Creative Agency) ที่พร้อมให้บริการอย่างครบวงจร ตั้งแต่ช่วยพัฒนาแคมเปญและดีไซน์ให้โดดเด่น พร้อมตอบโจทย์การสื่อสารได้อย่างเหมาะสมและมีประสิทธิภาพสูงสุดกับสื่อ The 20<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}the20_3.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="The 20 Ad Sets">
</div><br>

______________________________________________________________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ The 20 หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "banner_color": "#155724"
    },
    "Nextopia Siam Paragon": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: “NEXTOPIA” สื่อใหม่ล่าสุด สร้างประสบการณ์ให้แบรนด์ 360° พร้อมยกระดับภาพลักษณ์",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
{{Sale name}} ขอแนะนำ NEXTOPIA สื่อโฆษณาดิจิทัลสุดล้ำแห่งใหม่ ใจกลางศูนย์การค้า Siam Paragon ตั้งอยู่ในโซนใหม่ “NEXTOPIA” ซึ่งเป็นพื้นที่ที่รวมแบรนด์สินค้ารักษ์โลก และนวัตกรรมที่ตอบโจทย์ไลฟ์สไตล์แบบ Sustainable ของผู้บริโภครุ่นใหม่ที่ใส่ใจสิ่งแวดล้อม<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}nextopia_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Nextopia Sphere">
</div><br>

จุดเด่นของสื่อนี้คือ จอ LED ทรงกลมขนาดยักษ์ ใจกลางโซน อยู่ระหว่างชั้น 4 และ 5 นับเป็นจุด Iconic ใหม่ ดึงดูดสายตา<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}nextopia_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Nextopia 3D Content">
</div><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}nextopia_3.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Nextopia Showcase">
</div><br>

นอกจากนี้ NEXTOPIA แบ่งเวลา 30 นาทีต่อชั่วโมง ให้กับคอนเทนต์ให้ความรู้เกี่ยวกับสิ่งแวดล้อม เช่น การลดมลพิษ ภาวะโลกร้อน และพลังงานสะอาด พร้อมยกระดับภาพลักษณ์ของแบรนด์ได้อย่างดี<br><br>

_______________________________________________<br>
หากคุณ {{Client name}} สนใจสื่อ NEXTOPIA หรือบริการของเราเพิ่มเติมสามารถติดต่อได้ที่เบอร์ {{Tel}} หรือเพียงตอบกลับอีเมลนี้ได้เลยค่ะ<br>
ขอบคุณค่ะ {{Sale name}}""",
        "banner_color": "#4a154b"
    },
    "Central Network": {
        "subject": "[Plan B Media] OUTDOOR TRENDS: กระตุ้นการตัดสินใจซื้อ ด้วยสื่อ ณ จุดขายในห้าง Central ทั่วประเทศ",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ Central Network สื่อจอดิจิทัลภายในห้างสรรพสินค้าเซ็นทรัลทั่วประเทศ ที่มีเครือข่ายทั้งหมด 283 จอ ครอบคลุม 14 สาขาทั้งในกทม. และต่างจังหวัด เข้าถึงกลุ่มลูกค้าที่หลากหลายวัยและไลฟ์สไตล์<br><br>

------------------------------------------------------------------------<br>
จากข้อมูล Insight เกี่ยวกับพฤติกรรมผู้บริโภค พบว่า:<br>
• ผู้บริโภคใช้เวลาในการช้อปปิ้งในห้างเฉลี่ยคนละ 1-3 ชั่วโมงต่อครั้ง<br>
• ช้อปปิ้งในห้างบ่อย สูงถึง 6-7 ครั้งต่อสัปดาห์<br>
• โดยเฉพาะสินค้า Luxury ที่ผู้บริโภคนิยมดูและซื้อสินค้าผ่านทางหน้าร้าน มากกว่าออนไลน์<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_net_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Network Branches">
</div><br>

ตั้งอยู่ในพื้นที่ที่มีการสัญจรหนาแน่นภายในห้างสรรพสินค้า ช่วยเพิ่มการมองเห็นและเสริมการจดจำแบรนด์ได้อย่างดี<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_net_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Network Positions">
</div><br>

นับเป็นโอกาสที่แบรนด์จะสามารถเข้าถึงผู้บริโภคในช่วงเวลาที่พร้อมตัดสินใจซื้อ ยิ่งเป็นการกระตุ้นให้ผู้บริโภคตัดสินใจซื้อได้ง่ายขึ้น<br><br>

------------------------------------------------------------------------<br>
หากคุณ {{Client name}} สนใจสื่อ Central Network หรือบริการของเราเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {{Tel}} หรือ ตอบกลับมาที่อีเมลนี้ได้เลยค่ะ""",
        "banner_color": "#856404"
    },
    "Central Network [New Package]": {
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
สวัสดีค่ะ ทางเราขอแนะนำแพ็กเกจ Central Network ที่อัปเกรดครั้งใหญ่ โดยเปิดตัว CentralWorld 360 – สื่อดิจิทัลใหม่ล่าสุดในรูปแบบ จอ LED ทรงโค้งแบบ Tower Wraparound ที่ติดตั้งรอบลิฟต์แก้วบริเวณใจกลางศูนย์การค้า CentralWorld<br><br>

ด้วยขนาด 8.78 x 21 เมตร (รวมพื้นที่ 184.38 ตร.ม.) จอนี้รองรับ 3D Content ได้อย่างดี ด้วยคุณภาพความคมชัดสูง และมุมมองกว้าง มองเห็นได้ชัดเจนจากหลากหลายทิศทาง พื้นที่ดังกล่าวยังเป็นจุดที่ใช้จัดกิจกรรมและอีเวนต์เป็นประจำ ทำให้จอนี้กลายเป็น จุด touchpoint สำคัญ ที่ช่วยเพิ่มการรับรู้และความน่าสนใจให้กับแบรนด์<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_w360_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="CentralWorld 360 Miss Dior">
</div><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_w360_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="CentralWorld 360 NARS">
</div><br>

นอกจากนี้ ยังมี จอ VDO Wall ขนาดใหญ่ 2 จอ บริเวณทางขึ้นลิฟต์แก้ว พร้อมเป็นจุดที่ผู้คนหยุดรอและมีเวลาในการรับชมสื่อ (dwell time) สูง ช่วยเสริมมุมมองด้านหน้าให้สมบูรณ์ยิ่งขึ้น<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_w360_3.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="CentralWorld VDO Wall">
</div><br>

เรามีแพ็กเกจให้เลือกทั้งหมด 3 รูปแบบ ดังนี้:<br>
1. <b>CentralWorld 360</b>: สื่อดิจิทัลแบบ Iconic ที่ CentralWorld<br>
2. <b>Central Network</b>: สื่อเครือข่ายทั่วประเทศ<br>
3. <b>Central Network Plus</b>: แพ็กเกจจัดเต็ม ครบทุกจอ<br><br>

หากท่านสนใจข้อมูลเพิ่มเติม สามารถติดต่อกลับได้ทางอีเมลนี้ หรือเบอร์ {{Tel}} ได้ตลอดเวลาค่ะ""",
        "banner_color": "#383d41"
    },
    "Central Park": {
        "subject": "[Plan B Media] เปิดตัวจอ Signature ใหม่ล่าสุด! Central Park – สื่อดิจิทัลพรีเมียมใจกลางกรุงเทพฯ",
        "detail": f"""เรียน คุณ {{Client name}}<br><br>
สวัสดีค่ะ ทางเรามีความยินดีนำเสนอ "Central Park" จอดิจิทัลใหม่ล่าสุด บนโครงการมิกซ์ยูสระดับโลก Dusit Central Park บริเวณหัวมุมถนนสีลม – พระราม 4 เชื่อมต่อกับทั้ง BTS ศาลาแดง และ MRT สีลม<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_park_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Dusit Central Park Overview">
</div><br>

<b>จุดเด่นของสื่อ Central Park:</b><br>
• จอ LED Digital Curved ขนาดใหญ่กว่า 518 sq.m. บน facade ห้าง Central Park<br>
• จอถูกออกแบบเพื่อรองรับงาน Creative Content โดยเฉพาะ 3D Visual<br>
• เข้าถึงผู้คนมากกว่า 8 ล้าน eyeballs/เดือน และ Reach กว่า 2.6 ล้านคน/เดือน<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_park_2.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Park Tissot Screen">
</div><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_park_3.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Park Entrance Screen">
</div><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}central_park_4.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="Central Park Hourglass Screen">
</div><br>

______________________________________________________________________________________________<br>
หากท่านสนใจข้อมูลเพิ่มเติม สามารถติดต่อกลับได้ทางอีเมลนี้ หรือติดต่อที่เบอร์ {{Tel}} ได้ตลอดเวลาค่ะ""",
        "banner_color": "#d97706"
    },
    "PlanB TV Nationwide [New Pack]": {
        "subject": "[Plan B Media] ปรับแพ็กเกจ Plan B TV Nationwide ใหม่ ให้เข้าถึงกลุ่มเป้าหมายมากขึ้น คุ้มค่ายิ่งกว่าเดิม",
        "detail": f"""เรียน คุณ {{Client name}},<br><br>
สวัสดีค่ะ คุณ {{Client name}} ทางเราขอแจ้งให้ทราบเกี่ยวกับการปรับแพ็กเกจ Plan B TV Nationwide ใหม่<br><br>

<div style="text-align: center; margin: 15px 0;">
    <img src="{GITHUB_RAW_BASE}pbtv_nationwide_1.jpg" style="max-width: 100%; height: auto; border-radius: 8px;" alt="PlanB TV Nationwide">
</div><br>

<b>แพ็กเกจใหม่ของ PBTV Nationwide แบ่งเป็น:</b><br>
• Pack Full จำนวน 120 จอ<br>
• Pack Red / Blue จำนวน อย่างละ 57 จอ<br><br>

สำหรับแพ็กเกจ Plan B TV Nationwide ใหม่นี้ จะช่วยให้แบรนด์เข้าถึงผู้คนทั่วประเทศได้มากขึ้น ด้วย 120 จอที่ครอบคลุม 51 จังหวัดทั่วทุกภาค และเข้าถึงผู้ชมกว่า 138 ล้านคน พร้อมทั้งมอบความคุ้มค่ายิ่งขึ้นด้วย CPME ที่ลดลง<br><br>

หากลูกค้าสะดวก ทางเรายินดีอธิบายรายละเอียดเพิ่มเติมเกี่ยวกับแพ็กเกจนี้ เพื่อช่วยให้คุณเลือกใช้สื่อได้อย่างคุ้มค่าที่สุดค่ะ<br>
ขอบคุณค่ะ""",
        "banner_color": "#004085"
    }
}

if 'selected_media_folder' not in st.session_state:
    st.session_state.selected_media_folder = list(MEDIA_FOLDERS.keys())[0]

st.title("📢 PLAN B MEDIA • NEW MEDIA AUTOMATION SYSTEM")

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
        # ปุ่มควบคุม เลือกส่งทั้งหมด / ไม่เลือกทั้งหมด
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
        
        # จัดคอลัมน์ให้อยู่หน้าสุด
        if 'ส่งอีเมล?' not in df_rec.columns:
            df_rec.insert(0, 'ส่งอีเมล?', True)
            
        priority = ['ส่งอีเมล?', 'ที่มา']
        others = [c for c in df_rec.columns if c not in priority]
        df_rec = df_rec[priority + others]
        
        # ตาราง st.data_editor
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
# STEP 02 : เลือก New Media & พรีวิว
# ---------------------------------------------------------
elif step == "STEP 02 : เลือก New Media & พรีวิว":
    st.subheader("🖼️ STEP 02 : เลือกสื่อ New Media & พรีวิวเนื้อหาอีเมล")
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("#### 1️⃣ เลือกสื่อ New Media ที่ต้องการเสนอขาย")
        selected_folder = st.selectbox(
            "เลือกรายการสื่อ New Media:",
            options=list(MEDIA_FOLDERS.keys()),
            index=0
        )
        st.session_state.selected_media_folder = selected_folder
        folder_info = MEDIA_FOLDERS[selected_folder]
        
        sample_client = "ลูกค้าผู้มีเกียรติ (ตัวอย่าง)"
        if st.session_state.recipients:
            for r in st.session_state.recipients:
                if r.get('ส่งอีเมล?') and r.get('ชื่อผู้ติดต่อ'):
                    sample_client = r.get('ชื่อผู้ติดต่อ')
                    break
                    
        st.markdown("---")
        st.markdown("##### ✏️ แก้ไขข้อความเนื้อหาอีเมล (ถ้าต้องการ)")
        custom_subject = st.text_input("หัวข้ออีเมล (Subject)", value=folder_info["subject"])
        custom_detail = st.text_area("เนื้อหาในอีเมล (HTML)", value=folder_info["detail"], height=380)
        
        MEDIA_FOLDERS[selected_folder]["subject"] = custom_subject
        MEDIA_FOLDERS[selected_folder]["detail"] = custom_detail

    with col_right:
        st.markdown("#### 2️⃣ ตัวอย่างหน้าตาอีเมลที่จะส่งหาลูกค้า (Preview)")
        
        curr = MEDIA_FOLDERS[st.session_state.selected_media_folder]
        body_text = curr['detail'].replace("{{Client name}}", f"<b>{sample_client}</b>").replace("{{Sale name}}", f"<b>{user_name}</b>").replace("{{Tel}}", f"<b>{user_phone}</b>")
        
        preview_html = f"""<div style="border: 1px solid #cccccc; padding: 25px; border-radius: 8px; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); font-family: 'Aptos', 'Calibri', 'Sarabun', sans-serif; font-size: 16px; line-height: 1.6; color: #333;"><div style="background-color: {curr['banner_color']}; color: white; padding: 12px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 20px;">📢 PLAN B MEDIA • NEW MEDIA UPDATE ({selected_folder})</div><p style="font-size: 1.1rem; color: #003366; font-weight: bold;">Subject: {curr['subject']}</p><hr style="border: 0.5px solid #eee;"><div>{body_text}</div><hr style="border: 0.5px solid #eee;"><p style="font-size: 0.95rem; color: #555; margin-bottom: 0;"><b>ขอแสดงความนับถือ,</b><br><span style="color: #003366; font-weight: bold;">{user_name}</span><br>อีเมล: {user_email} | เบอร์โทรศัพท์: {user_phone}<br><b>Plan B Media Public Company Limited</b></p>{FOOTER_BANNER_HTML}</div>"""

        st.markdown(preview_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# STEP 03 : ยืนยันยอด & กดส่งอีเมล
# ---------------------------------------------------------
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader("✉️ STEP 03 : ตรวจสอบความถูกต้อง & ยืนยันการส่งอีเมล")
    
    selected_recipients = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    curr_folder = MEDIA_FOLDERS[st.session_state.selected_media_folder]
    
    col_sum1, col_sum2 = st.columns([1, 1])
    
    with col_sum1:
        st.markdown("#### 📊 สรุปรายการที่จะส่ง")
        st.write(f"• **จำนวนผู้รับทั้งหมด:** {len(selected_recipients)} รายชื่อ")
        st.write(f"• **สื่อ New Media ที่เลือก:** {st.session_state.selected_media_folder}")
        st.write(f"• **หัวข้ออีเมล:** {curr_folder['subject']}")
        st.write(f"• **ผู้ส่ง:** {user_name} ({user_email})")
        
    with col_sum2:
        st.markdown("#### 👥 รายชื่อผู้รับที่จะได้รับอีเมล")
        if selected_recipients:
            st.dataframe(pd.DataFrame(selected_recipients)[['ที่มา', 'ชื่อบริษัท', 'ชื่อผู้ติดต่อ', 'อีเมล']], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ ยังไม่ได้เลือกรายชื่อผู้รับเลยค่ะ กรุณากลับไปที่ STEP 01 แล้วติ๊กเลือกรายชื่อก่อนนะคะ")
            
    st.markdown("---")
    
    if selected_recipients:
        if st.button("🚀 ยืนยันและกดส่งอีเมลหาลูกค้าทันที (Batch Email)", type="primary", use_container_width=True):
            if not sender_password:
                st.error("❌ กรุณากรอก Google App Password ก่อนนะคะ")
            else:
                success_count = 0
                fail_count = 0
                
                with st.spinner("กำลังส่งอีเมลหาลูกค้า..."):
                    for recipient in selected_recipients:
                        rec_email = recipient.get('อีเมล')
                        rec_name = recipient.get('ชื่อผู้ติดต่อ', 'ลูกค้าผู้มีเกียรติ')
                        
                        if rec_email:
                            body_html = curr_folder['detail'].replace("{{Client name}}", rec_name).replace("{{Sale name}}", user_name).replace("{{Tel}}", user_phone)
                            
                            full_email_html = f"""<div style="font-family: 'Aptos', 'Calibri', 'Sarabun', sans-serif; font-size: 16px; line-height: 1.6; color: #333;"><div>{body_html}</div><hr><p><b>ขอแสดงความนับถือ,</b><br>{user_name}<br>Plan B Media Public Company Limited<br>อีเมล: {user_email} | โทร: {user_phone}</p>{FOOTER_BANNER_HTML}</div>"""
                            try:
                                msg = MIMEMultipart("alternative")
                                msg["Subject"] = curr_folder['subject']
                                msg["From"] = formataddr((user_name, gmail_sender))
                                msg["To"] = rec_email
                                msg["Reply-To"] = user_email

                                part = MIMEText(full_email_html, "html")
                                msg.attach(part)

                                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                                    server.login(gmail_sender, sender_password)
                                    server.sendmail(gmail_sender, rec_email, msg.as_string())
                                    
                                success_count += 1
                            except Exception as e:
                                fail_count += 1
                                st.error(f"ไม่สามารถส่งหา {rec_email} ได้: {e}")
                
                if success_count > 0:
                    st.balloons()
                    st.success(f"🎉 ส่งอีเมลสำเร็จเรียบร้อยแล้วจำนวน {success_count} รายชื่อ!")
