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

CREDENTIAL_DRIVE_URL_DEFAULT = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"

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
# MEDIA TEMPLATES DATA (NEW MEDIA MODE)
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
        "description": "สื่อในห้างสรรพสินค้า CentralWorld ทั่วประเทศ เหมาะกับ แฟชั่น, เครื่องสำอาง, รองเท้า, ร้านค้า Retail, FMCG, สกินแคร์, ความงาม",
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "drive_link": "https://drive.google.com/drive/folders/1jKRJBAlKcpauiUaNxTC0CuzK67_D6uOU",
        "body_intro": """สวัสดีค่ะ ทางเราขอแนะนำแพ็กเกจ <b>Central Network</b> ที่อัปเกรดครั้งใหญ่ โดยเปิดตัว CentralWorld 360 – สื่อดิจิทัลใหม่ล่าสุดในรูปแบบ จอ LED ทรงโค้งแบบ Tower Wraparound บริเวณลิฟต์แก้ว CentralWorld""",
        "images": ["central_w360_1.jpg", "central_w360_2.jpg", "central_w360_3.jpg"]
    },
    "The Skyline": {
        "title": "The Skyline",
        "description": "ป้ายภาพนิ่งขนาดใหญ่ทางเข้าสนามบินสุวรรณภูมิ เหมาะกับ สินค้าพรีเมียม, ท่องเที่ยว, โรงแรม, สายการบิน, อสังหาริมทรัพย์, ลักชัวรี",
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "drive_link": "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC",
        "body_intro": """สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ <b>The Skyline</b> สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ บนถนนทางเข้าสนามบินสุวรรณภูมิ""",
        "images": ["skyline_1.jpg", "skyline_2.jpg", "skyline_1.jpg"]
    },
    "rama 9 connected": {
        "title": "rama 9 connected",
        "description": "สื่อดิจิทัลใจกลาง CBD พระราม 9 ย่านธุรกิจ RCA เหมาะกับ ออฟฟิศ B2B, คลินิก, โรงพยาบาล, สถาบันการศึกษา",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"Rama 9 Connected\" สื่อโฆษณาใจกลาง CBD พระราม 9",
        "drive_link": "https://drive.google.com/drive/folders/1E8SfEFV2k7kmFBbiaj0atsQJrgwIB7Ij",
        "body_intro": """ขอแนะนำ <b>“RAMA 9 Connected”</b> สื่อโฆษณาดิจิทัลใหม่ล่าสุดใจกลาง CBD พระราม 9 ที่พร้อมให้บริการตั้งแต่วันที่ 1 มีนาคม 2025""",
        "images": ["rama9_1.jpg", "rama9_2.jpg", "rama9_1.jpg"]
    }
}

# 🧼 HELPER FUNCTION: สกัดข้อมูลรายชื่อ
def extract_sheet_data(record):
    c_name, comp_name = "", ""
    for k, v in record.items():
        key_str = str(k).strip().lower()
        val_str = str(v).strip() if pd.notna(v) else ""
        if key_str in ["name", "ชื่อผู้ติดต่อ", "contact name", "ชื่อ", "contact"] and val_str:
            c_name = val_str
            break
            
    for k, v in record.items():
        key_str = str(k).strip().lower()
        val_str = str(v).strip() if pd.notna(v) else ""
        if key_str in ["company name", "ชื่อบริษัท", "company", "แบรนด์", "brand", "บริษัท"] and val_str:
            comp_name = val_str
            break

    invalid_terms = ["-", "none", "nan", "null", ""]
    if c_name.lower() in invalid_terms: c_name = ""
    if comp_name.lower() in invalid_terms: comp_name = ""

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

# 🎨 1. HTML CARD - NEW MEDIA MODE
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
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:20px 0; background-color:#eef2f6; font-family:'Sukhumvit Set', Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 650px; background-color: #ffffff; border-radius: 18px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(15,23,42,0.06);">
            <tr>
                <td style="padding: 24px 32px; background: #0f172a;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td style="font-size: 24px; font-weight: 800; color: #ffffff;">Plan•B <span style="font-size: 11px; color: #38bdf8; font-weight: 700; letter-spacing: 1.5px;">MEDIA</span></td>
                            <td align="right" style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">SPECIAL OOH RECOMMENDATION</td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 28px 32px 18px 32px; font-size: 15px; line-height: 1.6; color: #334155;">
                    <p style="margin: 0 0 12px 0; font-size: 17px; font-weight: 800; color: #0f172a;">เรียน {greeting_name}</p>
                    <div style="background-color: #f0f9ff; border-left: 4px solid #0284c7; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; font-size: 14px; color: #0369a1; font-weight: 600;">
                        💡 {ai_pitch}
                    </div>
                    <p style="margin: 0 0 16px 0;">{body_text}</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 0 32px 20px 32px;">
                    <div style="margin-bottom: 12px; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                        <img src="{img_src1}" width="586" style="width:100%; max-width:586px; height:auto; display:block;" alt="Media Highlight 1">
                    </div>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="49%" style="padding-right: 1%;">
                                <div style="border-radius: 10px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
                                    <img src="{img_src2}" width="286" style="width:100%; max-width:286px; height:auto; display:block;" alt="Media Highlight 2">
                                </div>
                            </td>
                            <td width="49%" style="padding-left: 1%;">
                                <div style="border-radius: 10px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
                                    <img src="{img_src3}" width="286" style="width:100%; max-width:286px; height:auto; display:block;" alt="Media Highlight 3">
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px 32px 26px 32px; text-align: center;">
                    <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
                        <tr>
                            <td align="center" style="background-color: #0284c7; border-radius: 30px; box-shadow: 0 4px 14px rgba(2,132,199,0.35);">
                                <a href="{info['drive_link']}" target="_blank" style="display: inline-block; padding: 14px 32px; font-size: 14px; font-weight: 700; color: #ffffff; text-decoration: none;">
                                    📂 คลิกเปิดดู Media Plan & Rate Card ฉบับเต็ม (Google Drive) ➔
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 24px 32px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 13.5px; color: #475569; line-height: 1.6;">
                    <p style="margin: 0 0 10px 0;">หาก{closing_target} สนใจสื่อ {info['title']} หรือสอบถามข้อมูลแพ็กเกจเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {phone_num} หรือตอบกลับอีเมลนี้ได้เลยค่ะ</p>
                    <p style="margin: 0; font-weight: 800; color: #0f172a; font-size: 14px;">{sale_name} | {phone_num}<br><a href="mailto:{sale_email}" style="color: #0284c7; text-decoration: none; font-weight: 700;">{sale_email}</a></p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

# 🎨 2. HTML CARD - CREDENTIAL MODE (BENTO GRID DESIGN)
def build_credential_card_html(greeting_name, closing_target, sale_name, phone_num, sale_email, drive_url=CREDENTIAL_DRIVE_URL_DEFAULT, is_cid=False):
    if is_cid:
        showcase_img1 = "cid:showcase_img_0"
        showcase_img2 = "cid:showcase_img_1"
        showcase_img3 = "cid:showcase_img_2"
    else:
        showcase_img1 = f"{GITHUB_RAW_BASE}central_park_1.jpg"
        showcase_img2 = f"{GITHUB_RAW_BASE}central_w360_1.jpg"
        showcase_img3 = f"{GITHUB_RAW_BASE}nextopia_1.jpg"

    mailto_reply = f"mailto:{sale_email}?subject=[นัดหมาย] สนใจสอบถามข้อมูลสื่อโฆษณา Plan B Media"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:24px 0; background-color:#eef2f6; font-family:'Sukhumvit Set', Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 650px; background-color: #ffffff; border-radius: 20px; border: 1px solid #cbd5e1; overflow: hidden; box-shadow: 0 12px 32px rgba(15,23,42,0.08);">
            
            <!-- HEADER (PLAN B DARK NAVY) -->
            <tr>
                <td style="padding: 24px 32px; background: #0f172a;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td style="font-size: 24px; font-weight: 800; color: #ffffff;">Plan•B <span style="font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 1.5px; vertical-align: middle;">MEDIA</span></td>
                            <td align="right" style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">COMPANY CREDENTIAL 2026</td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- GREETING BENTO CARD -->
            <tr>
                <td style="padding: 28px 32px 16px 32px;">
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 22px;">
                        <p style="margin: 0 0 10px 0; font-size: 18px; font-weight: 800; color: #0f172a;">เรียน {greeting_name}</p>
                        <p style="margin: 0; color: #334155; font-size: 14.5px; line-height: 1.65;">
                            สวัสดีค่ะ ขออนุญาตแนะนำตัว ดิฉัน <b>{sale_name}</b> จากบริษัท <b>Plan B Media</b> นะคะ ทางเราเป็นผู้ให้บริการสื่อโฆษณานอกบ้าน (Out-of-Home Media) แบบครบวงจรที่ครอบคลุมพื้นที่ยุทธศาสตร์สำคัญทั่วประเทศค่ะ
                        </p>
                    </div>
                </td>
            </tr>

            <!-- SERVICES BENTO GRID -->
            <tr>
                <td style="padding: 0 32px 20px 32px;">
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px;">
                        <p style="margin: 0 0 14px 0; font-size: 13px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px;">📌 OUR MEDIA NETWORK & SERVICES (ขอบเขตบริการสื่อโฆษณา)</p>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-size: 13.5px; color: #334155; line-height: 1.85;">
                            <tr>
                                <td width="50%" style="padding-bottom: 8px;"><b>📺 Digital OOH:</b> จอดิจิทัล CBD & ย่านธุรกิจ</td>
                                <td width="50%" style="padding-bottom: 8px;"><b>🖼️ Classic Billboard:</b> ป้ายภาพนิ่งขนาดใหญ่</td>
                            </tr>
                            <tr>
                                <td style="padding-bottom: 8px;"><b>🛒 Retail Media:</b> สื่อในห้าง Central & Retail</td>
                                <td style="padding-bottom: 8px;"><b>🚌 Transit Media:</b> รถเมล์ & ขนส่งมวลชน</td>
                            </tr>
                            <tr>
                                <td><b>✈️ Airport Media:</b> สื่อสนามบิน</td>
                                <td><b>🌐 Global Network:</b> เครือข่ายสื่อต่างประเทศ</td>
                            </tr>
                        </table>
                    </div>
                </td>
            </tr>

            <!-- BENTO SHOWCASE GRID (3 COLUMNS SHOWCASE) -->
            <tr>
                <td style="padding: 0 32px 24px 32px;">
                    <p style="margin: 0 0 14px 0; font-size: 13px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px;">📸 PLAN B MEDIA SHOWCASE (ผลงานสื่อโฆษณาไฮไลต์)</p>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <!-- CARD 1 -->
                            <td width="31%" style="vertical-align: top;">
                                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%;">
                                    <img src="{showcase_img1}" width="180" style="width: 100%; max-width: 180px; height: 120px; object-fit: cover; display: block;" alt="Central Park Showcase">
                                    <div style="padding: 12px; font-size: 12px; line-height: 1.4;">
                                        <b style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 12.5px;">Central Park Showcase</b>
                                        <span style="color: #64748b;">ป้ายภาพนิ่งขนาดใหญ่ ทางเข้า CentralWorld</span>
                                    </div>
                                </div>
                            </td>
                            <td width="3.5%"></td>
                            <!-- CARD 2 -->
                            <td width="31%" style="vertical-align: top;">
                                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%;">
                                    <img src="{showcase_img2}" width="180" style="width: 100%; max-width: 180px; height: 120px; object-fit: cover; display: block;" alt="Central W360">
                                    <div style="padding: 12px; font-size: 12px; line-height: 1.4;">
                                        <b style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 12.5px;">Central W360 Network</b>
                                        <span style="color: #64748b;">จอดิจิทัล Elevator Wrap ใจกลาง CentralWorld</span>
                                    </div>
                                </div>
                            </td>
                            <td width="3.5%"></td>
                            <!-- CARD 3 -->
                            <td width="31%" style="vertical-align: top;">
                                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%;">
                                    <img src="{showcase_img3}" width="180" style="width: 100%; max-width: 180px; height: 120px; object-fit: cover; display: block;" alt="Nextopia Transit">
                                    <div style="padding: 12px; font-size: 12px; line-height: 1.4;">
                                        <b style="color: #0f172a; display: block; margin-bottom: 4px; font-size: 12.5px;">Transit Media: Nextopia</b>
                                        <span style="color: #64748b;">สื่อโฆษณาเคลื่อนที่ บนรถเมล์ Nextopia</span>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- PREMIUM CREDENTIAL DOWNLOAD CARD (CTA) -->
            <tr>
                <td style="padding: 0 32px 28px 32px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1.5px solid #0284c7; border-radius: 14px; padding: 22px; text-align: center;">
                        <tr>
                            <td>
                                <p style="margin: 0 0 6px 0; font-size: 15px; font-weight: 800; color: #0369a1; letter-spacing: 0.5px;">📁 PLAN B MEDIA PROFILE & CREDENTIAL</p>
                                <p style="margin: 0 0 14px 0; font-size: 12.5px; color: #0284c7;">รวบรวมภาพรวมสื่อโฆษณา ตัวอย่างผลงาน และข้อมูลบริษัทฉบับสมบูรณ์</p>
                                <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
                                    <tr>
                                        <td align="center" style="background-color: #0284c7; border-radius: 30px; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);">
                                            <a href="{drive_url}" target="_blank" style="display: inline-block; padding: 13px 32px; font-size: 14px; font-weight: 700; color: #ffffff; text-decoration: none;">
                                                📂 คลิกเปิดดู Company Credential Folder (Google Drive) ➔
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- FOOTER / CONTACT INFO WITH APPOINTMENT REPLY BUTTON -->
            <tr>
                <td style="padding: 24px 32px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 13.5px; color: #475569; line-height: 1.6;">
                    <p style="margin: 0 0 16px 0; color: #334155;">
                        ขอขอบคุณที่สละเวลาอ่านอีเมลฉบับนี้ และหวังว่าจะได้พูดคุยกับ{closing_target}ในเร็วๆ นี้นะคะ หากมีความสนใจต้องการข้อมูล Media Plan หรือขอเสนอราคาแคมเปญ สามารถติดต่อได้ทันทีค่ะ
                    </p>
                    
                    <div style="margin-bottom: 18px;">
                        <a href="{mailto_reply}" style="display: inline-block; padding: 12px 26px; background-color: #0f172a; color: #ffffff; font-weight: 700; font-size: 13.5px; text-decoration: none; border-radius: 25px; box-shadow: 0 4px 12px rgba(15,23,42,0.2);">
                            ✉️ คลิกเพื่อติดต่อนัดหมาย / ตอบกลับอีเมล ➔
                        </a>
                    </div>

                    <div style="padding-top: 14px; border-top: 1px dashed #cbd5e1;">
                        <p style="margin: 0; font-weight: 800; color: #0f172a; font-size: 14.5px;">{sale_name}</p>
                        <p style="margin: 3px 0 0 0; color: #475569;">📞 {phone_num} &nbsp;|&nbsp; ✉️ <a href="{mailto_reply}" style="color: #0284c7; text-decoration: none; font-weight: 700;">{sale_email}</a></p>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

# 🤖 AI ENGINE
def run_ai_smart_match_and_pitch(contact_name, company_name, index_hint=0):
    fallback_options = ["The 20", "Central Network [New Package]", "The Skyline", "rama 9 connected"]
    fallback_media = fallback_options[index_hint % len(fallback_options)]

    if not GEMINI_API_KEY:
        return fallback_media, f"AI แนะนำสื่อ {fallback_media} สำหรับ {company_name}", f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company_name} ค่ะ"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        media_context = {k: v.get("description", "") for k, v in MEDIA_FOLDERS.items()}
        prompt = f"ลูกค้า: {company_name}, เลือกสื่อจาก: {json.dumps(media_context, ensure_ascii=False)} ตอบเป็น JSON: {{'selected_media': 'ชื่อสื่อ', 'reason': 'เหตุผล', 'pitch': 'ข้อความเกริ่นนำ 2 บรรทัด'}}"
        data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            res_json = json.loads(json.loads(response.read().decode("utf-8"))["candidates"][0]["content"]["parts"][0]["text"])
            s_media = res_json.get("selected_media", fallback_media)
            if s_media not in MEDIA_FOLDERS: s_media = fallback_media
            return s_media, res_json.get("reason", ""), res_json.get("pitch", "")
    except Exception:
        return fallback_media, "AI วิเคราะห์ธุรกิจและเลือกสื่อที่เหมาะสม", f"ขอแนะนำสื่อโฆษณาทำเลศักยภาพสูงที่ตอบโจทย์แบรนด์ {company_name} ค่ะ"

# ==========================================
# SIDEBAR & STATE
# ==========================================
st.sidebar.title("⚙️ ข้อมูลผู้ส่ง (Plan B Media)")
user_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง", value="วิชญาดา (พลอย)")
user_email = st.sidebar.text_input("อีเมลองค์กร", value="wichayada.ph@planbmedia.co.th")
user_phone = st.sidebar.text_input("เบอร์โทรศัพท์", value="064-542-4441")

gmail_sender = st.sidebar.text_input("บัญชี Gmail ที่ใช้ส่ง", value=GMAIL_USER)
sender_password = st.sidebar.text_input("Google App Password", value=GMAIL_APP_PASS, type="password")
sheet_url_input = st.sidebar.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL)

step = st.sidebar.radio("เลือกขั้นตอน:", ["STEP 01 : จัดการรายชื่อลูกค้า", "STEP 02 : เลือกเนื้อหา & พรีวิว", "STEP 03 : ยืนยันยอด & กดส่งอีเมล"])
app_mode = st.sidebar.selectbox("เลือกประเภทอีเมลที่ต้องการส่ง:", [
    "1️⃣ New Media (เสนอขายแพ็กเกจสื่อเดิม)",
    "2️⃣ Credential (แนะนำตัวลูกค้าใหม่)",
    "3️⃣ Magnetic Report (รายงานสถิติ OOH ประจำเดือน)"
])

if 'recipients' not in st.session_state: st.session_state.recipients = []
if 'editor_key' not in st.session_state: st.session_state.editor_key = 0
if 'ai_results' not in st.session_state: st.session_state.ai_results = {}

st.title("📢 PLAN B MEDIA • AUTOMATION SYSTEM EMAIL")

# ==========================================
# STEP 01
# ==========================================
if step == "STEP 01 : จัดการรายชื่อลูกค้า":
    st.subheader("👥 STEP 01 : จัดการรายชื่อลูกค้าผู้รับ (รองรับ CC Email)")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 โหลดรายชื่อจาก Google Sheet Real-time"):
            csv_url = get_csv_url(sheet_url_input)
            if csv_url:
                df = pd.read_csv(csv_url).dropna(how='all')
                if 'CC' not in df.columns: df['CC'] = ""
                st.session_state.recipients = [{'ส่งอีเมล?': True, 'ที่มา': 'Google Sheets', **row.to_dict()} for _, row in df.iterrows()]
                st.session_state.editor_key += 1
                st.success(f"✅ ดึงรายชื่อสำเร็จ {len(st.session_state.recipients)} รายชื่อ!")
    with col2:
        nc = st.text_input("ชื่อบริษัท / แบรนด์")
        nn = st.text_input("ชื่อผู้ติดต่อ")
        ne = st.text_input("อีเมลผู้รับหลัก (To)")
        ncc = st.text_input("CC Email (ถ้ามี คั่นด้วยเครื่องหมายจุลภาค ,)")
        if st.button("➕ เพิ่มลูกค้ารายนี้"):
            if ne:
                st.session_state.recipients.append({
                    "ส่งอีเมล?": True, 
                    "ที่มา": "Manual", 
                    "Company Name": nc.strip(), 
                    "Name": nn.strip(), 
                    "Email": ne.strip(), 
                    "CC": ncc.strip()
                })
                st.session_state.editor_key += 1

    if st.session_state.recipients:
        edited_df = st.data_editor(pd.DataFrame(st.session_state.recipients), key=f"editor_{st.session_state.editor_key}", use_container_width=True)
        st.session_state.recipients = edited_df.to_dict('records')

# ==========================================
# STEP 02 : PREVIEW
# ==========================================
elif step == "STEP 02 : เลือกเนื้อหา & พรีวิว":
    st.subheader(f"🖼️ STEP 02 : พรีวิวอีเมลโหมด [{app_mode.split(' ')[1]}]")
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    
    if not selected_targets:
        st.warning("⚠️ กรุณากลับไปเลือกรายชื่อลูกค้าใน STEP 01 ก่อนค่ะ")
    else:
        if "1️⃣" in app_mode:
            if st.button("🤖 ให้ AI วิเคราะห์ & เลือกสื่อ OOH ให้ทุกแบรนด์พร้อมกัน", type="primary"):
                for idx, target in enumerate(selected_targets):
                    c_name, comp_name = extract_sheet_data(target)
                    s_media, r_reason, p_pitch = run_ai_smart_match_and_pitch(c_name, comp_name or "ลูกค้า", idx)
                    st.session_state.ai_results[str(target.get("Email") or f"c_{idx}")] = {"media": s_media, "reason": r_reason, "pitch": p_pitch}
                st.success("✅ AI ประมวลผลเรียบร้อยแล้วค่ะ!")

        for idx, target in enumerate(selected_targets, 1):
            c_name, comp_name = extract_sheet_data(target)
            email_key = str(target.get("Email") or f"c_{idx-1}").strip()
            cc_email = str(target.get("CC") or "").strip()
            
            if c_name and comp_name:
                greeting_name = f"คุณ{c_name} ({comp_name})"
                closing_target = f"คุณ{c_name}"
            elif comp_name:
                greeting_name = f"ทีมงานการตลาด {comp_name}"
                closing_target = f"ทางแบรนด์ {comp_name}"
            elif c_name:
                greeting_name = f"คุณ{c_name}"
                closing_target = f"คุณ{c_name}"
            else:
                greeting_name = "ทีมงานผู้ดูแลฝ่ายการตลาด"
                closing_target = "ทางองค์กรของท่าน"
            
            if "2️⃣" in app_mode:
                preview_html = build_credential_card_html(greeting_name, closing_target, user_name, user_phone, user_email, is_cid=False)
            else:
                ai_data = st.session_state.ai_results.get(email_key, {})
                selected_media = ai_data.get("media", list(MEDIA_FOLDERS.keys())[(idx-1) % len(MEDIA_FOLDERS)])
                ai_pitch = ai_data.get("pitch", f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การเติบโตของคุณค่ะ")
                preview_html = build_new_media_card_html(selected_media, greeting_name, closing_target, user_name, user_phone, ai_pitch, user_email, is_cid=False)

            cc_info = f" | 📑 CC: {cc_email}" if cc_email else ""
            with st.expander(f"📌 [{idx}/{len(selected_targets)}] พรีวิวการ์ดอีเมล: {greeting_name}{cc_info}", expanded=True):
                st.components.v1.html(preview_html, height=780, scrolling=True)

# ==========================================
# STEP 03 : SEND BATCH EMAILS
# ==========================================
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader(f"🚀 STEP 03 : ยืนยันยอดและกดส่งอีเมลโหมด [{app_mode.split(' ')[1]}]")
    selected_targets = [r for r in st.session_state.recipients if r.get('ส่งอีเมล?') == True]
    
    if selected_targets:
        if st.button("🚀 ยืนยันส่งอีเมลทั้งหมดทันที (Send Batch Emails)", type="primary", use_container_width=True):
            success_count = 0
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, target in enumerate(selected_targets):
                email_addr = str(target.get("Email") or "").strip()
                cc_addr_raw = str(target.get("CC") or "").strip()
                c_name, comp_name = extract_sheet_data(target)
                
                if c_name and comp_name:
                    greeting_name = f"คุณ{c_name} ({comp_name})"
                    closing_target = f"คุณ{c_name}"
                    display_target = f"{c_name} ({comp_name})"
                elif comp_name:
                    greeting_name = f"ทีมงานการตลาด {comp_name}"
                    closing_target = f"ทางแบรนด์ {comp_name}"
                    display_target = comp_name
                elif c_name:
                    greeting_name = f"คุณ{c_name}"
                    closing_target = f"คุณ{c_name}"
                    display_target = c_name
                else:
                    greeting_name = "ทีมงานผู้ดูแลฝ่ายการตลาด"
                    closing_target = "ทางองค์กรของท่าน"
                    display_target = email_addr
                    
                email_key = str(target.get("Email") or f"c_{idx}").strip()
                status_text.text(f"📤 กำลังส่งหา {display_target} ({email_addr})...")
                
                try:
                    msg = MIMEMultipart('mixed')
                    msg['From'] = formataddr((user_name, gmail_sender))
                    msg['To'] = email_addr
                    
                    recipients_all = [email_addr]
                    if cc_addr_raw:
                        msg['Cc'] = cc_addr_raw
                        cc_list = [c.strip() for c in cc_addr_raw.split(',') if c.strip()]
                        recipients_all.extend(cc_list)

                    msg['Reply-To'] = user_email
                    
                    if "2️⃣" in app_mode:
                        msg['Subject'] = "Plan B Media : ขออนุญาตนัดเข้าพบเพื่อนำเสนอสื่อโฆษณานอกบ้านสำหรับปี 2026"
                        body_html = build_credential_card_html(greeting_name, closing_target, user_name, user_phone, user_email, is_cid=True)
                    else:
                        ai_data = st.session_state.ai_results.get(email_key, {})
                        selected_media = ai_data.get("media", list(MEDIA_FOLDERS.keys())[idx % len(MEDIA_FOLDERS)])
                        ai_pitch = ai_data.get("pitch", f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การเติบโตของคุณค่ะ")
                        media_info = MEDIA_FOLDERS.get(selected_media, MEDIA_FOLDERS["The 20"])
                        msg['Subject'] = replace_placeholders(media_info["subject"], greeting_name, closing_target, user_name, user_phone)
                        body_html = build_new_media_card_html(selected_media, greeting_name, closing_target, user_name, user_phone, ai_pitch, user_email, is_cid=True)

                    msg_related = MIMEMultipart('related')
                    msg_related.attach(MIMEText(body_html, 'html', 'utf-8'))
                    
                    # EMBED BENTO SHOWCASE IMAGES FOR CREDENTIAL MODE
                    if "2️⃣" in app_mode:
                        showcase_files = ["central_park_1.jpg", "central_w360_1.jpg", "nextopia_1.jpg"]
                        for img_i, img_name in enumerate(showcase_files):
                            try:
                                img_url = f"{GITHUB_RAW_BASE}{img_name}"
                                res = requests.get(img_url, timeout=5)
                                if res.status_code == 200:
                                    mime_img = MIMEImage(res.content)
                                    mime_img.add_header('Content-ID', f'<showcase_img_{img_i}>')
                                    mime_img.add_header('Content-Disposition', 'inline', filename=img_name)
                                    msg_related.attach(mime_img)
                            except Exception:
                                pass
                    
                    # EMBED IMAGES FOR NEW MEDIA MODE
                    if "1️⃣" in app_mode:
                        media_info = MEDIA_FOLDERS.get(selected_media, MEDIA_FOLDERS["The 20"])
                        imgs = media_info.get("images", [])
                        for img_i, img_name in enumerate(imgs):
                            try:
                                img_url = f"{GITHUB_RAW_BASE}{img_name}"
                                res = requests.get(img_url, timeout=5)
                                if res.status_code == 200:
                                    mime_img = MIMEImage(res.content)
                                    mime_img.add_header('Content-ID', f'<media_img_{img_i}>')
                                    mime_img.add_header('Content-Disposition', 'inline', filename=img_name)
                                    msg_related.attach(mime_img)
                            except Exception:
                                pass

                    msg.attach(msg_related)

                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(gmail_sender, sender_password)
                        server.sendmail(gmail_sender, recipients_all, msg.as_string())
                        
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ ส่งหา {display_target} ไม่สำเร็จ: {e}")
                    
                progress_bar.progress((idx + 1) / len(selected_targets))
                
            status_text.empty()
            progress_bar.empty()
            st.balloons()
            st.success(f"🎉 ส่งอีเมลสำเร็จเรียบร้อยทั้งหมด **{success_count}** / **{len(selected_targets)}** รายชื่อ!")
