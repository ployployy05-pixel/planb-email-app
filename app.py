import base64
import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import json
import re
import urllib.request

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pandas as pd
import requests
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Plan B Media - Automation System Email",
    page_icon="📢",
    layout="wide",
)

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1PIMnucnqJmpCdnMLa13_7nuP9lOiEoXuFgVGlW5AGuw/edit?gid=1224436480#gid=1224436480"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ployployy05-pixel/planb-email-app/main/"
CREDENTIAL_DRIVE_URL_DEFAULT = "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC"

# Secrets & Keys
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")


def get_csv_url(sheet_url):
    try:
        sheet_id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
        sheet_id = sheet_id_match.group(1) if sheet_id_match else sheet_url
        gid_match = re.search(r"gid=([0-9]+)", sheet_url)
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
        "subject": '[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด "The 20" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก',
        "drive_link": "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC",
        "body_intro": """สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ <b>The 20</b> สื่อดิจิทัลใหม่ล่าสุด จาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยสื่อนี้ได้พลิกโฉม ป้ายโฆษณา Serie Poles เดิม ให้กลายเป็น จอ LED กว่า 74 จอ ที่เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD""",
        "images": ["the20_1.jpg", "the20_2.jpg", "the20_3.jpg"],
    },
    "Central Network [New Package]": {
        "title": "Central Network [New Package]",
        "description": "สื่อในห้างสรรพสินค้า CentralWorld ทั่วประเทศ เหมาะกับ แฟชั่น, เครื่องสำอาง, รองเท้า, ร้านค้า Retail, FMCG, สกินแคร์, ความงาม",
        "subject": "[Plan B Media] อัปเกรด Central Network ใหม่ – สื่อในห้างครอบคลุมทั่วประเทศ พร้อมสื่อใหม่ใจกลาง CentralWorld",
        "drive_link": "https://drive.google.com/drive/folders/1jKRJBAlKcpauiUaNxTC0CuzK67_D6uOU",
        "body_intro": """สวัสดีค่ะ ทางเราขอแนะนำแพ็กเกจ <b>Central Network</b> ที่อัปเกรดครั้งใหญ่ โดยเปิดตัว CentralWorld 360 – สื่อดิจิทัลใหม่ล่าสุดในรูปแบบ จอ LED ทรงโค้งแบบ Tower Wraparound บริเวณลิฟต์แก้ว CentralWorld""",
        "images": [
            "central_w360_1.jpg",
            "central_w360_2.jpg",
            "central_w360_3.jpg",
        ],
    },
    "The Skyline": {
        "title": "The Skyline",
        "description": "ป้ายภาพนิ่งขนาดใหญ่ทางเข้าสนามบินสุวรรณภูมิ เหมาะกับ สินค้าพรีเมียม, ท่องเที่ยว, โรงแรม, สายการบิน, อสังหาริมทรัพย์, ลักชัวรี",
        "subject": "[Plan B Media] OUTDOOR TRENDS: โอกาสเข้าถึงกลุ่มผู้บริโภคระดับพรีเมียม ด้วยสื่อใหม่ ‘THE SKYLINE’",
        "drive_link": "https://drive.google.com/drive/folders/1BXs65eLHSH0RSmyC7JF0LneUlr7kaMrC",
        "body_intro": """สวัสดีค่ะ หากคุณต้องการสร้างแบรนด์ให้โดดเด่น และเข้าถึงกลุ่มลูกค้าระดับพรีเมียม {{Sale name}} ขอแนะนำสื่อใหม่ <b>The Skyline</b> สื่อโฆษณาป้ายภาพนิ่งขนาดใหญ่ บนถนนทางเข้าสนามบินสุวรรณภูมิ""",
        "images": ["skyline_1.jpg", "skyline_2.jpg", "skyline_1.jpg"],
    },
    "rama 9 connected": {
        "title": "rama 9 connected",
        "description": "สื่อดิจิทัลใจกลาง CBD พระราม 9 ย่านธุรกิจ RCA เหมาะกับ ออฟฟิศ B2B, คลินิก, โรงพยาบาล, สถาบันการศึกษา",
        "subject": '[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด "Rama 9 Connected" สื่อโฆษณาใจกลาง CBD พระราม 9',
        "drive_link": "https://drive.google.com/drive/folders/1E8SfEFV2k7kmFBbiaj0atsQJrgwIB7Ij",
        "body_intro": """ขอแนะนำ <b>“RAMA 9 Connected”</b> สื่อโฆษณาดิจิทัลใหม่ล่าสุดใจกลาง CBD พระราม 9 ที่พร้อมให้บริการตั้งแต่วันที่ 1 มีนาคม 2025""",
        "images": ["rama9_1.jpg", "rama9_2.jpg", "rama9_1.jpg"],
    },
}


# 🧼 HELPER FUNCTION: สกัดข้อมูลรายชื่อ
def extract_sheet_data(record):
    c_name, comp_name = "", ""
    for k, v in record.items():
        key_str = str(k).strip().lower()
        val_str = str(v).strip() if pd.notna(v) else ""
        if (
            key_str
            in ["name", "ชื่อผู้ติดต่อ", "contact name", "ชื่อ", "contact"]
            and val_str
        ):
            c_name = val_str
            break

    for k, v in record.items():
        key_str = str(k).strip().lower()
        val_str = str(v).strip() if pd.notna(v) else ""
        if (
            key_str
            in [
                "company name",
                "ชื่อบริษัท",
                "company",
                "แบรนด์",
                "brand",
                "บริษัท",
            ]
            and val_str
        ):
            comp_name = val_str
            break

    invalid_terms = ["-", "none", "nan", "null", ""]
    if c_name.lower() in invalid_terms:
        c_name = ""
    if comp_name.lower() in invalid_terms:
        comp_name = ""

    return c_name, comp_name


# 🧹 HELPER FUNCTION: แทนที่ตัวแปรในข้อความ
def replace_placeholders(
    text,
    greeting_name,
    closing_target,
    sale_name,
    phone_num,
    pitch_text="",
    sale_email="",
):
    result = str(text)
    result = result.replace("{{Greeting Name}}", greeting_name).replace(
        "{Greeting Name}", greeting_name
    )
    result = result.replace("{{Closing Target}}", closing_target).replace(
        "{Closing Target}", closing_target
    )
    result = result.replace("{{Sale name}}", sale_name).replace(
        "{Sale name}", sale_name
    )
    result = result.replace("{{Tel}}", phone_num).replace("{Tel}", phone_num)
    if sale_email:
        result = result.replace("{{Sale Email}}", sale_email).replace(
            "{Sale Email}", sale_email
        )
    if pitch_text:
        result = result.replace("{{AI_PITCH}}", pitch_text).replace(
            "{AI_PITCH}", pitch_text
        )
    return result


# 🎨 1. HTML CARD - NEW MEDIA MODE
def build_new_media_card_html(
    media_key,
    greeting_name,
    closing_target,
    sale_name,
    phone_num,
    ai_pitch,
    sale_email,
    is_cid=False,
):
    info = MEDIA_FOLDERS.get(media_key, MEDIA_FOLDERS["The 20"])
    imgs = info.get("images", ["the20_1.jpg", "the20_2.jpg", "the20_3.jpg"])

    img_src1 = f"{GITHUB_RAW_BASE}{imgs[0]}"
    img_src2 = f"{GITHUB_RAW_BASE}{imgs[1]}" if len(imgs) > 1 else img_src1
    img_src3 = f"{GITHUB_RAW_BASE}{imgs[2]}" if len(imgs) > 2 else img_src1

    body_text = replace_placeholders(
        info["body_intro"], greeting_name, closing_target, sale_name, phone_num
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0; padding:20px 0; background-color:#f1f5f9; font-family:'Sukhumvit Set', Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <tr>
                <td style="padding: 22px 30px; background: #0f172a;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td style="font-size: 22px; font-weight: 800; color: #ffffff;">Plan•B <span style="font-size: 11px; color: #38bdf8; font-weight: 700; letter-spacing: 1px;">MEDIA</span></td>
                            <td align="right" style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">SPECIAL OOH RECOMMENDATION</td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 26px 30px 16px 30px; font-size: 15px; line-height: 1.6; color: #334155;">
                    <p style="margin: 0 0 12px 0; font-size: 16px; font-weight: 700; color: #0f172a;">เรียน {greeting_name}</p>
                    <div style="background-color: #f0f9ff; border-left: 4px solid #0284c7; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 14px; color: #0369a1; font-weight: 500;">
                        💡 {ai_pitch}
                    </div>
                    <p style="margin: 0 0 16px 0;">{body_text}</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 0 30px 20px 30px;">
                    <div style="margin-bottom: 10px; border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0;">
                        <img src="{img_src1}" width="540" style="width:100%; max-width:540px; height:auto; display:block;" alt="Media Highlight 1">
                    </div>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="49%" style="padding-right: 1%;">
                                <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                                    <img src="{img_src2}" width="265" style="width:100%; max-width:265px; height:auto; display:block;" alt="Media Highlight 2">
                                </div>
                            </td>
                            <td width="49%" style="padding-left: 1%;">
                                <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                                    <img src="{img_src3}" width="265" style="width:100%; max-width:265px; height:auto; display:block;" alt="Media Highlight 3">
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px 30px 24px 30px; text-align: center;">
                    <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
                        <tr>
                            <td align="center" style="background-color: #0056b3; border-radius: 30px;">
                                <a href="{info['drive_link']}" target="_blank" style="display: inline-block; padding: 13px 30px; font-size: 14px; font-weight: 700; color: #ffffff; text-decoration: none;">
                                    📂 คลิกเปิดดู Media Plan & Rate Card ฉบับเต็ม (Google Drive) ➔
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 22px 30px; background-color: #f8fafc; border-top: 1px solid #f1f5f9; font-size: 13px; color: #475569; line-height: 1.5;">
                    <p style="margin: 0 0 8px 0;">หาก{closing_target} สนใจสื่อ {info['title']} หรือสอบถามข้อมูลแพ็กเกจเพิ่มเติม สามารถติดต่อได้ที่เบอร์ {phone_num} หรือตอบกลับอีเมลนี้ได้เลยค่ะ</p>
                    <p style="margin: 0; font-weight: 700; color: #0f172a;">{sale_name} | {phone_num}<br><a href="mailto:{sale_email}" style="color: #0056b3; text-decoration: none;">{sale_email}</a></p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# 🎨 2. HTML CARD - CREDENTIAL MODE
def build_credential_card_html(
    greeting_name,
    closing_target,
    sale_name,
    phone_num,
    sale_email,
    drive_url=CREDENTIAL_DRIVE_URL_DEFAULT,
    is_cid=False,
):
    mailto_reply = f"mailto:{sale_email}?subject=[นัดหมาย] สนใจสอบถามข้อมูลสื่อโฆษณา Plan B Media"

    img_classic = f"{GITHUB_RAW_BASE}Classic.png"
    img_digital = f"{GITHUB_RAW_BASE}Digital.jpg"
    img_retail = f"{GITHUB_RAW_BASE}Retail.jpg"
    img_transit = f"{GITHUB_RAW_BASE}Transit.jpg"
    img_airport = f"{GITHUB_RAW_BASE}Airport.jpg"
    img_international = f"{GITHUB_RAW_BASE}International.png"
    img_footer_banner = f"{GITHUB_RAW_BASE}footer_banner.jpg"

    return f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin: 0; padding: 20px 0; background-color: #f1f5f9; font-family: 'Sukhumvit Set', Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="580" style="width: 580px; max-width: 580px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 8px 24px rgba(15,23,42,0.08);">
            <tr>
                <td style="background-color: #0b1a3a; padding: 20px 28px; color: #ffffff;">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td align="left" style="font-size: 22px; font-weight: 800; color: #ffffff; font-family: Arial, sans-serif;">Plan•B MEDIA</td>
                            <td align="right" style="font-size: 11px; color: #38bdf8; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; font-family: Arial, sans-serif;">COMPANY CREDENTIAL 2026</td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 26px 28px; color: #1e293b; font-size: 15px; line-height: 1.65; font-family: 'Sukhumvit Set', Arial, sans-serif;">
                    <div style="margin-bottom: 20px;">
                        เรียน {greeting_name},<br><br>
                        สวัสดีค่ะ ขออนุญาตแนะนำตัว พลอย Account Executive I, Sales จาก บริษัท แพลนบี มีเดีย นะคะ<br><br>
                        ขออนุญาตติดต่อเพื่อเสนอสื่อโฆษณานอกบ้าน (Out-of-Home Media) เพื่อช่วยยกระดับการรับรู้ของแบรนด์ให้เข้าถึงกลุ่มเป้าหมายได้อย่างแม่นยำและสร้าง Impact สูงสุดค่ะ
                    </div>

                    <table width="524" border="0" cellpadding="0" cellspacing="0" align="center" style="width: 524px; margin: 20px auto;">
                        <tr>
                            <td width="168" align="center" style="padding: 0 4px 12px 4px; vertical-align: top;">
                                <div style="width: 168px; height: 280px; overflow: hidden; border-radius: 8px; background-color: #ffffff;">
                                    <img src="{img_classic}" width="168" height="280" style="width: 168px; height: 280px; object-fit: cover; object-position: top; display: block; border-radius: 8px; border: 0;" alt="Classic Billboard">
                                </div>
                            </td>
                            <td width="168" align="center" style="padding: 0 4px 12px 4px; vertical-align: top;">
                                <div style="width: 168px; height: 280px; overflow: hidden; border-radius: 8px; background-color: #ffffff;">
                                    <img src="{img_digital}" width="168" height="280" style="width: 168px; height: 280px; object-fit: cover; object-position: top; display: block; border-radius: 8px; border: 0;" alt="Digital OOH">
                                </div>
                            </td>
                            <td width="168" align="center" style="padding: 0 4px 12px 4px; vertical-align: top;">
                                <div style="width: 168px; height: 280px; overflow: hidden; border-radius: 8px; background-color: #ffffff;">
                                    <img src="{img_retail}" width="168" height="280" style="width: 168px; height: 280px; object-fit: cover; object-position: top; display: block; border-radius: 8px; border: 0;" alt="Retail Media">
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td width="168" align="center" style="padding: 0 4px 0 4px; vertical-align: top;">
                                <div style="width: 168px; height: 280px; overflow: hidden; border-radius: 8px; background-color: #ffffff;">
                                    <img src="{img_transit}" width="168" height="280" style="width: 168px; height: 280px; object-fit: cover; object-position: top; display: block; border-radius: 8px; border: 0;" alt="Transit Media">
                                </div>
                            </td>
                            <td width="168" align="center" style="padding: 0 4px 0 4px; vertical-align: top;">
                                <div style="width: 168px; height: 280px; overflow: hidden; border-radius: 8px; background-color: #ffffff;">
                                    <img src="{img_airport}" width="168" height="280" style="width: 168px; height: 280px; object-fit: cover; object-position: top; display: block; border-radius: 8px; border: 0;" alt="Airport Media">
                                </div>
                            </td>
                            <td width="168" align="center" style="padding: 0 4px 0 4px; vertical-align: top;">
                                <div style="width: 168px; height: 280px; overflow: hidden; border-radius: 8px; background-color: #ffffff;">
                                    <img src="{img_international}" width="168" height="280" style="width: 168px; height: 280px; object-fit: cover; object-position: top; display: block; border-radius: 8px; border: 0;" alt="International Media">
                                </div>
                            </td>
                        </tr>
                    </table>

                    <div style="margin: 20px 0;">
                        หากทาง{closing_target} พอมีเวลาสะดวก พลอยขออนุญาตนัดหมายเข้าพบ หรือพูดคุยสั้นๆ ผ่าน Online Meeting ประมาณ <b>15-20 นาที</b> เพื่อนำเสนอ Media Plan และสิทธิพิเศษสำหรับปี 2026 ให้พิจารณาค่ะ
                    </div>

                    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f0f9ff; border: 1.5px solid #0284c7; border-radius: 12px; margin-bottom: 20px;">
                        <tr>
                            <td align="center" style="padding: 18px;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: 800; color: #0369a1;">📁 PLAN B MEDIA PROFILE & CREDENTIAL 2026</p>
                                <a href="{drive_url}" target="_blank" style="display: inline-block; background-color: #0284c7; color: #ffffff; padding: 12px 26px; border-radius: 30px; font-weight: 700; text-decoration: none; font-size: 13.5px;">
                                    📂 คลิกเปิดดู Company Credential Folder (Google Drive) ➔
                                </a>
                            </td>
                        </tr>
                    </table>

                    <div style="margin-bottom: 20px;">
                        <a href="{mailto_reply}" style="display: inline-block; background-color: #0f172a; color: #ffffff; padding: 11px 24px; border-radius: 25px; font-weight: 700; text-decoration: none; font-size: 13px;">
                            ✉️ คลิกเพื่อติดต่อนัดหมาย / ตอบกลับอีเมล ➔
                        </a>
                    </div>

                    <img src="{img_footer_banner}" width="524" style="width: 524px; max-width: 524px; height: auto; border-radius: 8px; margin: 10px 0 16px 0; display: block; border: 1px solid #e2e8f0;" alt="Plan B Media Network Banner">

                    <div style="border-top: 1px solid #e2e8f0; padding-top: 18px; font-size: 13px; color: #475569; line-height: 1.6;">
                        ขอขอบคุณที่สละเวลาพิจารณาข้อมูล และหวังเป็นอย่างยิ่งว่าจะได้มีโอกาสร่วมงานกันนะคะ<br><br>
                        <div style="font-size: 14.5px; font-weight: 800; color: #0f172a; margin-bottom: 2px;">วิชญาดา (พลอย) | Account Executive I, Sales</div>
                        Plan B Media Public Company Limited<br>
                        📞 <b>{phone_num}</b> &nbsp;|&nbsp; ✉️ <a href="{mailto_reply}" style="color: #0284c7; text-decoration: none; font-weight: 700;">{sale_email}</a>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# 🤖 AI ENGINE (Google Gemini 1.5 Flash API Engine)
def run_ai_smart_match_and_pitch(contact_name, company_name, index_hint=0):
    fallback_options = [
        "The 20",
        "Central Network [New Package]",
        "The Skyline",
        "rama 9 connected",
    ]
    fallback_media = fallback_options[index_hint % len(fallback_options)]

    if not GEMINI_API_KEY:
        return (
            fallback_media,
            f"AI แนะนำสื่อ {fallback_media} สำหรับ {company_name}",
            f"ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การสร้างความโดดเด่นให้กับแบรนด์ {company_name} ค่ะ",
        )

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        media_context = {
            k: v.get("description", "") for k, v in MEDIA_FOLDERS.items()
        }
        prompt = f"ลูกค้า: {company_name}, เลือกสื่อจาก: {json.dumps(media_context, ensure_ascii=False)} ตอบเป็น JSON: {{'selected_media': 'ชื่อสื่อ', 'reason': 'เหตุผล', 'pitch': 'ข้อความเกริ่นนำ 2 บรรทัด'}}"
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            res_json = json.loads(
                json.loads(response.read().decode("utf-8"))["candidates"][0][
                    "content"
                ]["parts"][0]["text"]
            )
            s_media = res_json.get("selected_media", fallback_media)
            if s_media not in MEDIA_FOLDERS:
                s_media = fallback_media
            return (
                s_media,
                res_json.get("reason", ""),
                res_json.get("pitch", ""),
            )
    except Exception:
        return (
            fallback_media,
            "AI (Gemini 1.5 Flash) วิเคราะห์ธุรกิจและเลือกสื่อที่เหมาะสม",
            f"ขอแนะนำสื่อโฆษณาทำเลศักยภาพสูงที่ตอบโจทย์แบรนด์ {company_name} ค่ะ",
        )


# ==========================================
# SIDEBAR & STATE MANAGEMENT
# ==========================================
st.sidebar.title("⚙️ ข้อมูลผู้ส่ง (Plan B Media)")
user_name = st.sidebar.text_input("ชื่อ-นามสกุล ผู้ส่ง", value="วิชญาดา (พลอย)")
user_email = st.sidebar.text_input(
    "อีเมลองค์กร", value="wichayada.ph@planbmedia.co.th"
)
user_phone = st.sidebar.text_input("เบอร์โทรศัพท์", value="064-542-4441")

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Gmail OAuth 2.0 Credentials")
client_id = st.sidebar.text_input(
    "Google Client ID",
    type="password",
    help="Client ID ที่สร้างขึ้นจาก Desktop App",
)
client_secret = st.sidebar.text_input(
    "Google Client Secret",
    type="password",
    help="Client Secret ที่สร้างขึ้นจาก Desktop App",
)
refresh_token = st.sidebar.text_input(
    "Refresh Token",
    value="1//04EXnnYDt12VjCgYIARAAGAQSSQF-L9IrKPOhl9XbvnQ1ztXN8tzT9QAlnSx5EX3XpBIm-f3IueKK5CDcHJJQtUyf-dmvNLRc0LtStd-g16OOxYwBUgz0kEg6SGE",
    type="password",
)

st.sidebar.markdown("---")
sheet_url_input = st.sidebar.text_input(
    "Google Sheet URL", value=DEFAULT_SHEET_URL
)

step = st.sidebar.radio(
    "เลือกขั้นตอน:",
    [
        "STEP 01 : จัดการรายชื่อลูกค้า",
        "STEP 02 : เลือกเนื้อหา & พรีวิว",
        "STEP 03 : ยืนยันยอด & กดส่งอีเมล",
    ],
)
app_mode = st.sidebar.selectbox(
    "เลือกประเภทอีเมลที่ต้องการส่ง:",
    [
        "1️⃣ New Media (เสนอขายแพ็กเกจสื่อเดิม)",
        "2️⃣ Credential (แนะนำตัวลูกค้าใหม่)",
        "3️⃣ Magnetic Report (รายงานสถิติ OOH ประจำเดือน)",
    ],
)

if "recipients" not in st.session_state:
    st.session_state.recipients = []
if "editor_key" not in st.session_state:
    st.session_state.editor_key = 0
if "ai_results" not in st.session_state:
    st.session_state.ai_results = {}
if "sent_log" not in st.session_state:
    st.session_state.sent_log = []

st.title("📢 PLAN B MEDIA • AUTOMATION SYSTEM EMAIL")
st.caption(
    "🤖 Powered by **Google Gemini 1.5 Flash API** | AI Integration Level 4 System"
)

# ==========================================
# STEP 01 : CUSTOMER MANAGEMENT
# ==========================================
if step == "STEP 01 : จัดการรายชื่อลูกค้า":
    st.subheader(
        "👥 STEP 01 : จัดการรายชื่อลูกค้าผู้รับ (รองรับ CC Email)"
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 โหลดรายชื่อจาก Google Sheet Real-time"):
            csv_url = get_csv_url(sheet_url_input)
            if csv_url:
                df = pd.read_csv(csv_url).dropna(how="all")
                if "CC" not in df.columns:
                    df["CC"] = ""
                st.session_state.recipients = [
                    {"ส่งอีเมล?": True, "ที่มา": "Google Sheets", **row.to_dict()}
                    for _, row in df.iterrows()
                ]
                st.session_state.editor_key += 1
                st.success(
                    f"✅ ดึงรายชื่อสำเร็จ {len(st.session_state.recipients)} รายชื่อ!"
                )
    with col2:
        nc = st.text_input("ชื่อบริษัท / แบรนด์")
        nn = st.text_input("ชื่อผู้ติดต่อ")
        ne = st.text_input("อีเมลผู้รับหลัก (To)")
        ncc = st.text_input(
            "CC Email (ถ้ามี คั่นด้วยเครื่องหมายจุลภาค ,)"
        )
        if st.button("➕ เพิ่มลูกค้ารายนี้"):
            if ne:
                st.session_state.recipients.append(
                    {
                        "ส่งอีเมล?": True,
                        "ที่มา": "Manual",
                        "Company Name": nc.strip(),
                        "Name": nn.strip(),
                        "Email": ne.strip(),
                        "CC": ncc.strip(),
                    }
                )
                st.session_state.editor_key += 1

    if st.session_state.recipients:
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.recipients),
            key=f"editor_{st.session_state.editor_key}",
            use_container_width=True,
        )
        st.session_state.recipients = edited_df.to_dict("records")

# ==========================================
# STEP 02 : PREVIEW & AI MATCHING
# ==========================================
elif step == "STEP 02 : เลือกเนื้อหา & พรีวิว":
    st.subheader(f"🖼️ STEP 02 : พรีวิวอีเมลโหมด [{app_mode.split(' ')[1]}]")
    selected_targets = [
        r for r in st.session_state.recipients if r.get("ส่งอีเมล?") == True
    ]

    if not selected_targets:
        st.warning("⚠️ กรุณากลับไปเลือกรายชื่อลูกค้าใน STEP 01 ก่อนค่ะ")
    else:
        if "1️⃣" in app_mode:
            if st.button(
                "🤖 ให้ AI (Gemini 1.5 Flash) วิเคราะห์ & เลือกสื่อ OOH ให้ทุกแบรนด์พร้อมกัน",
                type="primary",
            ):
                for idx, target in enumerate(selected_targets):
                    c_name, comp_name = extract_sheet_data(target)
                    s_media, r_reason, p_pitch = run_ai_smart_match_and_pitch(
                        c_name, comp_name or "ลูกค้า", idx
                    )
                    st.session_state.ai_results[
                        str(target.get("Email") or f"c_{idx}")
                    ] = {
                        "media": s_media,
                        "reason": r_reason,
                        "pitch": p_pitch,
                    }
                st.success(
                    "✅ Gemini 1.5 Flash API ประมวลผลวิเคราะห์เรียบร้อยแล้วค่ะ!"
                )

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
                preview_html = build_credential_card_html(
                    greeting_name,
                    closing_target,
                    user_name,
                    user_phone,
                    user_email,
                    is_cid=False,
                )
            else:
                ai_data = st.session_state.ai_results.get(email_key, {})
                selected_media = ai_data.get(
                    "media",
                    list(MEDIA_FOLDERS.keys())[(idx - 1) % len(MEDIA_FOLDERS)],
                )
                ai_pitch = ai_data.get(
                    "pitch",
                    "ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การเติบโตของคุณค่ะ",
                )
                preview_html = build_new_media_card_html(
                    selected_media,
                    greeting_name,
                    closing_target,
                    user_name,
                    user_phone,
                    ai_pitch,
                    user_email,
                    is_cid=False,
                )

            cc_info = f" | 📑 CC: {cc_email}" if cc_email else ""
            with st.expander(
                f"📌 [{idx}/{len(selected_targets)}] พรีวิวการ์ดอีเมล: {greeting_name}{cc_info}",
                expanded=True,
            ):
                st.components.v1.html(preview_html, height=850, scrolling=True)

# ==========================================
# STEP 03 : REVIEW & BATCH SENDING (GMAIL API OAUTH 2.0 INTEGRATED)
# ==========================================
elif step == "STEP 03 : ยืนยันยอด & กดส่งอีเมล":
    st.subheader(
        f"🚀 STEP 03 : Review & Batch Sending [{app_mode.split(' ')[1]}]"
    )
    selected_targets = [
        r for r in st.session_state.recipients if r.get("ส่งอีเมล?") == True
    ]

    if not selected_targets:
        st.warning(
            "⚠️ ไม่พบรายชื่อลูกค้าที่เลือกส่ง! กรุณากลับไปเลือกรายชื่อใน STEP 01 ก่อนนะคะ"
        )
    else:
        # 📊 1. SUMMARY METRICS DASHBOARD
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("📧 จำนวนผู้รับหลัก (To)", f"{len(selected_targets)} ราย")
        cc_count = sum(
            [1 for r in selected_targets if str(r.get("CC") or "").strip()]
        )
        m_col2.metric("📑 มีการ CC อีเมล", f"{cc_count} ราย")
        m_col3.metric("🎯 โหมดที่ใช้ส่ง", app_mode.split(" ")[1])

        st.markdown("---")

        # 📋 2. REVIEW TARGETS TABLE
        st.markdown("### 📋 ตารางสรุปรายชื่อที่จะจัดส่งใน Batch นี้")
        review_data = []
        for idx, target in enumerate(selected_targets, 1):
            c_name, comp_name = extract_sheet_data(target)
            email_addr = str(target.get("Email") or "").strip()
            cc_addr = str(target.get("CC") or "").strip()
            email_key = email_addr or f"c_{idx-1}"

            ai_info = st.session_state.ai_results.get(email_key, {})
            selected_media = (
                ai_info.get(
                    "media",
                    list(MEDIA_FOLDERS.keys())[(idx - 1) % len(MEDIA_FOLDERS)],
                )
                if "1️⃣" in app_mode
                else "Credential Profile 2026"
            )

            review_data.append(
                {
                    "ลำดับ": idx,
                    "แบรนด์ / บริษัท": comp_name or "-",
                    "ผู้ติดต่อ": c_name or "-",
                    "อีเมลผู้รับ (To)": email_addr,
                    "CC Email": cc_addr or "-",
                    "สื่อ OOH ที่ AI เลือก": selected_media,
                }
            )

        st.dataframe(pd.DataFrame(review_data), use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 🚀 3. ACTION BUTTON & BATCH EXECUTION (GMAIL API OAUTH 2.0)
        send_btn_label = f"🚀 ยืนยันส่งอีเมลหาลูกค้า {len(selected_targets)} รายนี้ทันที (Send Batch Emails)"
        if st.button(send_btn_label, type="primary", use_container_width=True):
            if not client_id or not client_secret or not refresh_token:
                st.error(
                    "❌ กรุณากรอก Google Client ID, Client Secret และ Refresh Token ใน Sidebar ด้านซ้ายก่อนส่งค่ะ"
                )
            else:
                success_count = 0
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # 1. Setup Gmail API Credentials จาก OAuth Refresh Token
                    creds = Credentials(
                        token=None,
                        refresh_token=refresh_token,
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=client_id,
                        client_secret=client_secret,
                    )
                    service = build("gmail", "v1", credentials=creds)

                    # 2. Loop ส่งอีเมลหาลูกค้าทีละราย (นำส่งปลายทางทั้ง Gmail และ Outlook)
                    for idx, target in enumerate(selected_targets):
                        c_name, comp_name = extract_sheet_data(target)
                        to_email = str(target.get("Email") or "").strip()
                        cc_email = str(target.get("CC") or "").strip()
                        email_key = to_email or f"c_{idx}"

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

                        # ประกอบเนื้อหา HTML และ Subject
                        if "2️⃣" in app_mode:
                            subject = "[Plan B Media] ขออนุญาตแนะนำตัวและเรียนเสนอสื่อโฆษณานอกบ้าน (OOH Media) สำหรับปี 2026"
                            html_body = build_credential_card_html(
                                greeting_name,
                                closing_target,
                                user_name,
                                user_phone,
                                user_email,
                                is_cid=False,
                            )
                        else:
                            ai_info = st.session_state.ai_results.get(
                                email_key, {}
                            )
                            selected_media = ai_info.get(
                                "media",
                                list(MEDIA_FOLDERS.keys())
                                [idx % len(MEDIA_FOLDERS)],
                            )
                            ai_pitch = ai_info.get(
                                "pitch",
                                "ขอแนะนำสื่อโฆษณาคุณภาพทำเลศักยภาพสูง ที่ตอบโจทย์การเติบโตของคุณค่ะ",
                            )
                            media_info = MEDIA_FOLDERS.get(
                                selected_media, MEDIA_FOLDERS["The 20"]
                            )
                            subject = media_info["subject"]
                            html_body = build_new_media_card_html(
                                selected_media,
                                greeting_name,
                                closing_target,
                                user_name,
                                user_phone,
                                ai_pitch,
                                user_email,
                                is_cid=False,
                            )

                        # สร้าง MIME Email Object
                        msg = MIMEMultipart()
                        msg["From"] = formataddr((user_name, user_email))
                        msg["To"] = to_email
                        if cc_email:
                            msg["Cc"] = cc_email
                        msg["Subject"] = subject
                        msg.attach(MIMEText(html_body, "html"))

                        # แปลง Base64 สำหรับ Gmail API
                        raw_msg = base64.urlsafe_b64encode(
                            msg.as_bytes()
                        ).decode()
                        payload = {"raw": raw_msg}

                        # สั่งส่งผ่าน Gmail API (ข้อความจะถูกส่งไปถึงทั้งผู้รับ Gmail และ Outlook)
                        service.users().messages().send(
                            userId="me", body=payload
                        ).execute()

                        success_count += 1
                        progress_bar.progress(
                            (idx + 1) / len(selected_targets)
                        )
                        status_text.text(
                            f"⏳ กำลังส่งอีเมล ({idx + 1}/{len(selected_targets)}): {to_email}"
                        )

                    st.success(
                        f"✅ ส่งอีเมลสำเร็จทั้งหมด {success_count} รายการ เรียบร้อยแล้วค่ะ!"
                    )
                except Exception as e:
                    st.error(
                        f"❌ เกิดข้อผิดพลาดในการส่งอีเมลด้วย Gmail API: {str(e)}"
                    )
