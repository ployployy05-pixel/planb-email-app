import streamlit as st

st.set_page_config(page_title="Plan B Email Generator", layout="wide")

st.title("📧 Plan B Media - Email Card Generator [Credential]")

# Sidebar สำหรับกรอกข้อมูลลูกค้า
st.sidebar.header("📝 ข้อมูลลูกค้า (Client Info)")
client_name = st.sidebar.text_input("ชื่อลูกค้า / ผู้ติดต่อ", "คุณ P")
client_company = st.sidebar.text_input("ชื่อบริษัทลูกค้า", "P")
credential_drive_link = st.sidebar.text_input(
    "ลิงก์ Google Drive Credential", 
    "https://drive.google.com/drive/folders/1cIs047U-1o39IIn_AawS426Jd-bWq12u"
)

# โครงสร้างหน้าเว็บและ HTML แม่แบบเดิมของคุณพลอย
html_content = f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan B Media - Company Credential 2026</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, 'Sarabun', sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 20px;
            color: #333333;
        }}
        .container {{
            max-width: 650px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        .header {{
            background-color: #0b172a;
            color: #ffffff;
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        .header .subtitle {{
            font-size: 11px;
            color: #94a3b8;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .content {{
            padding: 25px;
        }}
        .greeting-card {{
            background-color: #f8fafc;
            border-left: 4px solid #1d4ed8;
            padding: 16px 20px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 25px;
            font-size: 14px;
            line-height: 1.6;
            color: #334155;
        }}
        .section-title {{
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 15px;
        }}
        .services-box {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 25px;
            font-size: 13px;
            line-height: 1.8;
            color: #334155;
        }}
        .showcase-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 25px;
        }}
        .showcase-card {{
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .showcase-card img {{
            width: 100%;
            height: 100px;
            object-fit: cover;
        }}
        .showcase-card-body {{
            padding: 10px;
        }}
        .showcase-card-title {{
            font-size: 12px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
        }}
        .showcase-card-desc {{
            font-size: 11px;
            color: #64748b;
            margin: 0;
        }}
        .btn-cta-drive {{
            display: block;
            width: 100%;
            padding: 14px 0;
            background-color: #2563eb;
            color: #ffffff !important;
            text-align: center;
            text-decoration: none;
            font-size: 14px;
            font-weight: 700;
            border-radius: 8px;
            margin-bottom: 25px;
            box-sizing: border-box;
        }}
        .signature-box {{
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            font-size: 13px;
            color: #475569;
        }}
        .btn-cta-reply {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #1e293b;
            color: #ffffff !important;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            margin: 12px 0;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>Plan•B <span style="font-weight: 300; font-size: 14px;">MEDIA</span></h1>
        <div class="subtitle">COMPANY CREDENTIAL 2026</div>
    </div>

    <div class="content">
        <div class="greeting-card">
            <strong>เรียน {client_name} ({client_company})</strong><br><br>
            สวัสดีค่ะ ขออนุญาตแนะนำตัว ดิฉัน <strong>วิชญาดา (พลอย)</strong> จากบริษัท <strong>Plan B Media</strong> นะคะ<br>
            ทางเราเป็นผู้ให้บริการสื่อโฆษณานอกบ้าน (Out-of-Home Media) แบบครบวงจรที่ครอบคลุมพื้นที่ยุทธศาสตร์สำคัญทั่วประเทศค่ะ
        </div>

        <div class="section-title">
            📌 OUR MEDIA NETWORK & SERVICES (ขอบเขตบริการสื่อโฆษณา)
        </div>

        <div class="services-box">
            📺 <strong>Digital OOH:</strong> จอดิจิทัล CBD & ย่านธุรกิจ &nbsp;&nbsp;|&nbsp;&nbsp; 🖼️ <strong>Classic Billboard:</strong> ป้ายภาพนิ่งขนาดใหญ่<br>
            🛒 <strong>Retail Media:</strong> สื่อในห้าง Central & Retail &nbsp;&nbsp;|&nbsp;&nbsp; 🚌 <strong>Transit Media:</strong> รถเมล์ & ขนส่งมวลชน<br>
            ✈️ <strong>Airport Media:</strong> สื่อสนามบิน &nbsp;&nbsp;|&nbsp;&nbsp; 🌐 <strong>Global Network:</strong> เครือข่ายสื่อต่างประเทศ
        </div>

        <div class="section-title">
            📷 PLAN B MEDIA SHOWCASE (ผลงานสื่อโฆษณาไฮไลต์)
        </div>

        <div class="showcase-grid">
            <div class="showcase-card">
                <img src="https://raw.githubusercontent.com/ployployy05-pixel/planb-email-app/main/central_net_1.jpg" alt="Central Park Showcase">
                <div class="showcase-card-body">
                    <div class="showcase-card-title">Central Park Showcase</div>
                    <p class="showcase-card-desc">ป้ายภาพนิ่งขนาดใหญ่ ทางเข้าเมือง</p>
                </div>
            </div>
            <div class="showcase-card">
                <img src="https://raw.githubusercontent.com/ployployy05-pixel/planb-email-app/main/central_net_2.jpg" alt="Central W360 Network">
                <div class="showcase-card-body">
                    <div class="showcase-card-title">Central W360 Network</div>
                    <p class="showcase-card-desc">จอดิจิทัล Elevator Wrap ในห้าง</p>
                </div>
            </div>
            <div class="showcase-card">
                <img src="https://raw.githubusercontent.com/ployployy05-pixel/planb-email-app/main/Plan%20B%20TV%20Nationwide.jpg" alt="Transit Media">
                <div class="showcase-card-body">
                    <div class="showcase-card-title">Transit Media: Nextopia</div>
                    <p class="showcase-card-desc">สื่อโฆษณาเคลื่อนที่ บนรถเมล์</p>
                </div>
            </div>
        </div>

        <a href="{credential_drive_link}" target="_blank" class="btn-cta-drive">
            📂 คลิกเปิดดู Plan B Company Credential Folder (Google Drive) ➔
        </a>

        <div class="signature-box">
            ขอขอบคุณที่สละเวลาอ่านอีเมลนี้นะคะ เพื่อโอกาสร่วมมือกันในอนาคต พลอยพร้อมให้ข้อมูลเพิ่มเติมและนัดหมายเพื่อนำเสนอผลงานจริงค่ะ<br>
            
            <a href="mailto:wichayada.ph@planbmedia.co.th?subject=Re: Plan B Media Credential" class="btn-cta-reply">
                ✉️ คลิกเพื่อติดต่อนัดหมาย / ตอบกลับอีเมล
            </a>
            <br><br>
            <strong>วิชญาดา (พลอย) | Account Executive</strong><br>
            📞 064-542-4441 | ✉️ wichayada.ph@planbmedia.co.th<br>
            Plan B Media Public Company Limited
        </div>
    </div>
</div>

</body>
</html>
"""

# แสดงผล Preview
st.components.v1.html(html_content, height=1000, scrolling=True)

# กล่องสำหรับ Copy โค้ด
st.subheader("📋 Copy HTML Code สำหรับนำไปใช้ส่งอีเมล")
st.code(html_content, language="html")
