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

# DATA TEMPLATES FOR MEDIA
MEDIA_FOLDERS = {
    "The 20": {
        "title": "The 20",
        "subject": "[Plan B Media] OUTDOOR TRENDS: สื่อใหม่ล่าสุด \"The 20\" สัมผัสประสบการณ์ใหม่กับ DOOH ที่ยาวที่สุดในโลก",
        "detail": """เรียน {{Greeting Name}}<br><br>
{AI_PITCH}<br><br>
สวัสดีค่ะ {{Sale name}} ขอแนะนำสื่อ The 20 สื่อดิจิทัลใหม่ล่าสุด จาก Plan B เพื่อเฉลิมฉลองครบรอบ 20 ปีของเรา โดยสื่อนี้ได้พลิกโฉม ป้ายโฆษณา Serie Poles เดิม ให้กลายเป็น จอ LED กว่า 74 จอ ที่เรียงรายตลอดเส้นทางยาวกว่า 2.5 กม. บนทางด่วนพิเศษเฉลิมมหานคร ใจกลาง Prime CBD<br><br>
<div style="text-align: center; margin: 15px 0;">
    <img src="{IMG1}" width="
