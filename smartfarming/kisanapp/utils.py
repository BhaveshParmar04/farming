import requests
from django.conf import settings

def send_sms_otp(mobile, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"

    params = {
        "authorization": settings.FAST2SMS_API_KEY,
        "variables_values": otp,
        "route": "otp",
        "numbers": mobile,
    }

    response = requests.get(url, params=params, timeout=15)
    # print("SMS API Response:", response.text)

    try:
        return response.json()
    except ValueError:
        return {
            "return": False,
            "message": "Invalid response from SMS provider"
        }
        
        

from datetime import date, timedelta

# Crop schedule templates: list of (day_offset, activity_type, title, message)
CROP_SCHEDULES = {
    "Wheat": [
        (0,   "sowing",    "Wheat Sowing Day",            "Aaj ghau vavvo – beej upchar karo (thiram/carbendazim)."),
        (7,   "watering",  "Paheli Sinchai (Crown Root)",  "Crown root initiation stage – pehli vaar pani aapvo."),
        (10,  "fertilizer","Urea Top Dressing",            "Urea 50 kg/ha top dressing karo."),
        (21,  "watering",  "Tillering Stage Pani",         "Tillering stage – biji vaar pani aapvo."),
        (45,  "watering",  "Jointing Stage Pani",          "Jointing stage – triji vaar pani aapvo."),
        (60,  "fertilizer","DAP Spray",                    "DAP 2% foliar spray karo."),
        (65,  "watering",  "Flowering Stage Pani",         "Flowering stage – chauthi vaar pani aapvo."),
        (75,  "pesticide", "Aphid / Yellow Rust Check",    "Aphid hoy to imidacloprid spray karo. Yellow rust mate propiconazole."),
        (90,  "watering",  "Grain Filling Pani",           "Grain filling stage – panchmi vaar pani aapvo."),
        (110, "harvesting","Ghau Katni Taiyar",            "Ghau pakvi gayu – katni shuru karo. Moisture 14% niche hoy tyare."),
    ],
    "Cotton": [
        (0,   "sowing",    "Cotton Sowing",                "Kapas vavvo – row spacing 90x60 cm rakho."),
        (15,  "watering",  "Paheli Sinchai",               "Seedling stage – halku pani aapvo."),
        (30,  "fertilizer","DAP + Urea",                   "DAP 100 kg + Urea 50 kg/ha aapvo."),
        (45,  "watering",  "Vegetative Stage Pani",        "Vegetative growth – biji vaar pani aapvo."),
        (60,  "pesticide", "Whitefly / Jassid Check",      "Neem oil 5ml/L spray karo. Whitefly mate imidacloprid."),
        (70,  "watering",  "Flowering Stage Pani",         "Flowering shuru – triji vaar pani aapvo."),
        (75,  "fertilizer","Potash Top Dressing",          "Potash 50 kg/ha aapvo – boll development mate."),
        (90,  "pesticide", "Pink Bollworm Alert",          "Pheromone traps check karo. Bollworm mate chlorantraniliprole spray."),
        (100, "watering",  "Boll Formation Pani",          "Boll formation – chauthi vaar pani aapvo."),
        (150, "harvesting","Kapas Vinnvan Shuru",          "Boll khulva lagya – pehli vinnvan shuru karo."),
    ],
    "Rice": [
        (0,   "sowing",    "Nursery Taiyar Karo",          "Nursery bed taiyar karo – beej 24 karak pani ma bholavo."),
        (25,  "sowing",    "Transplanting",                "25 divas ni nursery – khet ma ropan karo."),
        (30,  "fertilizer","Basal Fertilizer",             "Urea 60 kg + DAP 60 kg + MOP 40 kg/ha aapvo."),
        (35,  "watering",  "Flooding Maintain",            "2-3 cm pani khet ma rakho – continuous flooding."),
        (50,  "fertilizer","Urea Top Dressing",            "Urea 60 kg/ha top dressing – tillering stage."),
        (60,  "pesticide", "Brown Planthopper Check",      "BPH mate imidacloprid spray. Blast mate tricyclazole."),
        (70,  "watering",  "Panicle Initiation Pani",      "Panicle initiation – pani level maintain karo."),
        (90,  "watering",  "Flowering Pani",               "Flowering stage – khet sukhu na padva devo."),
        (110, "watering",  "Grain Filling Pani",           "Grain filling – alternate wetting & drying shuru karo."),
        (130, "harvesting","Chaval Katni",                 "Grain 80% pakvu – pani band karo ane 7 din baad katni karo."),
    ],
    "Maize": [
        (0,   "sowing",    "Makai Vavvo",                  "Makai vavvo – spacing 60x25 cm, depth 4-5 cm."),
        (10,  "watering",  "Germination Pani",             "Germination stage – halku pani aapvo."),
        (20,  "fertilizer","Basal Dose",                   "DAP 120 kg + Zinc 25 kg/ha aapvo."),
        (30,  "watering",  "Knee High Stage Pani",         "Knee high stage – biji vaar pani aapvo."),
        (40,  "fertilizer","Urea Top Dressing",            "Urea 100 kg/ha top dressing karo."),
        (50,  "pesticide", "Fall Armyworm Check",          "Whorl ma sawdust jaisi material hoy to chlorantraniliprole spray karo."),
        (55,  "watering",  "Tasseling Pani",               "Tasseling stage – triji vaar pani – critical stage."),
        (65,  "watering",  "Grain Filling Pani",           "Grain filling – chauthi vaar pani aapvo."),
        (90,  "harvesting","Makai Katni",                  "Husk sukhi gayi – makai katni shuru karo."),
    ],
    "Groundnut": [
        (0,   "sowing",    "Moongfali Vavvi",              "Moongfali vavvi – spacing 30x10 cm, beej upchar karo."),
        (15,  "watering",  "Paheli Sinchai",               "Seedling stage – halku pani aapvo."),
        (25,  "fertilizer","Gypsum + DAP",                 "Gypsum 200 kg + DAP 100 kg/ha aapvo."),
        (35,  "watering",  "Flowering Pani",               "Flowering stage – biji vaar pani aapvo."),
        (45,  "watering",  "Pegging Stage Pani",           "Pegging stage – triji vaar pani – critical stage."),
        (50,  "pesticide", "Leaf Miner / Tikka Check",     "Leaf miner mate neem spray. Tikka disease mate mancozeb."),
        (60,  "watering",  "Pod Development Pani",         "Pod filling – chauthi vaar pani aapvo."),
        (90,  "harvesting","Moongfali Khudai",             "Leaves pili padva lagi – khudai shuru karo."),
    ],
    "Soybean": [
        (0,   "sowing",    "Soybean Vavvo",                "Soybean vavvo – Rhizobium seed treatment karo."),
        (15,  "watering",  "Paheli Sinchai",               "Seedling stage – halku pani aapvo."),
        (20,  "fertilizer","DAP Basal Dose",               "DAP 100 kg/ha aapvo."),
        (35,  "watering",  "Flowering Pani",               "Flowering stage – biji vaar pani aapvo."),
        (45,  "pesticide", "Girdle Beetle Check",          "Girdle beetle mate chlorpyrifos spray. Yellow mosaic mate whitefly control."),
        (50,  "watering",  "Pod Filling Pani",             "Pod filling – triji vaar pani aapvo."),
        (80,  "harvesting","Soybean Katni",                "Leaves jhadi padva lagi – katni shuru karo."),
    ],
    "Mustard": [
        (0,   "sowing",    "Sarso Vavvi",                  "Sarso vavvi – spacing 30x10 cm, depth 2-3 cm."),
        (15,  "watering",  "Paheli Sinchai",               "Seedling stage – halku pani aapvo."),
        (20,  "fertilizer","DAP + Sulphur",                "DAP 100 kg + Sulphur 20 kg + Urea 60 kg/ha aapvo."),
        (35,  "watering",  "Branching Stage Pani",         "Branching stage – biji vaar pani aapvo."),
        (45,  "pesticide", "Aphid Alert",                  "Aphid mate dimethoate spray. Alternaria blight mate mancozeb."),
        (55,  "watering",  "Pod Formation Pani",           "Pod formation – triji vaar pani aapvo."),
        (80,  "harvesting","Sarso Katni",                  "Pods pili padva lagi – katni shuru karo."),
    ],
    "Sugarcane": [
        (0,   "sowing",    "Sherdio Vavvo",                "Sherdio vavvo – 2-3 aankh vali kalam vavvo."),
        (20,  "watering",  "Paheli Sinchai",               "Germination stage – pani aapvo."),
        (30,  "fertilizer","Basal Fertilizer",             "Urea 200 kg + DAP 100 kg + MOP 100 kg/ha aapvo."),
        (45,  "watering",  "Tillering Pani",               "Tillering stage – biji vaar pani aapvo."),
        (60,  "pesticide", "Top Borer Check",              "Top borer mate carbofuran granules. Pyrilla mate neem spray."),
        (90,  "watering",  "Grand Growth Pani",            "Grand growth stage – drip irrigation shuru karo."),
        (120, "fertilizer","Top Dressing",                 "Urea 100 kg/ha top dressing karo."),
        (180, "watering",  "Maturity Stage Pani",          "Maturity stage – pani band karo 30 din pehla."),
        (300, "harvesting","Sherdio Katni",                "Sherdio pakvi gayu – katni shuru karo."),
    ],
    "Tomato": [
        (0,   "sowing",    "Tameta Nursery",               "Nursery taiyar karo – beej upchar karo."),
        (25,  "sowing",    "Transplanting",                "25 divas ni nursery – khet ma ropan karo."),
        (30,  "watering",  "Drip Irrigation Shuru",        "Drip irrigation shuru karo – 5-6 vaar/week."),
        (35,  "fertilizer","NPK 19:19:19",                 "NPK 19:19:19 200 kg/ha + Calcium nitrate aapvo."),
        (45,  "pesticide", "Fruit Borer Check",            "Fruit borer mate spinosad spray. Early blight mate mancozeb."),
        (55,  "watering",  "Flowering Pani",               "Flowering stage – pani niyamit rakho."),
        (65,  "fertilizer","Potassium Spray",              "Potassium nitrate 1% foliar spray karo."),
        (80,  "harvesting","Tameta Vinnvan",               "Tameta lal thava lagya – vinnvan shuru karo."),
    ],
    "Bajra (Millet)": [
        (0,   "sowing",    "Bajra Vavvo",                  "Bajra vavvo – spacing 45x15 cm."),
        (10,  "watering",  "Paheli Sinchai",               "Germination – halku pani aapvo."),
        (20,  "fertilizer","FYM + Urea",                   "FYM 10t/ha + Urea 60 kg/ha aapvo."),
        (35,  "watering",  "Vegetative Pani",              "Vegetative stage – biji vaar pani aapvo."),
        (45,  "pesticide", "Shoot Fly / Downy Mildew",     "Shoot fly mate imidacloprid seed treatment. Downy mildew mate metalaxyl."),
        (60,  "watering",  "Flowering Pani",               "Flowering stage – triji vaar pani aapvo."),
        (75,  "harvesting","Bajra Katni",                  "Panicle pakvi gayi – katni shuru karo."),
    ],
}


def generate_crop_activities(farmer, land, crop_name, start_date=None):
    """Generate CropActivity records for a given crop on a land."""
    from .models import CropActivity, Notification
    if start_date is None:
        start_date = date.today()

    schedule = CROP_SCHEDULES.get(crop_name)
    if not schedule:
        return 0

    # Remove existing pending activities for same land+crop
    CropActivity.objects.filter(
        farmer=farmer, land=land, crop_name=crop_name, status="pending"
    ).delete()

    activities = []
    for day_offset, act_type, title, message in schedule:
        activities.append(CropActivity(
            farmer=farmer,
            land=land,
            crop_name=crop_name,
            activity_type=act_type,
            title=title,
            message=message,
            due_date=start_date + timedelta(days=day_offset),
        ))
    CropActivity.objects.bulk_create(activities)

    # Create a single Notification for this crop plan
    Notification.objects.create(
        farmer=farmer,
        land=land,
        crop_name=crop_name,
        notif_type="sowing",
        title=f"{crop_name} plan saved – {len(activities)} activities scheduled",
        message=f"{land.land_name} par {crop_name} mate {len(activities)} activities {start_date.strftime('%d %b %Y')} thi schedule thayi.",
    )

    return len(activities)
