import requests
from django.conf import settings
from django.core.mail import send_mail

# ── SMS OTP (commented out — replaced by email OTP) ──────────────────────────
# def send_sms_otp(mobile, otp):
#     url = "https://www.fast2sms.com/dev/bulkV2"
#     params = {
#         "authorization": settings.FAST2SMS_API_KEY,
#         "variables_values": otp,
#         "route": "otp",
#         "numbers": mobile,
#     }
#     response = requests.get(url, params=params, timeout=15)
#     try:
#         return response.json()
#     except ValueError:
#         return {"return": False, "message": "Invalid response from SMS provider"}


def send_email_otp(email, otp):
    """Send OTP to the given email address. Returns (True, None) or (False, error_message)."""
    try:
        send_mail(
            subject="Your Kisan Acharya OTP 🌾",
            message=f"Your OTP is: {otp}\nIt is valid for 10 minutes. Do not share it with anyone.",
            from_email=None,
            recipient_list=[email],
            html_message=f"""
<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;background:#f9fff9;border-radius:14px;overflow:hidden;border:1px solid #c8e6c9;">
  <div style="background:linear-gradient(135deg,#1b5e20,#2e7d32);padding:24px;text-align:center;">
    <h2 style="color:#fff;margin:0;font-size:1.4rem;">🌾 Kisan Acharya</h2>
    <p style="color:rgba(255,255,255,.8);margin:6px 0 0;font-size:.85rem;">Your One-Time Password</p>
  </div>
  <div style="padding:28px;text-align:center;">
    <p style="color:#444;font-size:.95rem;margin-bottom:20px;">Use the OTP below to verify your identity.</p>
    <div style="background:#e8f5e9;border:2px dashed #4caf50;border-radius:12px;padding:18px;display:inline-block;min-width:180px;">
      <span style="font-size:2.2rem;font-weight:900;letter-spacing:10px;color:#1b5e20;">{otp}</span>
    </div>
    <p style="color:#888;font-size:.8rem;margin-top:18px;">Valid for <strong>10 minutes</strong>. Do not share this OTP with anyone.</p>
  </div>
  <div style="background:#f1f8e9;padding:12px;text-align:center;border-top:1px solid #c8e6c9;">
    <p style="margin:0;font-size:.75rem;color:#aaa;">© 2026 Kisan Acharya — Smart Farming Platform</p>
  </div>
</div>""",
        )
        return True, None
    except Exception as e:
        print(f"[EMAIL OTP ERROR] {e}")
        return False, str(e)
