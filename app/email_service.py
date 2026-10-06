import os
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from dotenv import load_dotenv

def _send_email_worker(inquiry):
    load_dotenv(override=True)
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME", "madrasfoodiesconsultancy@gmail.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    recipient = os.getenv("NOTIFICATION_RECIPIENT", "madrasfoodiesconsultancy@gmail.com")

    name = inquiry.get("name", "Unknown")
    email = inquiry.get("email", "Not provided")
    phone = inquiry.get("phone", "Not provided") or "Not provided"
    service = inquiry.get("service", "General Inquiry")
    message = inquiry.get("message", "")
    created_at = inquiry.get("created_at") or datetime.now().strftime("%Y-%m-%d %I:%M:%S %p IST")

    subject_raw = f"[Madras Foodies] New Project Enquiry: {name} - {service}"

    # Plain text version
    text_content = f"""
New Project Enquiry Received - Madras Foodies Consultancy
=========================================================

Submission Time: {created_at}

Client Details:
- Full Name: {name}
- Email Address: {email}
- Phone Number: {phone}
- Service Interested In: {service}

Project Details / Message:
---------------------------------------------------------
{message}
---------------------------------------------------------

Sent automatically from Madras Foodies Consultancy web portal.
"""

    # HTML version
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f7f7f5; margin: 0; padding: 24px; color: #111; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 18px; border: 1px solid #e5e5e0; overflow: hidden; }}
    .header {{ background: #0b0b0b; color: #ffffff; padding: 28px; text-align: left; }}
    .header h2 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
    .header p {{ margin: 6px 0 0; color: #aaaaaa; font-size: 13px; }}
    .content {{ padding: 28px; }}
    .meta-box {{ background: #fafaf8; border: 1px solid #ededeb; border-radius: 12px; padding: 18px; margin-bottom: 24px; }}
    .field {{ margin-bottom: 12px; font-size: 14px; }}
    .field:last-child {{ margin-bottom: 0; }}
    .label {{ font-weight: 700; color: #555; display: inline-block; width: 140px; }}
    .value {{ color: #111; }}
    .value a {{ color: #111; text-decoration: underline; font-weight: 600; }}
    .badge {{ display: inline-block; background: #111; color: #fff; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .message-box {{ background: #fdfdfd; border-left: 3px solid #111; padding: 16px 20px; border-radius: 6px; font-size: 14px; line-height: 1.6; color: #222; margin-top: 12px; white-space: pre-wrap; }}
    .footer {{ padding: 20px 28px; background: #fafaf8; border-top: 1px solid #ededeb; font-size: 12px; color: #888; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>New Project Enquiry</h2>
      <p>Received via madrasfoodies.com contact form on {created_at}</p>
    </div>
    <div class="content">
      <div class="meta-box">
        <div class="field"><span class="label">Full Name:</span> <span class="value"><strong>{name}</strong></span></div>
        <div class="field"><span class="label">Email Address:</span> <span class="value"><a href="mailto:{email}">{email}</a></span></div>
        <div class="field"><span class="label">Phone Number:</span> <span class="value"><a href="tel:{phone}">{phone}</a></span></div>
        <div class="field"><span class="label">Service Selected:</span> <span class="value"><span class="badge">{service}</span></span></div>
      </div>

      <h4 style="margin: 0 0 8px; font-size: 15px; color: #111;">Project Details / Message:</h4>
      <div class="message-box">{message}</div>
    </div>
    <div class="footer">
      Madras Foodies Consultancy &bull; Chennai, Tamil Nadu &bull; +91 90428 53189
    </div>
  </div>
</body>
</html>
"""

    if not smtp_password:
        print(f"[EMAIL NOTIFICATION] SMTP_PASSWORD not set in .env. Notification logged:")
        print(f"  To: {recipient}")
        print(f"  Subject: {subject_raw}")
        print(f"  Client: {name} ({email}) | Service: {service}")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject_raw, "utf-8")
        msg["From"] = f"Madras Foodies Web <{smtp_username}>"
        msg["To"] = recipient
        msg["Reply-To"] = email

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, [recipient], msg.as_string())

        print(f"[EMAIL NOTIFICATION SUCCESS] Sent email notification for enquiry from {name} to {recipient}", flush=True)
    except Exception as e:
        print(f"[EMAIL NOTIFICATION ERROR] Could not send email: {type(e).__name__}: {e}", flush=True)


def dispatch_inquiry_email(inquiry):
    """
    Dispatches the email notification asynchronously in a background thread
    so the web request completes in milliseconds with zero latency.
    """
    thread = threading.Thread(target=_send_email_worker, args=(inquiry,), daemon=True)
    thread.start()
