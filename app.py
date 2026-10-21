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

# ==========================================
# MEDIA TEMPLATES DATA (NEW MEDIA MODE - PREMIUM CARD DESIGN)
# ==========================================
MEDIA_FOLDERS = {
    "The 20": {
        "title": "The 20",
        "description": "สื่อดิจิทัล DOOH ยาวที่สุดในโลก 2.5 กม. บนทางด่วน CBD เหมาะกับ Tech, ยานยนต์, แบรนด์ใหญ่ระดับองค์กร, สถาบันการเงิน, พลังงาน ที่ต้องการ Impact สูง",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "drive_link": "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC",
        "body_intro": """สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ <b>The 20</b> สื่อดิจิทัลใหม่ล่าสุด จาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยสื่อนี้ได้พลิกโฉม ป้ายโฆษณา Serie Poles เดิม ให้กลายเป็น จอ LED กว่า 74 จอ ที่เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD""",
        "images": ["the20_1.jpg", "the20_2.jpg", "the20_3.jpg"]
    },
    "Central Network [New Package]": {
        "title": "Central Network [New Package]",
        "description": "สื่อในห้างสรรพสินค้า CentralWorld ทั่วประเทศ เหมาะกับ แฟชั่น, เครื่องสำอาง, รองเท้า, สนีกเกอร์, อาหาร, ร้านค้า Retail, FMCG, คอสเมติก, สปา, สกินแคร์, เล็บ, ความงาม",
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "drive_link": "https://drive.google.com/drive/folders/1jKRJBAlKcpauiUaNxTC0CuzK67_D6uOU",
        "body_intro": """สวัสดีค่ะ ทางเราขอแนะนำแพ็กเกจ <b>Central Network</b> ที่อัปเกรดครั้งใหญ่ โดยเปิดตัว CentralWorld 360 – สื่อดิจิทัลใหม่ล่าสุดในรูปแบบ จอ LED ทรงโค้งแบบ Tower Wraparound บริเวณลิฟต์แก้ว CentralWorld""",
        "images": ["central_w360_1.jpg", "central_w360_2.jpg", "central_w360_3.jpg"]
    },
    "The Skyline": {
        "title": "The Skyline",
        "description": "ป้ายภาพนิ่งขนาดใหญ่ทางเข้าสนามบินสุวรรณภูมิ เหมาะกับ สินค้าพรีเมียม, ท่องเที่ยว, โรงแรม, สายการบิน, อสังหาริมทรัพย์, ลักชัวรี, แบรนด์เนม, สินค้านำเข้า",
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "drive_link": "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC",
        "body_intro": """สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ <b>The Skyline</b> สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ บนถนนทางเข้าสนามบินสุวรรณภูมิ""",
        "images": ["skyline_1.jpg", "skyline_2.jpg", "skyline_1.jpg"]
    },
    "rama 9 connected": {
        "title": "rama 9 connected",
        "description": "สื่อดิจิทัลใจกลาง CBD พระราม 9 ย่านธุรกิจ RCA เหมาะกับ ออฟฟิศ B2B, คลินิก, โรงพยาบาล, สถาบันการศึกษา, โรงเรียน, มหาวิทยาลัย",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "drive_link": "https://drive.google.com/drive/folders/1E8SfEFV2k7kmFBbiaj0atsQJrgwIB7Ij",
        "body_intro": """ขอแนะนำ <b>“RAMA 9 Connected”</b> สื่อโฆษณาดิจิทัลใหม่ล่าสุดใจกลาง CBD พระราม 9 ที่พร้อมให้บริการตั้งแต่วันที่ 1 มีนาคม 2025<br><br>
<b>จุดเด่นของสื่อ:</b><br>
✔ จอ Digital ขนาดใหญ่จำนวน 1 จอ – ตั้งอยู่ในทำเลศักยภาพ บริเวณแยกมารยาทดี จุดตัดระหว่างถนนจตุรทิศและเพชรอุทัย<br>
✔ ใจกลางศูนย์ธุรกิจพระราม 9 – รายล้อมด้วยแหล่งสำคัญ เช่น RCA, โรงพยาบาลพระราม 9, ห้าง Bravo และอาคารสำนักงาน""",
        "images": ["rama9_1.jpg", "rama9_2.jpg", "rama9_1.jpg"]
    }
}

# 🧼 HELPER FUNCTION: สกัดข้อมูลรายชื่อ
def extract_sheet_data(record):
    c_name, comp_name = "", ""
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

# 🧹 HELPER FUNCTION: แทนที่ตัวแปรในข้อความ
def replace_placeholders(text, greeting_name, closing_target, sale_name, phone_num, pitch_text="", sale_email=""):
    result = str(text)
    result = result.replace("{{Greeting Name}}", greeting_name).replace("{Greeting Name}", greeting_name)
    result = result.replace("{{Closing Target}}", closing_target).replace("{Closing Target}", closing_target)
    result = result.replace("{{Sale name}}", sale_name).replace("{Sale name}", sale_name)
    result = result.replace("{{Tel}}", phone_num).replace("{Tel}", phone_num)
    if sale_email:
        result = result.replace("{{Sale Email}}", sale_email).replace("{Sale Email}", sale_email)
    if pitch_text:
        result = result.replace("{{AI_PITCH}}", pitch_text).replace("{AI_PITCH}", pitch_text)
    return result

# 🎨 HELPER FUNCTION: สร้าง HTML CARD ของ NEW MEDIA (สไตล์พรีเมียม)
def build_new_media_card_html(media_key, greeting_name, closing_target, sale_name, phone_num, ai_pitch, sale_email, is_cid=False):
    info = MEDIA_FOLDERS.get(media_key, MEDIA_FOLDERS["The 20"])
    imgs = info.get("images", ["the20_1.jpg", "the20_2.jpg", "the20_3.jpg"])
    
    if is_cid:
        img_src1 = "cid:media_img_0"
        img_src2 = "cid:media_img_1" if len(imgs) > 1 else img_src1
        img_src3 = "cid:media_img_2" if len(imgs) > 2 else img_src1
    else:
        img_src1 = f"{GITHUB_RAW_BASE}{imgs[0]}"
        img_src2 = f"{GITHUB_RAW_BASE}{imgs[1]}" if len(imgs) > 1 else img_src1
        img_src3 = f"{GITHUB_RAW_BASE}{imgs[2]}" if len(imgs) > 2 else img_src1

    body_text = replace_placeholders(info["body_intro"], greeting_name, closing_target, sale_name, phone_num)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:20px 0; background-color:#f1f5f9; font-family:'Sukhumvit Set', Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 620px; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <!-- HEADER -->
            <tr>
                <td style="padding: 20px 28px; background: #0f172a;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td style="font-size: 22px; font-weight: 800; color: #ffffff;">
                                Plan•B <span style="font-size: 11px; color: #38bdf8; font-weight: 700; letter-spacing: 1px;">MEDIA</span>
                            </td>
                            <td align="right" style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">
                                SPECIAL OOH RECOMMENDATION
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- CONTENT BODY -->
            <tr>
                <td style="padding: 24px 28px 16px 28px; font-size: 14px; line-height: 1.6; color: #334155;">
                    <p style="margin: 0 0 12px 0; font-size: 16px; font-weight: 700; color: #0f172a;">
                        เรียน {greeting_name}
                    </p>
                    
                    <!-- AI PITCH BOX -->
                    <div style="background-color: #f0f9ff; border-left: 4px solid #0284c7; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 14px; color: #0369a1; font-weight: 500;">
                        💡 {ai_pitch}
                    </div>

                    <p style="margin: 0 0 16px 0;">
                        {body_text}
                    </p>
                </td>
            </tr>

            <!-- MEDIA IMAGE GALLERY (GRID LAYOUT) -->
            <tr>
                <td style="padding: 0 28px 20px 28px;">
                    <!-- HIGHLIGHT IMAGE 1 -->
                    <div style="margin-bottom: 10px; border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0;">
                        <img src="{img_src1}" width="564" style="width:100%; max-width:564px; height:auto; display:block;" alt="Media Highlight 1">
                    </div>
                    
                    <!-- GRID IMAGES 2 & 3 -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="49%" style="padding-right: 1%;">
                                <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                                    <img src="{img_src2}" width="276" style="width:100%; max-width:276px; height:auto; display:block;" alt="Media Highlight 2">
                                </div>
                            </td>
                            <td width="49%" style="padding-left: 1%;">
                                <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                                    <img src="{img_src3}" width="276" style="width:100%; max-width:276px; height:auto; display:block;" alt="Media Highlight 3">
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- PREMIUM DRIVE LINK BUTTON (CTA) -->
            <tr>
                <td style="padding: 10px 28px 24px 28px; text-align: center;">
                    <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
                        <tr>
                            <td align="center" style="background-color: #0056b3; border-radius: 30px;">
                                <a href="{info['drive_link']}" target="_blank" style="display: inline-block; padding: 12px 28px; font-size: 13px; font-weight: 700; color: #ffffff; text-decoration: none;">
                                    📂 คลิกเปิดดู Media Plan & Rate Card ฉบับเต็ม (Google Drive) ➔
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- FOOTER -->
            <tr>
                <td style="padding: 20px 28px; background-color: #f8fafc; border-top: 1px solid #f1f5f9; font-size: 13px; color: #475569; line-height: 1.5;">
                    <p style="margin: 0 0 8px 0;">
                        หาก{closing_target} สนใจสื่อ {info['title']} หรือสอบถามข้อมูลแพ็กเกจเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {phone_num} หรือตอบกลับอีเมลนี้ได้เลยค่ะ
                    </p>
                    <p style="margin: 0; font-weight: 700; color: #0f172a;">
                        {sale_name} | {phone_num}<br>
                        <a href="mailto:{sale_email}" style="color: #0056b3; text-decoration: none;">{sale_email}</a>
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html

# 🤖 AI
