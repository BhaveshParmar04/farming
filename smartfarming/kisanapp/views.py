from django.shortcuts import render, redirect, get_object_or_404
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .utils import send_sms_otp
from .models import MobileOTP
from .models import FarmerRegistration, MobileOTP
from .forms import FarmerRegistrationForm
from datetime import timedelta
from django.db.models import Q
from .models import *

# ── Login required decorator for farmer session ──────────────────────────────
def farmer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("farmer_id"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper
# Create your views here.

def home(request):
    from .models import FarmerRegistration, GovtScheme, CropListing, ContactMessage
    farmer_id = request.session.get("farmer_id")
    farmer = FarmerRegistration.objects.filter(id=farmer_id).first() if farmer_id else None

    if request.method == "POST":
        name  = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        msg   = request.POST.get("message", "").strip()
        if name and msg:
            ContactMessage.objects.create(name=name, email=email, phone=phone, message=msg, farmer=farmer)
            messages.success(request, "Your message has been sent! We will get back to you soon.")
        else:
            messages.error(request, "Name and message are required.")
        return redirect("home")

    context = {
        "stat_farmers": FarmerRegistration.objects.count(),
        "stat_schemes": GovtScheme.objects.count(),
        "stat_crops":   CropListing.objects.count(),
        "farmer": farmer,
    }
    return render(request, 'index.html', context)

def about(request):
    from .models import FarmerRegistration, GovtScheme
    context = {
        "ab_farmers": FarmerRegistration.objects.count(),
        "ab_schemes": GovtScheme.objects.count(),
    }
    return render(request, 'about.html', context)

import requests
from django.conf import settings
from django.shortcuts import render


def fetch_agriculture_news():
    url = "https://newsapi.org/v2/everything"

    query = (
    '("agriculture" OR "farming" OR "farmer" OR "farmers" OR "crop" OR "mandi" OR '
    '"irrigation" OR "agri technology" OR "crop disease" OR "farm equipment") '
    'AND ("India" OR "Indian") '
    'NOT ("stock market" OR stock OR stocks OR shares OR ipo OR crypto OR '
    '"mutual fund" OR earnings OR "quarter results" OR startup)'
    )

    params = {
        "q": query,
        "searchIn": "title,description",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 24,
        "domains": "thehindubusinessline.com,indianexpress.com,hindustantimes.com,financialexpress.com,business-standard.com",
        "apiKey": settings.NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        print("STATUS:", response.status_code)
        print("RESPONSE:", data)

        if response.status_code == 200 and data.get("status") == "ok":
            articles = data.get("articles", [])

            # Extra server-side filtering for safety
            filtered_articles = []
            blocked_words = [
                "stock", "stocks", "share market", "ipo", "crypto",
                "mutual fund", "earnings", "equity"
            ]

            for article in articles:
                text = " ".join([
                    str(article.get("title", "")),
                    str(article.get("description", "")),
                    str(article.get("content", "")),
                ]).lower()

                if "india" not in text and "indian" not in text:
                    continue

                if any(word in text for word in blocked_words):
                    continue

                filtered_articles.append(article)

            return filtered_articles, None

        return [], data.get("message", "Failed to fetch agriculture news.")

    except requests.RequestException as e:
        return [], str(e)
    

def agriculture_news(request):
    articles, error_message = fetch_agriculture_news()

    # Session me save kar do taaki detail page me use ho sake
    request.session["news_articles"] = articles

    return render(
        request,
        "news.html",
        {
            "articles": articles,
            "error_message": error_message,
        },
    )


def news_details(request, article_id):
    articles = request.session.get("news_articles", [])

    if not articles:
        # agar direct detail page open hua ho bina list page ke
        articles, error_message = fetch_agriculture_news()
        request.session["news_articles"] = articles
    else:
        error_message = None

    if article_id < 0 or article_id >= len(articles):
        return redirect("agriculture_news")

    article = articles[article_id]

    recent_articles = []
    for index, item in enumerate(articles[:5]):
        recent_articles.append({
            "id": index,
            "title": item.get("title"),
            "urlToImage": item.get("urlToImage"),
            "publishedAt": item.get("publishedAt"),
        })

    context = {
        "article": article,
        "recent_articles": recent_articles,
        "error_message": error_message,
    }
    return render(request, "news_details.html", context)

def contact(request):
    from .models import ContactMessage
    farmer_id = request.session.get("farmer_id")
    farmer = None
    if farmer_id:
        farmer = FarmerRegistration.objects.filter(id=farmer_id).first()

    if request.method == "POST":
        name    = request.POST.get("name", "").strip()
        email   = request.POST.get("email", "").strip()
        phone   = request.POST.get("phone", "").strip()
        msg     = request.POST.get("message", "").strip()
        if name and msg:
            ContactMessage.objects.create(
                name=name, email=email, phone=phone,
                message=msg, farmer=farmer
            )
            messages.success(request, "Your message has been sent! We will get back to you soon.")
        else:
            messages.error(request, "Name and message are required.")
        return redirect("home")

    return render(request, 'contact.html', {"farmer": farmer})


@farmer_required
def market_price(request):
    farmer_id = request.session.get("farmer_id")
    farmer = None
    price_data = []
    error_msg = None

    if farmer_id:
        farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
        selected_state = request.GET.get("state", farmer.state)
        selected_district = request.GET.get("district", farmer.district)
    else:
        selected_state = request.GET.get("state", "")
        selected_district = request.GET.get("district", "")

    selected_commodity = request.GET.get("commodity", "")

    # data.gov.in Agmarknet API - register at https://data.gov.in to get free key
    API_KEY = getattr(settings, "AGMARKNET_API_KEY", "")

    if API_KEY and (selected_state or selected_commodity):
        api_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": 100,
        }
        if selected_state:
            params["filters[State]"] = selected_state
        if selected_district:
            params["filters[District]"] = selected_district
        if selected_commodity:
            params["filters[Commodity]"] = selected_commodity

        try:
            resp = requests.get(api_url, params=params, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and data.get("status") == "ok":
                for r in data.get("records", []):
                    try:
                        price_data.append({
                            "state": r.get("State", ""),
                            "district": r.get("District", ""),
                            "market": r.get("Market", ""),
                            "commodity": r.get("Commodity", ""),
                            "variety": r.get("Variety", ""),
                            "min": float(r.get("Min Price", 0)),
                            "max": float(r.get("Max Price", 0)),
                            "avg": float(r.get("Modal Price", 0)),
                            "date": r.get("Arrival Date", ""),
                        })
                    except (ValueError, TypeError):
                        continue
            else:
                error_msg = "API key invalid or limit exceeded."
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
    elif not API_KEY:
        error_msg = "API key not configured. Add AGMARKNET_API_KEY in settings.py"

    # Fallback demo data jyare API key nathi ya data nathi
    if not price_data:
        demo_state = selected_state or "Gujarat"
        demo_district = selected_district or "Ahmedabad"
        price_data = [
            {"state": demo_state, "district": demo_district, "market": f"{demo_district} APMC", "commodity": "Tomato", "variety": "Local", "min": 800, "max": 1400, "avg": 1100, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"{demo_district} APMC", "commodity": "Onion", "variety": "Red", "min": 600, "max": 1200, "avg": 900, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"{demo_district} APMC", "commodity": "Potato", "variety": "Desi", "min": 400, "max": 900, "avg": 650, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"{demo_district} APMC", "commodity": "Wheat", "variety": "Lokwan", "min": 2100, "max": 2500, "avg": 2300, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"Nearby Mandi", "commodity": "Cotton", "variety": "Shankar-6", "min": 6200, "max": 7100, "avg": 6650, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"Nearby Mandi", "commodity": "Groundnut", "variety": "Bold", "min": 5500, "max": 6200, "avg": 5850, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"{demo_district} Grain Market", "commodity": "Maize", "variety": "Yellow", "min": 1800, "max": 2200, "avg": 2000, "date": "23/03/2026"},
            {"state": demo_state, "district": demo_district, "market": f"{demo_district} Grain Market", "commodity": "Rice", "variety": "Basmati", "min": 3200, "max": 4500, "avg": 3850, "date": "23/03/2026"},
        ]
        if not error_msg:
            error_msg = "Demo data shown. Add AGMARKNET_API_KEY in settings.py for live prices."

    import json
    context = {
        "farmer": farmer,
        "price_data_json": json.dumps(price_data),
        "price_data": price_data,
        "selected_state": selected_state,
        "selected_district": selected_district,
        "selected_commodity": selected_commodity,
        "error_msg": error_msg,
        "total": len(price_data),
    }
    return render(request, "market_price.html", context)

def register(request):
    if request.method == "POST":
        form = FarmerRegistrationForm(request.POST)

        mobile = request.POST.get("mobile", "").strip()

        # Check OTP verification before saving
        otp_record = MobileOTP.objects.filter(
            mobile=mobile,
            is_verified=True
        ).order_by("-created_at").first()

        if not otp_record:
            messages.error(request, "Please verify your mobile number first.")
            return render(request, "register.html", {"form": form})

        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.mobile_verified = True
            farmer.save()

            # Send welcome email
            if farmer.email:
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        subject="Welcome to Kisan Acharya 🌾 — Smart Farming Platform",
                        message="",
                        from_email=None,
                        recipient_list=[farmer.email],
                        html_message=f"""
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f9fff9;border-radius:16px;overflow:hidden;border:1px solid #c8e6c9;">
  <div style="background:linear-gradient(135deg,#1b5e20,#2e7d32);padding:32px 28px;text-align:center;">
    <h1 style="color:#fff;margin:0;font-size:1.8rem;">🌾 Welcome to Kisan Acharya!</h1>
    <p style="color:rgba(255,255,255,.85);margin:8px 0 0;font-size:.95rem;">Smart Farming Platform for Indian Farmers</p>
  </div>
  <div style="padding:28px;">
    <p style="font-size:1rem;color:#1a4f1a;">Dear <strong>{farmer.full_name}</strong>,</p>
    <p style="color:#444;line-height:1.7;">Thank you for registering on <strong>Kisan Acharya</strong>! You are now part of a growing community of smart farmers across India.</p>
    <div style="background:#e8f5e9;border-radius:12px;padding:18px;margin:20px 0;">
      <p style="margin:0 0 10px;font-weight:700;color:#1b5e20;">What you can do on Kisan Acharya:</p>
      <ul style="margin:0;padding-left:20px;color:#2e7d32;line-height:2;">
        <li>🗺️ Add and manage your lands</li>
        <li>🤖 Get AI-powered crop suggestions</li>
        <li>🏛️ Explore government schemes</li>
        <li>📈 Check live market prices</li>
        <li>🛒 Sell crops directly to buyers</li>
      </ul>
    </div>
    <div style="text-align:center;margin:24px 0;">
      <a href="https://farming-41nr.onrender.com" style="background:linear-gradient(135deg,#1b5e20,#2e7d32);color:#fff;padding:14px 32px;border-radius:30px;text-decoration:none;font-weight:700;font-size:1rem;">
        🌾 Go to Kisan Acharya
      </a>
    </div>
    <p style="color:#888;font-size:.82rem;text-align:center;margin:0;">If you have any questions, contact us at <a href="mailto:savajakhil12@gmail.com" style="color:#2e7d32;">savajakhil12@gmail.com</a></p>
  </div>
  <div style="background:#f1f8e9;padding:14px;text-align:center;border-top:1px solid #c8e6c9;">
    <p style="margin:0;font-size:.78rem;color:#888;">© 2026 Kisan Acharya — Smart Farming Platform | Gujarat, India</p>
  </div>
</div>""",
                    )
                except Exception as e:
                    print(f"EMAIL ERROR: {e}")
                    pass  # Email fail thay to registration rok nahi

            # Optional: clean used OTPs for this mobile
            MobileOTP.objects.filter(mobile=mobile).delete()

            messages.success(request, "Registration successful.")
            return redirect("home")

    else:
        form = FarmerRegistrationForm()

    return render(request, "register.html", {"form": form})

@require_POST
def send_otp(request):

    mobile = request.POST.get("mobile", "").strip()

    if not mobile.isdigit() or len(mobile) != 10:
        return JsonResponse({"success": False, "message": "Invalid mobile number."})

    # delete previous OTP
    MobileOTP.objects.filter(mobile=mobile).delete()

    otp = str(random.randint(100000, 999999))

    MobileOTP.objects.create(
        mobile=mobile,
        otp=otp,
        expires_at=timezone.now() + timezone.timedelta(minutes=2)
    )
    # testing
    print(f"OTP for {mobile} is: {otp}")
    
    return JsonResponse({
        "success": True,
        "message": "OTP sent successfully. Check terminal."
    })
    # send OTP using Fast2SMS
    # sms_response = send_sms_otp(mobile, otp)
    # print("SMS Response:", sms_response)  # Debugging line

    # if sms_response.get("return"):
    #     return JsonResponse({
    #         "success": True,
    #         "message": "OTP sent successfully"
    #     })
    # else:
    #     return JsonResponse({
    #         "success": False,
    #         "message": "Failed to send OTP"
    #     })  

@require_POST
def verify_otp(request):
    mobile = request.POST.get("mobile", "").strip()
    otp = request.POST.get("otp", "").strip()

    otp_record = MobileOTP.objects.filter(
        mobile=mobile,
        otp=otp,
        is_verified=False
    ).order_by("-created_at").first()

    if not otp_record:
        return JsonResponse({"success": False, "message": "Invalid OTP."})

    if otp_record.is_expired():
        return JsonResponse({"success": False, "message": "OTP expired."})

    otp_record.is_verified = True
    otp_record.save()

    return JsonResponse({"success": True, "message": "OTP verified successfully."})

@farmer_required
def farming_guide(request):
    farmer_id = request.session.get("farmer_id")
    farmer = None
    lands = []

    if farmer_id:
        farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
        lands = list(farmer.lands.all().order_by("-created_at"))

    return render(request, 'farming_guide.html', {
        "farmer": farmer,
        "lands": lands,
    })


@farmer_required
def save_crop_plan(request):
    """AJAX: save selected crops for a land and generate activity schedule."""
    if request.method != "POST":
        return JsonResponse({"success": False})
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return JsonResponse({"success": False, "message": "Login required."})

    from .utils import generate_crop_activities
    from datetime import date

    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    land_id = request.POST.get("land_id")
    crops = request.POST.getlist("crops")  # list of crop names

    if not land_id or not crops:
        return JsonResponse({"success": False, "message": "Land and crops required."})

    land = get_object_or_404(FarmerLand, id=land_id, farmer=farmer)

    total = 0
    for crop_name in crops:
        total += generate_crop_activities(farmer, land, crop_name, date.today())

    return JsonResponse({
        "success": True,
        "message": f"✅ {total} activities scheduled for {', '.join(crops)} on {land.land_name}!"
    })

@farmer_required
def ai_assistant(request):
    return render(request, 'ai_assistant.html')


@require_POST
def ai_chat(request):
    """AJAX: Real OpenAI chat for farming assistant."""
    from openai import OpenAI
    from django.conf import settings
    import base64, json as _json

    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        return JsonResponse({"success": False, "message": "OpenAI API key not configured."})

    client = OpenAI(api_key=api_key)

    message = request.POST.get("message", "").strip()
    lang = request.POST.get("lang", "en")
    image_file = request.FILES.get("image")

    lang_map = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}
    lang_name = lang_map.get(lang, "English")

    system_prompt = f"""You are SmartFarm AI, an expert Indian agricultural assistant.
Always respond in {lang_name} language only.
Help farmers with: crop selection, soil health, fertilizers, pest control, irrigation, crop diseases, government schemes, market prices.
Keep responses concise, practical and farmer-friendly.
If analyzing a crop image, identify: disease name, cause, treatment, prevention."""

    try:
        if image_file:
            # Vision — image + optional text
            img_bytes = image_file.read()
            b64 = base64.b64encode(img_bytes).decode()
            ext = image_file.name.split(".")[-1].lower()
            mime = "image/jpeg" if ext in ["jpg","jpeg"] else "image/png" if ext == "png" else "image/jpeg"

            user_content = [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": message or "Analyze this crop image and identify any disease, cause, treatment and prevention tips."}
            ]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=600,
            )
        else:
            # Text only
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
            )

        reply = response.choices[0].message.content.strip()
        return JsonResponse({"success": True, "reply": reply})

    except Exception as e:
        err = str(e)
        if "429" in err:
            return JsonResponse({"success": False, "message": "API quota exceeded. Please try again later."})
        return JsonResponse({"success": False, "message": f"Error: {err}"})

def add_land(request):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return redirect("login")

    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    lands = farmer.lands.all().order_by("-created_at")

    if request.method == "POST":
        if lands.count() >= 10:
            messages.error(request, "Maximum 10 lands allowed.")
            return redirect("add_land")

        land_name = request.POST.get("land_name", "").strip()
        land_area = request.POST.get("land_area", "").strip()
        water_supply = request.POST.get("water_supply", "Borewell")
        soil_method = request.POST.get("soil_method", "upload")

        if not land_name or not land_area:
            messages.error(request, "Land name and area are required.")
            return redirect("add_land")

        # Soil data validation — upload or manual required
        if soil_method == "upload" and not request.FILES.get("soil_report"):
            messages.error(request, "Please upload a soil report, or switch to manual entry.")
            return redirect("add_land")

        if soil_method == "upload" and request.FILES.get("soil_report"):
            uploaded_file = request.FILES["soil_report"]
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext == "pdf":
                try:
                    from pypdf import PdfReader
                    import io as _io
                    import re
                    file_bytes = uploaded_file.read()
                    reader = PdfReader(_io.BytesIO(file_bytes))
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                    pdf_lower = pdf_text.lower()
                    soil_keywords = [
                        r"\bnitrogen\b", r"\bphosphorus\b", r"\bpotassium\b",
                        r"\borganic carbon\b", r"\belectrical conductivity\b",
                        r"\bsoil report\b", r"\bsoil health\b", r"\bsoil test\b",
                        r"\bsoil sample\b", r"\bph value\b", r"\bsoil ph\b",
                        r"\bzinc\b", r"\bsulphur\b", r"\bmanganese\b",
                        r"\bमिट्टी\b", r"\bkrishi vigyan\b", r"\bsoil fertility\b",
                    ]
                    has_soil_data = any(re.search(kw, pdf_lower) for kw in soil_keywords)
                    if not has_soil_data:
                        messages.error(request, "આ PDF માં soil report data મળ્યો નથી. કૃપા કરીને સાચો Soil Testing Report PDF upload કરો.")
                        return redirect("add_land")
                    # Reset file pointer for saving
                    from django.core.files.uploadedfile import InMemoryUploadedFile
                    import sys
                    uploaded_file = InMemoryUploadedFile(
                        _io.BytesIO(file_bytes), 'soil_report',
                        uploaded_file.name, uploaded_file.content_type,
                        sys.getsizeof(_io.BytesIO(file_bytes)), None
                    )
                    request.FILES['soil_report'] = uploaded_file
                except Exception:
                    messages.error(request, "PDF read કરવામાં error આવ્યો. બીજો PDF try કરો.")
                    return redirect("add_land")

        if soil_method == "manual":
            ph = request.POST.get("ph", "").strip()
            n  = request.POST.get("n", "").strip()
            p  = request.POST.get("p", "").strip()
            k  = request.POST.get("k", "").strip()
            if not any([ph, n, p, k]):
                messages.error(request, "Please enter at least one soil value (pH, N, P, or K).")
                return redirect("add_land")

        land = FarmerLand(
            farmer=farmer,
            land_name=land_name,
            land_area=land_area,
            water_supply=water_supply,
            soil_method=soil_method,
        )

        if soil_method == "upload" and request.FILES.get("soil_report"):
            land.soil_report = request.FILES["soil_report"]
        elif soil_method == "manual":
            land.ph = request.POST.get("ph", "")
            land.ec = request.POST.get("ec", "")
            land.organic_carbon = request.POST.get("oc", "")
            land.nitrogen = request.POST.get("n", "")
            land.phosphorus = request.POST.get("p", "")
            land.potassium = request.POST.get("k", "")
            land.sulphur = request.POST.get("s", "")
            land.zinc = request.POST.get("zn", "")
            land.iron = request.POST.get("fe", "")
            land.manganese = request.POST.get("mn", "")
            land.copper = request.POST.get("cu", "")
            land.boron = request.POST.get("b", "")

        land.save()
        messages.success(request, f"'{land_name}' added successfully.")
        return redirect("add_land")

    return render(request, "add_land.html", {"lands": lands, "farmer": farmer})


def edit_land(request, land_id):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return redirect("login")

    land = get_object_or_404(FarmerLand, id=land_id, farmer_id=farmer_id)

    if request.method == "POST":
        land.land_name = request.POST.get("land_name", land.land_name).strip()
        land.land_area = request.POST.get("land_area", land.land_area).strip()
        land.water_supply = request.POST.get("water_supply", land.water_supply)
        land.soil_method = request.POST.get("soil_method", land.soil_method)

        if land.soil_method == "upload" and request.FILES.get("soil_report"):
            land.soil_report = request.FILES["soil_report"]
        elif land.soil_method == "manual":
            land.ph = request.POST.get("ph", "")
            land.ec = request.POST.get("ec", "")
            land.organic_carbon = request.POST.get("oc", "")
            land.nitrogen = request.POST.get("n", "")
            land.phosphorus = request.POST.get("p", "")
            land.potassium = request.POST.get("k", "")
            land.sulphur = request.POST.get("s", "")
            land.zinc = request.POST.get("zn", "")
            land.iron = request.POST.get("fe", "")
            land.manganese = request.POST.get("mn", "")
            land.copper = request.POST.get("cu", "")
            land.boron = request.POST.get("b", "")

        land.save()
        messages.success(request, f"'{land.land_name}' updated successfully.")
        return redirect("add_land")

    return redirect("add_land")


def delete_land(request, land_id):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return redirect("login")

    land = get_object_or_404(FarmerLand, id=land_id, farmer_id=farmer_id)
    land.delete()
    messages.success(request, "Land deleted successfully.")
    return redirect("add_land")


def download_soil_form(request):
    """Generate a printable soil testing request form PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from django.http import HttpResponse
    import io

    farmer_id = request.session.get("farmer_id")
    farmer_name = ""
    farmer_mobile = ""
    farmer_location = ""
    if farmer_id:
        try:
            farmer = FarmerRegistration.objects.get(id=farmer_id)
            farmer_name = farmer.full_name
            farmer_mobile = farmer.mobile
            farmer_location = f"{farmer.village}, {farmer.taluka}, {farmer.district}, {farmer.state}"
        except Exception:
            pass

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Title'],
                                  fontSize=18, textColor=colors.HexColor('#1b5e20'),
                                  spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'],
                                     fontSize=11, textColor=colors.HexColor('#2e7d32'),
                                     spaceAfter=4, alignment=TA_CENTER)
    heading_style = ParagraphStyle('heading', parent=styles['Normal'],
                                    fontSize=12, textColor=colors.HexColor('#1b5e20'),
                                    spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('normal', parent=styles['Normal'],
                                   fontSize=10, spaceAfter=4)
    note_style = ParagraphStyle('note', parent=styles['Normal'],
                                 fontSize=9, textColor=colors.HexColor('#555555'),
                                 spaceAfter=3)

    story = []

    # Header
    story.append(Paragraph("🌾 Kisan Acharya — Smart Farming Platform", title_style))
    story.append(Paragraph("Soil Testing Request Form", subtitle_style))
    story.append(Paragraph("Take this form to your nearest Soil Testing Centre", subtitle_style))
    story.append(Spacer(1, 0.4*cm))

    # Divider
    story.append(Table([['']], colWidths=[17*cm],
                        style=[('LINEABOVE', (0,0), (-1,0), 1.5, colors.HexColor('#2e7d32'))]))
    story.append(Spacer(1, 0.3*cm))

    # Farmer Info
    story.append(Paragraph("FARMER INFORMATION", heading_style))
    farmer_data = [
        ['Farmer Name:', farmer_name or '___________________________',
         'Mobile:', farmer_mobile or '___________________'],
        ['Location:', farmer_location or '___________________________',
         'Date:', '___________________'],
        ['Land Name:', '___________________________',
         'Land Area:', '___________ acres/bigha'],
    ]
    farmer_table = Table(farmer_data, colWidths=[3.5*cm, 5.5*cm, 2.5*cm, 5.5*cm])
    farmer_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#1b5e20')),
        ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor('#1b5e20')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(farmer_table)
    story.append(Spacer(1, 0.3*cm))

    # Soil Parameters Table
    story.append(Paragraph("SOIL TEST PARAMETERS (To be filled by Testing Centre)", heading_style))

    params = [
        ['Parameter', 'Unit', 'Result', 'Status\n(Low/Medium/High)', 'Recommendation'],
        ['pH (Soil Reaction)', '—', '', '', ''],
        ['EC (Electrical Conductivity)', 'dS/m', '', '', ''],
        ['Organic Carbon (OC)', '%', '', '', ''],
        ['Nitrogen (N)', 'kg/ha', '', '', ''],
        ['Phosphorus (P)', 'kg/ha', '', '', ''],
        ['Potassium (K)', 'kg/ha', '', '', ''],
        ['Sulphur (S)', 'ppm', '', '', ''],
        ['Zinc (Zn)', 'ppm', '', '', ''],
        ['Iron (Fe)', 'ppm', '', '', ''],
        ['Manganese (Mn)', 'ppm', '', '', ''],
        ['Copper (Cu)', 'ppm', '', '', ''],
        ['Boron (B)', 'ppm', '', '', ''],
    ]

    param_table = Table(params, colWidths=[5*cm, 2*cm, 2.5*cm, 3.5*cm, 4*cm])
    param_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1b5e20')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        # Data rows
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f1f8e9'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#c8e6c9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 0.4*cm))

    # Centre Stamp & Signature
    story.append(Paragraph("TESTING CENTRE DETAILS", heading_style))
    centre_data = [
        ['Centre Name:', '________________________________',
         'Centre Stamp:', ''],
        ['Address:', '________________________________', '', ''],
        ['Technician Name:', '________________',
         'Signature:', '________________'],
        ['Date of Testing:', '________________',
         'Report Date:', '________________'],
    ]
    centre_table = Table(centre_data, colWidths=[3.5*cm, 5.5*cm, 3*cm, 5*cm])
    centre_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#1b5e20')),
        ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor('#1b5e20')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('SPAN', (3,0), (3,1)),
        ('BOX', (3,0), (3,1), 1, colors.HexColor('#c8e6c9')),
    ]))
    story.append(centre_table)
    story.append(Spacer(1, 0.3*cm))

    # Instructions
    story.append(Paragraph("INSTRUCTIONS FOR FARMER", heading_style))
    instructions = [
        "1. Take a soil sample from your land (0-15 cm depth) — collect from 5-6 different spots and mix well.",
        "2. Take approx. 500 grams of mixed soil in a clean bag.",
        "3. Bring this form and soil sample to your nearest Soil Testing Centre (Krishi Vigyan Kendra / APMC / Agriculture Department).",
        "4. After getting the report, enter the values in Kisan Acharya website under 'Add Land → Manual Soil Data'.",
        "5. Our AI will then give you personalized crop recommendations based on your soil data.",
    ]
    for inst in instructions:
        story.append(Paragraph(inst, note_style))

    story.append(Spacer(1, 0.3*cm))

    # Footer
    story.append(Table([['']], colWidths=[17*cm],
                        style=[('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#c8e6c9'))]))
    story.append(Paragraph(
        "Kisan Acharya — Smart Farming Platform | For help: support@Kisan Acharya.in | www.Kisan Acharya.in",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8,
                       textColor=colors.HexColor('#888888'), alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Kisan Acharya_Soil_Testing_Form.pdf"'
    return response

def mark_activity_done(request, activity_id):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return redirect("login")
    activity = get_object_or_404(CropActivity, id=activity_id, farmer_id=farmer_id)
    activity.status = request.POST.get("status", "done")
    activity.save()
    return redirect("notifications")


def notification_count(request):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return JsonResponse({"count": 0})
    count = Notification.objects.filter(farmer_id=farmer_id, is_read=False).count()
    return JsonResponse({"count": count})


def notifications_api(request):
    """Returns recent notifications + upcoming crop activities for navbar popup."""
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return JsonResponse({"items": [], "count": 0})
    from django.utils import timezone
    now   = timezone.now()
    today = now.date()
    cutoff_12h  = now - timezone.timedelta(hours=12)
    next_15days = today + timezone.timedelta(days=15)

    icon_map = {
        "watering":   "fa-tint",
        "fertilizer": "fa-flask",
        "pesticide":  "fa-bug",
        "harvesting": "fa-tractor",
        "sowing":     "fa-seedling",
        "general":    "fa-info-circle",
    }

    items = []

    # 1. Bell popup — only last 12 hours notifications
    notifs = Notification.objects.filter(
        farmer_id=farmer_id,
        is_read=False,
        created_at__gte=cutoff_12h,
    ).select_related("land").order_by("-created_at")[:8]

    for n in notifs:
        diff = now - n.created_at
        s = int(diff.total_seconds())
        if s < 60:      time_str = "just now"
        elif s < 3600:  m = s//60;   time_str = f"{m} min ago"
        elif s < 86400: h = s//3600; time_str = f"{h} hour ago"
        else:           d = s//86400; time_str = f"{d} day ago"
        items.append({
            "land":    n.land.land_name if n.land else "",
            "crop":    n.crop_name,
            "message": n.title,
            "time":    time_str,
            "icon":    icon_map.get(n.notif_type, "fa-info-circle"),
            "overdue": False,
            "unread":  True,
        })

    # 2. Upcoming CropActivities (unread only, next 15 days)
    activities = CropActivity.objects.filter(
        farmer_id=farmer_id,
        status="pending",
        is_read=False,
        due_date__gte=today,
        due_date__lte=next_15days
    ).select_related("land").order_by("due_date")[:8]

    for a in activities:
        days_left = (a.due_date - today).days
        if days_left == 0:   time_str = "Today"
        elif days_left == 1: time_str = "Tomorrow"
        else:                time_str = f"In {days_left} days"
        items.append({
            "land":    a.land.land_name if a.land else "",
            "crop":    a.crop_name,
            "message": a.title,
            "time":    time_str,
            "icon":    icon_map.get(a.activity_type, "fa-seedling"),
            "overdue": False,
            "unread":  True,
        })

    # 3. Overdue activities (unread only, last 7 days only)
    overdue = CropActivity.objects.filter(
        farmer_id=farmer_id,
        status="pending",
        is_read=False,
        due_date__lt=today,
        due_date__gte=today - timezone.timedelta(days=7)
    ).select_related("land").order_by("-due_date")[:3]

    for a in overdue:
        days_ago = (today - a.due_date).days
        items.append({
            "land":    a.land.land_name if a.land else "",
            "crop":    a.crop_name,
            "message": f"⚠️ {a.title}",
            "time":    f"{days_ago} day{'s' if days_ago>1 else ''} overdue",
            "icon":    icon_map.get(a.activity_type, "fa-exclamation-circle"),
            "overdue": True,
            "unread":  True,
        })

    # Total unread count — only last 12h notifications
    unread_count = (
        Notification.objects.filter(farmer_id=farmer_id, is_read=False, created_at__gte=cutoff_12h).count() +
        CropActivity.objects.filter(farmer_id=farmer_id, status="pending", is_read=False, due_date__gte=today, due_date__lte=next_15days).count() +
        CropActivity.objects.filter(farmer_id=farmer_id, status="pending", is_read=False, due_date__lt=today, due_date__gte=today - timezone.timedelta(days=7)).count()
    )

    # Bell click → mark all as read → popup ma thi jase, View All page par haji dikhse
    if request.GET.get("mark_read") == "1":
        Notification.objects.filter(farmer_id=farmer_id, is_read=False).update(is_read=True)
        CropActivity.objects.filter(farmer_id=farmer_id, status="pending", is_read=False).update(is_read=True)
        return JsonResponse({"items": items[:10], "count": 0})

    return JsonResponse({"items": items[:10], "count": unread_count})


@farmer_required
def notifications(request):
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    from django.utils import timezone
    from collections import defaultdict
    today = timezone.now().date()
    one_year_ago = today - timezone.timedelta(days=365)

    # All notifications last 1 year — grouped by land
    all_notifs = Notification.objects.filter(
        farmer=farmer,
        created_at__date__gte=one_year_ago,
    ).select_related("land").order_by("-created_at")

    # Group by land name
    land_notifs = defaultdict(list)
    for n in all_notifs:
        land_name = n.land.land_name if n.land else "General"
        land_notifs[land_name].append(n)

    # Pending crop activities grouped by land
    activities = CropActivity.objects.filter(
        farmer=farmer, status="pending"
    ).select_related("land").order_by("due_date")

    land_activities = defaultdict(lambda: {"urgent": [], "upcoming": []})
    for act in activities:
        key = act.land.land_name
        if act.due_date <= today:
            land_activities[key]["urgent"].append(act)
        else:
            land_activities[key]["upcoming"].append(act)

    # Govt scheme notifications
    scheme_notifs = SchemeNotification.objects.filter(
        Q(farmer=farmer) | Q(farmer__isnull=True)
    ).select_related("scheme").order_by("-created_at")[:20]

    # Mark all as read
    Notification.objects.filter(farmer=farmer, is_read=False).update(is_read=True)
    CropActivity.objects.filter(farmer=farmer, status="pending", is_read=False).update(is_read=True)
    SchemeNotification.objects.filter(
        Q(farmer=farmer) | Q(farmer__isnull=True), is_read=False
    ).update(is_read=True)

    return render(request, 'notifications.html', {
        "farmer": farmer,
        "land_notifs": dict(land_notifs),
        "land_activities": dict(land_activities),
        "scheme_notifs": scheme_notifs,
        "today": today,
    })


def _generate_land_login_notifications(farmer):
    """On login: create notifications for today's and tomorrow's pending crop activities."""
    from django.utils import timezone
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)

    activities = CropActivity.objects.filter(
        farmer=farmer,
        status="pending",
        due_date__in=[today, tomorrow],
    ).select_related("land")

    for activity in activities:
        # Avoid duplicate notification for same activity today
        already = Notification.objects.filter(
            farmer=farmer,
            land=activity.land,
            crop_name=activity.crop_name,
            title__contains=activity.title,
            created_at__date=today,
        ).exists()
        if already:
            continue

        due_label = "⏰ આજે" if activity.due_date == today else "📅 કાલે"
        Notification.objects.create(
            farmer=farmer,
            land=activity.land,
            crop_name=activity.crop_name,
            notif_type=activity.activity_type,
            title=f"{due_label}: {activity.title}",
            message=f"{activity.land.land_name} – {activity.crop_name}: {activity.message}",
        )


def login(request):
     return render(request, "login.html")

def send_login_otp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    mobile = request.POST.get("mobile", "").strip()

    if not mobile:
        return JsonResponse({"success": False, "message": "Please enter mobile number"})

    if not mobile.isdigit():
        return JsonResponse({"success": False, "message": "Mobile number must contain only digits"})

    if len(mobile) != 10:
        return JsonResponse({"success": False, "message": "Mobile number must be exactly 10 digits"})

    # check user exists or not
    farmer = FarmerRegistration.objects.filter(mobile=mobile).first()
    if not farmer:
        return JsonResponse({"success": False, "message": "User does not exist. Please register first."})

    # delete old unverified OTPs for this mobile
    MobileOTP.objects.filter(mobile=mobile, is_verified=False).delete()

    otp = str(random.randint(100000, 999999))

    try:
        MobileOTP.objects.create(
            mobile=mobile,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=2)
        )
    except Exception as e:
        # debug mode, show real error cause; remove in production
        return JsonResponse({"success": False, "message": f"Could not save OTP: {e}"}, status=500)

    # demo/testing only
    # production me SMS API use karna
    return JsonResponse({
        "success": True,
        "message": "OTP sent successfully",
        "demo_otp": otp
    })


def verify_login_otp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"})

    mobile = request.POST.get("mobile", "").strip()
    otp = request.POST.get("otp", "").strip()

    if not mobile:
        return JsonResponse({"success": False, "message": "Please enter mobile number"})

    if not mobile.isdigit() or len(mobile) != 10:
        return JsonResponse({"success": False, "message": "Enter a valid 10 digit mobile number"})

    if not otp:
        return JsonResponse({"success": False, "message": "Please enter OTP"})

    if not otp.isdigit() or len(otp) != 6:
        return JsonResponse({"success": False, "message": "OTP must be exactly 6 digits"})

    # check user exists
    farmer = FarmerRegistration.objects.filter(mobile=mobile).first()
    if not farmer:
        return JsonResponse({"success": False, "message": "User does not exist. Please register first."})

    otp_obj = MobileOTP.objects.filter(
        mobile=mobile,
        otp=otp,
        is_verified=False
    ).order_by("-created_at").first()

    if not otp_obj:
        return JsonResponse({"success": False, "message": "Invalid OTP"})

    if otp_obj.is_expired():
        return JsonResponse({"success": False, "message": "OTP has expired. Please resend OTP."})

    otp_obj.is_verified = True
    otp_obj.save()

    # mark mobile verified
    farmer.mobile_verified = True
    farmer.save()

    # session login
    request.session["farmer_id"] = farmer.id
    request.session["farmer_name"] = farmer.full_name
    request.session["farmer_mobile"] = farmer.mobile

    return JsonResponse({
        "success": True,
        "message": "Login successful",
        "redirect_url": "/"
    })


def logout(request):
    request.session.flush()
    return redirect("login")

@farmer_required
def profile(request):
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    lands = farmer.lands.all().order_by("-created_at")
    return render(request, "profile.html", {"farmer": farmer, "lands": lands})


@farmer_required
def update_profile(request):
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)

    if request.method == "POST":
        farmer.full_name = request.POST.get("full_name", farmer.full_name).strip()
        farmer.land_record = request.POST.get("land_record", farmer.land_record).strip()
        farmer.state = request.POST.get("state", farmer.state).strip()
        farmer.district = request.POST.get("district", farmer.district).strip()
        farmer.taluka = request.POST.get("taluka", farmer.taluka).strip()
        farmer.village = request.POST.get("village", farmer.village).strip()
        farmer.save()
        request.session["farmer_name"] = farmer.full_name
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return redirect("profile")

@farmer_required
def crops_marketplace(request):
    farmer_id = request.session.get("farmer_id")

    if request.method == "POST":
        if not farmer_id:
            messages.error(request, "Please login to sell crops.")
            return redirect("login")

        farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
        name = request.POST.get("name", "").strip()
        crop_type = request.POST.get("type", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        unit = request.POST.get("unit", "kg")
        price = request.POST.get("price", "").strip()

        if not all([name, crop_type, quantity, price]):
            messages.error(request, "Please fill all required fields.")
            return redirect("crops_marketplace")

        crop = CropListing.objects.create(
            farmer=farmer,
            name=name,
            type=crop_type,
            quantity=quantity,
            unit=unit,
            price=price,
            video=request.FILES.get("video"),
        )

        images = request.FILES.getlist("images")[:5]
        for img in images:
            CropImage.objects.create(crop=crop, image=img)

        messages.success(request, f"'{name}' listed successfully.")
        return redirect("crops_marketplace")

    # ── Nearby filter ──────────────────────────────────────────────────────
    current_farmer = None
    if farmer_id:
        current_farmer = FarmerRegistration.objects.filter(id=farmer_id).first()

    base_qs = CropListing.objects.filter(is_active=True).select_related("farmer").prefetch_related("images")

    if current_farmer:
        # Same district first (closest ~50km)
        district_crops = base_qs.filter(
            farmer__district=current_farmer.district,
            farmer__state=current_farmer.state
        ).exclude(farmer=current_farmer).order_by("-created_at")

        # Same state (within ~100-200km)
        state_crops = base_qs.filter(
            farmer__state=current_farmer.state
        ).exclude(
            farmer__district=current_farmer.district
        ).exclude(farmer=current_farmer).order_by("-created_at")

        # Other states
        other_crops = base_qs.exclude(
            farmer__state=current_farmer.state
        ).order_by("-created_at")

        # Own listings — for My Listings tab
        own_crops = base_qs.filter(farmer=current_farmer).order_by("-created_at")

        # Combine: own first (for My Listings), then nearby, then others
        from itertools import chain
        crops = list(chain(own_crops, district_crops, state_crops, other_crops))
        nearby_count = district_crops.count() + state_crops.count()
    else:
        crops = base_qs.order_by("-created_at")
        nearby_count = 0

    return render(request, "crops_marketplace.html", {
        "crops": crops,
        "current_farmer": current_farmer,
        "nearby_count": nearby_count,
    })

@farmer_required
def farming_tools(request):
    farmer_id = request.session.get("farmer_id")

    if request.method == "POST":
        if not farmer_id:
            messages.error(request, "Please login to list tools.")
            return redirect("login")

        farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "").strip()
        price = request.POST.get("price", "").strip()
        condition = request.POST.get("condition", "Good")
        description = request.POST.get("description", "").strip()

        if not all([name, category, price]):
            messages.error(request, "Please fill all required fields.")
            return redirect("farming_tools")

        tool = FarmingTool.objects.create(
            farmer=farmer,
            name=name,
            category=category,
            price=price,
            condition=condition,
            description=description,
            video=request.FILES.get("video"),
        )

        images = request.FILES.getlist("images")[:5]
        for img in images:
            FarmingToolImage.objects.create(tool=tool, image=img)

        messages.success(request, f"'{name}' listed successfully.")
        return redirect("farming_tools")

    # ── Nearby filter ──────────────────────────────────────────────────────
    current_farmer = None
    if farmer_id:
        current_farmer = FarmerRegistration.objects.filter(id=farmer_id).first()

    tools_qs = FarmingTool.objects.filter(is_active=True).select_related("farmer").prefetch_related("images")

    if current_farmer:
        district_tools = tools_qs.filter(
            farmer__district=current_farmer.district,
            farmer__state=current_farmer.state
        ).exclude(farmer=current_farmer).order_by("-created_at")

        state_tools = tools_qs.filter(
            farmer__state=current_farmer.state
        ).exclude(
            farmer__district=current_farmer.district
        ).exclude(farmer=current_farmer).order_by("-created_at")

        other_tools = tools_qs.exclude(
            farmer__state=current_farmer.state
        ).order_by("-created_at")

        own_tools = tools_qs.filter(farmer=current_farmer).order_by("-created_at")

        from itertools import chain
        tools = list(chain(own_tools, district_tools, state_tools, other_tools))
        nearby_tools_count = district_tools.count() + state_tools.count()
    else:
        tools = tools_qs.order_by("-created_at")
        nearby_tools_count = 0

    return render(request, "farming_tools.html", {
        "tools": tools,
        "current_farmer": current_farmer,
        "nearby_count": nearby_tools_count,
    })


@farmer_required
def delete_crop_listing(request, crop_id):
    farmer_id = request.session.get("farmer_id")
    crop = get_object_or_404(CropListing, id=crop_id, farmer_id=farmer_id)
    crop.delete()
    messages.success(request, "Listing deleted successfully.")
    return redirect("crops_marketplace")
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return JsonResponse({"success": False, "message": "Please login first."})
    crop = get_object_or_404(CropListing, id=crop_id, is_active=True)
    if crop.farmer_id == farmer_id:
        return JsonResponse({"success": False, "message": "You cannot buy your own crop."})
    buyer = get_object_or_404(FarmerRegistration, id=farmer_id)
    quantity = request.POST.get("quantity", "").strip()
    message = request.POST.get("message", "").strip()
    if not quantity:
        return JsonResponse({"success": False, "message": "Please enter quantity."})
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid quantity."})
    BuyRequest.objects.create(crop=crop, buyer=buyer, quantity=qty, message=message)
    return JsonResponse({"success": True, "message": f"Buy request sent to {crop.farmer.full_name}!"})


def my_buy_requests(request):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return redirect("login")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    # requests I sent
    sent = BuyRequest.objects.filter(buyer=farmer).select_related("crop", "crop__farmer").order_by("-created_at")
    # requests on my crops
    received = BuyRequest.objects.filter(crop__farmer=farmer).select_related("crop", "buyer").order_by("-created_at")
    return render(request, "buy_requests.html", {"sent": sent, "received": received, "farmer": farmer})


def update_buy_request(request, req_id):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return redirect("login")
    buy_req = get_object_or_404(BuyRequest, id=req_id, crop__farmer_id=farmer_id)
    status = request.POST.get("status")
    if status in ["accepted", "rejected"]:
        buy_req.status = status
        buy_req.save()
    return redirect("my_buy_requests")


# ─────────────────────────────────────────────
#  LOCATION API VIEWS
# ─────────────────────────────────────────────

def location_districts(request):
    """Return districts for a given state."""
    from .location_data import LOCATION_DATA
    state = request.GET.get("state", "")
    districts = sorted(LOCATION_DATA.get(state, {}).keys())
    return JsonResponse({"districts": districts})


def location_talukas(request):
    """Return talukas for a given state + district."""
    from .location_data import LOCATION_DATA
    state = request.GET.get("state", "")
    district = request.GET.get("district", "")
    talukas = sorted((LOCATION_DATA.get(state, {}).get(district, {}) or {}).keys())
    return JsonResponse({"talukas": talukas})


def location_villages(request):
    """Return villages for a given state + district + taluka."""
    from .location_data import LOCATION_DATA
    state = request.GET.get("state", "")
    district = request.GET.get("district", "")
    taluka = request.GET.get("taluka", "")
    villages = sorted(((LOCATION_DATA.get(state, {}).get(district, {}) or {}).get(taluka, [])))
    return JsonResponse({"villages": villages})


def location_states(request):
    """Return all states."""
    from .location_data import LOCATION_DATA
    states = sorted(LOCATION_DATA.keys())
    return JsonResponse({"states": states})


# ─────────────────────────────────────────────
#  BUYER VIEWS
# ─────────────────────────────────────────────

def buyer_register(request):
    if request.method == "POST":
        mobile = request.POST.get("mobile", "").strip()
        otp_record = MobileOTP.objects.filter(mobile=mobile, is_verified=True).order_by("-created_at").first()
        ctx = {"buyer_states": Buyer.STATE_CHOICES, "states": Buyer.STATE_CHOICES, "crop_choices": Buyer.CROP_CHOICES}
        if not otp_record:
            ctx["error"] = "Please verify your mobile number first."
            return render(request, "buyer_register.html", ctx)
        full_name        = request.POST.get("full_name", "").strip()
        company          = request.POST.get("company", "").strip()
        interested_crops = request.POST.get("interested_crops", "").strip()
        notes            = request.POST.get("notes", "").strip()
        locations_json   = request.POST.get("locations_json", "[]").strip()
        import json
        try:
            locations = json.loads(locations_json)
        except Exception:
            locations = []
        if not all([full_name, interested_crops]) or not locations:
            ctx["error"] = "Please fill all required fields and add at least one location."
            return render(request, "buyer_register.html", ctx)
        if Buyer.objects.filter(mobile=mobile).exists():
            ctx["error"] = "Mobile already registered. Please login."
            return render(request, "buyer_register.html", ctx)
        buyer = Buyer.objects.create(
            full_name=full_name, mobile=mobile, mobile_verified=True,
            company=company, locations=locations,
            interested_crops=interested_crops, notes=notes,
        )
        MobileOTP.objects.filter(mobile=mobile).delete()
        request.session["buyer_id"]   = buyer.id
        request.session["buyer_name"] = buyer.full_name
        messages.success(request, "Registration successful!")
        return redirect("buyer_dashboard")
    return render(request, "buyer_register.html", {
        "states": Buyer.STATE_CHOICES,
        "crop_choices": Buyer.CROP_CHOICES,
    })


def buyer_login(request):
    return render(request, "buyer_login.html")


def send_buyer_otp(request):
    if request.method != "POST":
        return JsonResponse({"success": False})
    mobile = request.POST.get("mobile", "").strip()
    if not mobile.isdigit() or len(mobile) != 10:
        return JsonResponse({"success": False, "message": "Invalid mobile number."})
    MobileOTP.objects.filter(mobile=mobile, is_verified=False).delete()
    otp = str(random.randint(100000, 999999))
    MobileOTP.objects.create(mobile=mobile, otp=otp, expires_at=timezone.now() + timedelta(minutes=2))
    print(f"[BUYER OTP] {mobile} → {otp}")
    return JsonResponse({"success": True, "message": "OTP sent.", "demo_otp": otp})


def verify_buyer_login_otp(request):
    if request.method != "POST":
        return JsonResponse({"success": False})
    mobile = request.POST.get("mobile", "").strip()
    otp    = request.POST.get("otp", "").strip()
    try:
        buyer = Buyer.objects.get(mobile=mobile)
    except Buyer.DoesNotExist:
        return JsonResponse({"success": False, "message": "Mobile not registered. Please register first."})
    otp_obj = MobileOTP.objects.filter(mobile=mobile, otp=otp, is_verified=False).order_by("-created_at").first()
    if not otp_obj:
        return JsonResponse({"success": False, "message": "Invalid OTP."})
    if otp_obj.is_expired():
        return JsonResponse({"success": False, "message": "OTP expired."})
    otp_obj.is_verified = True
    otp_obj.save()
    request.session["buyer_id"]   = buyer.id
    request.session["buyer_name"] = buyer.full_name
    return JsonResponse({"success": True, "redirect_url": "/buyer/dashboard/"})


def buyer_dashboard(request):
    buyer_id = request.session.get("buyer_id")
    if not buyer_id:
        return redirect("buyer_login")
    buyer = get_object_or_404(Buyer, id=buyer_id)
    import json
    from django.db.models import Q

    search_q    = request.GET.get("q", "").strip()
    crop_filter = request.GET.get("crop", "").strip()

    # Find farmers in buyer's locations
    locations = buyer.locations or []
    if not locations:
        farmers_qs = FarmerRegistration.objects.none()
    else:
        q_obj = Q()
        for loc in locations:
            state    = loc.get("state", "")
            district = loc.get("district", "")
            if state and district:
                q_obj |= Q(state=state, district__icontains=district)
            elif state:
                q_obj |= Q(state=state)
        farmers_qs = FarmerRegistration.objects.filter(q_obj).distinct()

    if search_q:
        farmers_qs = farmers_qs.filter(
            Q(full_name__icontains=search_q) |
            Q(village__icontains=search_q)
        )

    # Attach active crop listings to each farmer
    farmers = []
    for farmer in farmers_qs.order_by("full_name"):
        active_crops = farmer.crop_listings.filter(is_active=True)
        if crop_filter:
            active_crops = active_crops.filter(name__icontains=crop_filter)
        farmer.active_crops = list(active_crops[:4])
        farmers.append(farmer)

    return render(request, "buyer_dashboard.html", {
        "buyer": buyer,
        "farmers": farmers,
        "total_farmers": len(farmers),
        "search_q": search_q,
        "crop_filter": crop_filter,
    })


def buyer_logout(request):
    request.session.pop("buyer_id", None)
    request.session.pop("buyer_name", None)
    return redirect("buyer_login")


def buyer_profile(request):
    buyer_id = request.session.get("buyer_id")
    if not buyer_id:
        return redirect("buyer_login")
    buyer = get_object_or_404(Buyer, id=buyer_id)
    import json
    if request.method == "POST":
        buyer.full_name        = request.POST.get("full_name", buyer.full_name).strip()
        buyer.company          = request.POST.get("company", buyer.company or "").strip()
        buyer.interested_crops = request.POST.get("interested_crops", buyer.interested_crops).strip()
        buyer.notes            = request.POST.get("notes", buyer.notes or "").strip()
        try:
            buyer.locations = json.loads(request.POST.get("locations_json", "[]"))
        except Exception:
            pass
        buyer.save()
        request.session["buyer_name"] = buyer.full_name
        messages.success(request, "Profile updated.")
        return redirect("buyer_profile")
    selected_crops = buyer.crop_list()
    return render(request, "buyer_profile.html", {
        "buyer": buyer,
        "states": Buyer.STATE_CHOICES,
        "crop_choices": Buyer.CROP_CHOICES,
        "selected_crops": selected_crops,
        "locations_json": json.dumps(buyer.locations),
    })


@farmer_required
def direct_buyers(request):
    farmer_id = request.session.get("farmer_id")
    buyer_id  = request.session.get("buyer_id")
    crop_filter = request.GET.get("crop", "").strip()

    buyers_qs = Buyer.objects.filter(is_active=True).order_by("-created_at")

    if crop_filter:
        buyers_qs = buyers_qs.filter(interested_crops__icontains=crop_filter)

    farmer = None
    if farmer_id:
        farmer = get_object_or_404(FarmerRegistration, id=farmer_id)

    if farmer:
        all_buyers = list(buyers_qs)

        # Same district + taluka (closest)
        same_district = [b for b in all_buyers if any(
            loc.get("state") == farmer.state and
            loc.get("district") == farmer.district
            for loc in (b.locations or [])
        )]

        # Same state only (exclude already in district)
        same_district_ids = {b.id for b in same_district}
        same_state = [b for b in all_buyers if b.id not in same_district_ids and any(
            loc.get("state") == farmer.state
            for loc in (b.locations or [])
        )]

        # Others
        nearby_ids = same_district_ids | {b.id for b in same_state}
        others = [b for b in all_buyers if b.id not in nearby_ids]

        buyers = same_district + same_state + others
        nearby_count = len(same_district) + len(same_state)
        same_district_count = len(same_district)
    else:
        buyers = list(buyers_qs)
        nearby_count = 0
        same_district_count = 0

    all_crops = sorted(set(
        c.strip()
        for b in Buyer.objects.filter(is_active=True)
        for c in b.interested_crops.split(",") if c.strip()
    ))

    current_buyer = None
    if buyer_id:
        current_buyer = get_object_or_404(Buyer, id=buyer_id)

    return render(request, "direct_buyers.html", {
        "buyers": buyers,
        "current_buyer": current_buyer,
        "crop_filter": crop_filter,
        "all_crops": all_crops,
        "farmer_id": farmer_id,
        "farmer": farmer,
        "nearby_count": nearby_count,
        "same_district_count": same_district_count,
    })


@farmer_required
def search(request):
    query = request.GET.get("q", "").strip()
    results = {}
    not_found = False
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)

    if query:
        # My lands only
        lands = FarmerLand.objects.filter(
            farmer=farmer
        ).filter(
            Q(land_name__icontains=query) | Q(water_supply__icontains=query)
        )[:5]

        # My crop listings
        my_crops = CropListing.objects.filter(farmer=farmer).filter(
            Q(name__icontains=query) | Q(type__icontains=query)
        )[:5]

        # My tools
        my_tools = FarmingTool.objects.filter(farmer=farmer).filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )[:5]

        # Public schemes (all farmers can see)
        schemes = GovtScheme.objects.filter(is_active=True).filter(
            Q(title__icontains=query) | Q(short_description__icontains=query) |
            Q(keywords__icontains=query) | Q(category__icontains=query)
        )[:5]

        # Public crop marketplace (other farmers' active listings)
        market_crops = CropListing.objects.filter(
            is_active=True
        ).exclude(farmer=farmer).filter(
            Q(name__icontains=query) | Q(type__icontains=query)
        )[:5]

        # Public tools marketplace
        market_tools = FarmingTool.objects.filter(
            is_active=True
        ).exclude(farmer=farmer).filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )[:5]

        results = {
            "lands": lands,
            "my_crops": my_crops,
            "my_tools": my_tools,
            "schemes": schemes,
            "market_crops": market_crops,
            "market_tools": market_tools,
        }
        total = (lands.count() + my_crops.count() + my_tools.count() +
                 schemes.count() + market_crops.count() + market_tools.count())
        not_found = total == 0

    # AJAX JSON response for inline search overlay
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        import json as _json
        def fmt(qs, title_field, sub_fn):
            return [{"title": getattr(obj, title_field, str(obj)), "sub": sub_fn(obj)} for obj in qs]

        return JsonResponse({
            "not_found": not_found,
            "lands":        fmt(results.get("lands", []),       "land_name",  lambda o: f"{o.land_area} · {o.water_supply}"),
            "my_crops":     fmt(results.get("my_crops", []),    "name",       lambda o: f"₹{o.price}/{o.get_unit_display()} · {o.quantity} {o.get_unit_display()}"),
            "my_tools":     fmt(results.get("my_tools", []),    "name",       lambda o: f"₹{o.price} · {o.condition}"),
            "schemes":      fmt(results.get("schemes", []),     "title",      lambda o: o.short_description[:60] if o.short_description else ""),
            "market_crops": fmt(results.get("market_crops", []),"name",       lambda o: f"₹{o.price} · {o.farmer.full_name}, {o.farmer.district}"),
            "market_tools": fmt(results.get("market_tools", []),"name",       lambda o: f"₹{o.price} · {o.farmer.full_name}, {o.farmer.district}"),
        })

    return render(request, "search_results.html", {
        "query": query,
        "results": results,
        "not_found": not_found,
        "farmer": farmer,
    })


@farmer_required
def govt_schemes(request):
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    category = request.GET.get("category", "all").strip().lower()
    query = request.GET.get("q", "").strip()

    schemes = GovtScheme.objects.filter(is_active=True)

    if category and category != "all":
        schemes = schemes.filter(category=category)

    if query:
        schemes = schemes.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(full_description__icontains=query) |
            Q(eligibility__icontains=query) |
            Q(benefits__icontains=query) |
            Q(required_documents__icontains=query) |
            Q(keywords__icontains=query)
        )

    schemes = schemes.order_by("-created_at")

    # Farmer's existing applications
    applied_ids = set(
        FarmerSchemeApplication.objects.filter(farmer=farmer).values_list("scheme_id", flat=True)
    )

    # Scheme notifications for this farmer
    scheme_notifs = SchemeNotification.objects.filter(
        Q(farmer=farmer) | Q(farmer__isnull=True)
    ).order_by("-created_at")[:10]
    unread_scheme_notif_count = SchemeNotification.objects.filter(
        Q(farmer=farmer) | Q(farmer__isnull=True), is_read=False
    ).count()

    # Profile completeness
    profile, _ = FarmerProfile.objects.get_or_create(farmer=farmer)

    context = {
        "schemes": schemes,
        "search_query": query,
        "active_category": category if category else "all",
        "applied_ids": applied_ids,
        "scheme_notifs": scheme_notifs,
        "unread_scheme_notif_count": unread_scheme_notif_count,
        "farmer": farmer,
        "profile": profile,
        "profile_score": profile.score(),
    }
    return render(request, "govt_schemes.html", context)


@farmer_required
def govt_scheme_detail(request, pk):
    scheme = get_object_or_404(GovtScheme, pk=pk, is_active=True)
    recent_schemes = GovtScheme.objects.filter(is_active=True).exclude(pk=pk).order_by("-created_at")[:5]

    return render(request, "govt_scheme_detail.html", {
        "scheme": scheme,
        "recent_schemes": recent_schemes,
    })


# ─── Farmer Profile (0-100 Score) ────────────────────────────────────────────
@farmer_required
def farmer_profile_form(request):
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    profile, _ = FarmerProfile.objects.get_or_create(farmer=farmer)

    if request.method == "POST":
        profile.has_aadhar       = bool(request.POST.get("has_aadhar"))
        profile.aadhar_number    = request.POST.get("aadhar_number", "").strip()
        if request.FILES.get("aadhar_doc"):
            profile.aadhar_doc = request.FILES["aadhar_doc"]
        profile.has_pan          = bool(request.POST.get("has_pan"))
        profile.pan_number       = request.POST.get("pan_number", "").strip()
        if request.FILES.get("pan_doc"):
            profile.pan_doc = request.FILES["pan_doc"]
        profile.has_bank_account = bool(request.POST.get("has_bank_account"))
        profile.bank_name        = request.POST.get("bank_name", "").strip()
        profile.account_number   = request.POST.get("account_number", "").strip()
        profile.ifsc_code        = request.POST.get("ifsc_code", "").strip()
        profile.has_land_record  = bool(request.POST.get("has_land_record"))
        profile.land_record_number = request.POST.get("land_record_number", "").strip()
        if request.FILES.get("land_record_doc"):
            profile.land_record_doc = request.FILES["land_record_doc"]
        profile.has_soil_health_card = bool(request.POST.get("has_soil_health_card"))
        profile.soil_health_card_number = request.POST.get("soil_health_card_number", "").strip()
        if request.FILES.get("soil_health_card_doc"):
            profile.soil_health_card_doc = request.FILES["soil_health_card_doc"]
        profile.annual_income    = request.POST.get("annual_income", "").strip()
        profile.has_income_cert  = bool(request.POST.get("has_income_cert"))
        profile.income_cert_number = request.POST.get("income_cert_number", "").strip()
        if request.FILES.get("income_cert_doc"):
            profile.income_cert_doc = request.FILES["income_cert_doc"]
        profile.caste_category   = request.POST.get("caste_category", "").strip()
        profile.has_caste_cert   = bool(request.POST.get("has_caste_cert"))
        profile.caste_cert_number = request.POST.get("caste_cert_number", "").strip()
        if request.FILES.get("caste_cert_doc"):
            profile.caste_cert_doc = request.FILES["caste_cert_doc"]
        profile.email            = request.POST.get("email", "").strip()
        profile.has_ration_card  = bool(request.POST.get("has_ration_card"))
        profile.ration_card_number = request.POST.get("ration_card_number", "").strip()
        if request.FILES.get("ration_card_doc"):
            profile.ration_card_doc = request.FILES["ration_card_doc"]
        profile.has_photo        = bool(request.POST.get("has_photo"))
        if request.FILES.get("farmer_photo"):
            profile.farmer_photo = request.FILES["farmer_photo"]
        profile.save()
        messages.success(request, f"Profile updated! Score: {profile.score()}/100")
        return redirect("farmer_profile_form")

    return render(request, "farmer_profile_form.html", {
        "farmer": farmer,
        "profile": profile,
        "score": profile.score(),
    })


# ─── Soil AI Suggestion ───────────────────────────────────────────────────────
@require_POST
def soil_ai_suggest(request):
    """AJAX: Analyze soil data and return crop suggestions using OpenAI."""
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return JsonResponse({"success": False, "message": "Login required."})

    land_id = request.POST.get("land_id")
    land = get_object_or_404(FarmerLand, id=land_id, farmer_id=farmer_id)

    from openai import OpenAI
    from django.conf import settings
    import base64, json as _json

    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        return JsonResponse({"success": False, "message": "OPENAI_API_KEY not configured in settings.py"})

    client = OpenAI(api_key=api_key)

    JSON_SCHEMA = """{
  "crops": [{"name": "...", "reason": "...", "match": "high/medium/low"}],
  "soil_health": {"overall": "Good/Moderate/Poor", "summary": "..."},
  "deficiencies": [{"nutrient": "...", "level": "...", "fix": "..."}],
  "season": "...",
  "tips": "..."
}"""

    try:
        if land.soil_method == "manual" and any([land.ph, land.nitrogen, land.phosphorus, land.potassium]):
            prompt = f"""You are an expert Indian agricultural scientist.
Soil Analysis Data:
- pH: {land.ph or 'N/A'}
- EC: {land.ec or 'N/A'} dS/m
- Organic Carbon: {land.organic_carbon or 'N/A'} %
- Nitrogen (N): {land.nitrogen or 'N/A'} kg/ha
- Phosphorus (P): {land.phosphorus or 'N/A'} kg/ha
- Potassium (K): {land.potassium or 'N/A'} kg/ha
- Sulphur: {land.sulphur or 'N/A'}
- Zinc: {land.zinc or 'N/A'}
- Iron: {land.iron or 'N/A'}
- Manganese: {land.manganese or 'N/A'}
- Copper: {land.copper or 'N/A'}
- Boron: {land.boron or 'N/A'}
- Water Supply: {land.water_supply}
- Location: {land.farmer.district}, {land.farmer.state}, India
- Land Area: {land.land_area}

Based on this soil data provide top 3 crop recommendations with reasons, soil health assessment, deficiencies and fixes, best season.
Reply ONLY in this JSON format:
{JSON_SCHEMA}"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=1000,
            )
            raw = response.choices[0].message.content.strip()
            result = _json.loads(raw)

        elif land.soil_method == "upload" and land.soil_report:
            ext = land.soil_report.name.split(".")[-1].lower()
            with open(land.soil_report.path, "rb") as f:
                file_bytes = f.read()
            b64 = base64.b64encode(file_bytes).decode()

            if ext in ["jpg", "jpeg", "png"]:
                mime = "image/jpeg" if ext in ["jpg","jpeg"] else "image/png"
                prompt_text = f"""You are an expert Indian agricultural scientist. This is a soil health report image from {land.farmer.district}, {land.farmer.state}, India.
Analyze it and provide top 3 crop recommendations, soil health assessment, deficiencies and fixes, best season.
Reply ONLY in this JSON format:
{JSON_SCHEMA}"""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ]}],
                    response_format={"type": "json_object"},
                    max_tokens=1000,
                )
            else:
                # PDF — extract text and validate soil content
                try:
                    from pypdf import PdfReader
                    import io as _io
                    reader = PdfReader(_io.BytesIO(file_bytes))
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                except Exception:
                    pdf_text = ""

                # Check if PDF contains soil-related keywords (strict match)
                import re
                soil_keywords = [
                    r"\bnitrogen\b", r"\bphosphorus\b", r"\bpotassium\b",
                    r"\borganic carbon\b", r"\belectrical conductivity\b",
                    r"\bsoil report\b", r"\bsoil health\b", r"\bsoil test\b",
                    r"\bsoil sample\b", r"\bph value\b", r"\bsoil ph\b",
                    r"\bzinc\b", r"\bsulphur\b", r"\bmanganese\b",
                    r"\bमिट्टी\b", r"\bkrishi vigyan\b", r"\bsoil fertility\b",
                ]
                pdf_lower = pdf_text.lower()
                has_soil_data = any(re.search(kw, pdf_lower) for kw in soil_keywords)

                if not has_soil_data:
                    return JsonResponse({
                        "success": False,
                        "message": "આ PDF માં soil report data મળ્યો નથી. કૃપા કરીને સાચો soil testing report PDF upload કરો, અથવા Manual Soil Data વાપરો."
                    })

                prompt_text = f"""You are an expert Indian agricultural scientist.
A farmer from {land.farmer.district}, {land.farmer.state}, India has uploaded a soil report PDF.
Here is the extracted text from the PDF:

{pdf_text[:3000]}

Based on the soil data in this report, provide top 3 crop recommendations with reasons, soil health assessment, deficiencies and fixes, best season.
If the data is incomplete, use what is available.
Reply ONLY in this JSON format:
{JSON_SCHEMA}"""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_text}],
                    response_format={"type": "json_object"},
                    max_tokens=1000,
                )

            raw = response.choices[0].message.content.strip()
            result = _json.loads(raw)

        else:
            return JsonResponse({"success": False, "message": "No soil data available. Please add manual soil data or upload a soil report."})

        return JsonResponse({"success": True, "data": result, "land_name": land.land_name})

    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return JsonResponse({"success": False, "message": "API quota exceeded. Please try again later."})
        if "401" in err or "invalid" in err.lower():
            return JsonResponse({"success": False, "message": "API key is invalid. Please check settings."})
        return JsonResponse({"success": False, "message": f"AI Error: {err}"})


# ─── Govt Scheme One-Click Apply ──────────────────────────────────────────────
@farmer_required
@require_POST
def scheme_apply(request, scheme_id):
    farmer_id = request.session.get("farmer_id")
    farmer = get_object_or_404(FarmerRegistration, id=farmer_id)
    scheme = get_object_or_404(GovtScheme, id=scheme_id, is_active=True)

    app, created = FarmerSchemeApplication.objects.get_or_create(
        farmer=farmer, scheme=scheme,
        defaults={"status": "applied"}
    )
    if created:
        # Create scheme notification for this farmer
        SchemeNotification.objects.create(
            farmer=farmer,
            scheme=scheme,
            application=app,
            notif_type="status_update",
            title=f"✅ Applied: {scheme.title}",
            message=f"Tamari '{scheme.title}' scheme mate application submit thayi. Status: Applied.",
        )
        messages.success(request, f"'{scheme.title}' mate apply thayu!")
    else:
        messages.info(request, f"Tame pahela thi '{scheme.title}' mate apply karyu che.")

    return redirect("govt_schemes")


# ─── Mark Scheme Notifications Read ──────────────────────────────────────────
@farmer_required
def mark_scheme_notifs_read(request):
    farmer_id = request.session.get("farmer_id")
    from django.db.models import Q
    SchemeNotification.objects.filter(
        Q(farmer_id=farmer_id) | Q(farmer__isnull=True), is_read=False
    ).update(is_read=True)
    return JsonResponse({"success": True})


# ─── Scheme Notification Count API ───────────────────────────────────────────
def scheme_notif_count(request):
    farmer_id = request.session.get("farmer_id")
    if not farmer_id:
        return JsonResponse({"count": 0})
    from django.db.models import Q
    count = SchemeNotification.objects.filter(
        Q(farmer_id=farmer_id) | Q(farmer__isnull=True), is_read=False
    ).count()
    return JsonResponse({"count": count})
