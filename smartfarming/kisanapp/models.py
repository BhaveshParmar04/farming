from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class FarmerRegistration(models.Model):
    STATE_CHOICES = [
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Karnataka", "Karnataka"),
        ("Kerala", "Kerala"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("West Bengal", "West Bengal"),
    ]

    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=10, unique=True)
    mobile_verified = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)

    land_record = models.CharField(max_length=100)
    state = models.CharField(max_length=50, choices=STATE_CHOICES)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.mobile}"


class MobileOTP(models.Model):
    mobile = models.CharField(max_length=10)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.mobile} - {self.otp}"
    

class FarmerLand(models.Model):
    WATER_CHOICES = [
        ("Borewell", "Borewell"),
        ("Canal", "Canal"),
        ("River", "River"),
        ("Rain Water", "Rain Water"),
        ("Drip Irrigation", "Drip Irrigation"),
    ]
    SOIL_METHOD_CHOICES = [
        ("upload", "Upload Report"),
        ("manual", "Manual Entry"),
    ]

    farmer = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="lands")
    land_name = models.CharField(max_length=150)
    land_area = models.CharField(max_length=50)
    water_supply = models.CharField(max_length=50, choices=WATER_CHOICES, default="Borewell")
    soil_method = models.CharField(max_length=10, choices=SOIL_METHOD_CHOICES, default="upload")

    # upload method
    soil_report = models.FileField(upload_to="soil_reports/", blank=True, null=True)

    # manual method
    ph = models.CharField(max_length=10, blank=True, null=True)
    ec = models.CharField(max_length=10, blank=True, null=True)
    organic_carbon = models.CharField(max_length=10, blank=True, null=True)
    nitrogen = models.CharField(max_length=10, blank=True, null=True)
    phosphorus = models.CharField(max_length=10, blank=True, null=True)
    potassium = models.CharField(max_length=10, blank=True, null=True)
    sulphur = models.CharField(max_length=10, blank=True, null=True)
    zinc = models.CharField(max_length=10, blank=True, null=True)
    iron = models.CharField(max_length=10, blank=True, null=True)
    manganese = models.CharField(max_length=10, blank=True, null=True)
    copper = models.CharField(max_length=10, blank=True, null=True)
    boron = models.CharField(max_length=10, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.land_name} - {self.farmer.full_name}"


class CropListing(models.Model):
    TYPE_CHOICES = [
        ("Vegetable", "Vegetable"),
        ("Fruit", "Fruit"),
        ("Grain", "Grain"),
        ("Pulse", "Pulse"),
        ("Other", "Other"),
    ]
    UNIT_CHOICES = [
        ("kg", "kg"),
        ("quintal", "Quintal"),
        ("ton", "Ton"),
    ]

    farmer = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="crop_listings")
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="kg")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    video = models.FileField(upload_to="crop_videos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.farmer.full_name}"


class CropImage(models.Model):
    crop = models.ForeignKey(CropListing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="crop_images/")

    def __str__(self):
        return f"Image for {self.crop.name}"


class FarmingTool(models.Model):
    CATEGORY_CHOICES = [
        ("Tractor", "Tractor"),
        ("Tractor Parts", "Tractor Parts"),
        ("Irrigation Equipment", "Irrigation Equipment"),
        ("Harvesting Tools", "Harvesting Tools"),
        ("Sprayer", "Sprayer"),
        ("Other Farming Equipment", "Other Farming Equipment"),
    ]
    CONDITION_CHOICES = [
        ("New", "New"),
        ("Good", "Good"),
        ("Used", "Used"),
        ("For Rent", "For Rent"),
    ]

    farmer = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="tools")
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="Good")
    description = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to="tool_videos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.farmer.full_name}"


class FarmingToolImage(models.Model):
    tool = models.ForeignKey(FarmingTool, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="tool_images/")

    def __str__(self):
        return f"Image for {self.tool.name}"


class CropActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ("watering",    "Watering"),
        ("fertilizer",  "Fertilizer"),
        ("pesticide",   "Pesticide"),
        ("harvesting",  "Harvesting"),
        ("sowing",      "Sowing"),
        ("general",     "General"),
    ]
    STATUS_CHOICES = [
        ("pending",  "Pending"),
        ("done",     "Done"),
        ("skipped",  "Skipped"),
    ]

    farmer   = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="activities")
    land     = models.ForeignKey(FarmerLand, on_delete=models.CASCADE, related_name="activities")
    crop_name= models.CharField(max_length=100)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    title    = models.CharField(max_length=255)
    message  = models.TextField()
    due_date = models.DateField()
    status   = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    is_read  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.crop_name} – {self.title} ({self.land.land_name})"

    @property
    def is_urgent(self):
        from django.utils import timezone
        return self.status == "pending" and self.due_date <= timezone.now().date()


class BuyRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    crop = models.ForeignKey(CropListing, on_delete=models.CASCADE, related_name="buy_requests")
    buyer = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="buy_requests")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.full_name} wants {self.quantity} of {self.crop.name}"


class GovtScheme(models.Model):
    CATEGORY_CHOICES = [
        ("crop", "Crop"),
        ("subsidy", "Subsidy"),
        ("equipment", "Equipment"),
        ("irrigation", "Irrigation"),
        ("insurance", "Insurance"),
    ]

    title = models.CharField(max_length=255)
    short_description = models.TextField()
    full_description = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    required_documents = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="subsidy")
    keywords = models.CharField(max_length=255, blank=True, null=True)
    official_details_url = models.URLField()
    apply_url = models.URLField()
    icon_class = models.CharField(max_length=100, default="fas fa-leaf")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    TYPE_CHOICES = [
        ("watering",   "Watering"),
        ("fertilizer", "Fertilizer"),
        ("pesticide",  "Pesticide"),
        ("harvesting", "Harvesting"),
        ("sowing",     "Sowing"),
        ("general",    "General"),
    ]

    farmer   = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="notifications")
    land     = models.ForeignKey(FarmerLand, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    crop_name= models.CharField(max_length=100, blank=True)
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="general")
    title    = models.CharField(max_length=255)
    message  = models.TextField()
    is_read  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.farmer.full_name} – {self.title}"

    def time_ago(self):
        from django.utils import timezone
        diff = timezone.now() - self.created_at
        s = int(diff.total_seconds())
        if s < 60:   return "just now"
        if s < 3600: m = s//60;  return f"{m} minute{'s' if m>1 else ''} ago"
        if s < 86400: h = s//3600; return f"{h} hour{'s' if h>1 else ''} ago"
        d = s//86400; return f"{d} day{'s' if d>1 else ''} ago"


class FarmerSchemeApplication(models.Model):
    """Track which govt schemes a farmer has applied for."""
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("pending", "Pending"),
    ]
    farmer = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="scheme_applications")
    scheme = models.ForeignKey(GovtScheme, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    notes  = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("farmer", "scheme")
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.farmer.full_name} → {self.scheme.title} [{self.status}]"


class FarmerProfile(models.Model):
    """Stores farmer's document/eligibility details for govt scheme applications (0-100 score)."""
    farmer = models.OneToOneField(FarmerRegistration, on_delete=models.CASCADE, related_name="profile_details")

    # Personal Documents (20 pts)
    has_aadhar       = models.BooleanField(default=False)
    aadhar_number    = models.CharField(max_length=12, blank=True)
    aadhar_doc       = models.ImageField(upload_to="profile_docs/aadhar/", blank=True, null=True)
    has_pan          = models.BooleanField(default=False)
    pan_number       = models.CharField(max_length=10, blank=True)
    pan_doc          = models.ImageField(upload_to="profile_docs/pan/", blank=True, null=True)

    # Bank Details (20 pts)
    has_bank_account = models.BooleanField(default=False)
    bank_name        = models.CharField(max_length=100, blank=True)
    account_number   = models.CharField(max_length=20, blank=True)
    ifsc_code        = models.CharField(max_length=11, blank=True)

    # Land Documents (20 pts)
    has_land_record  = models.BooleanField(default=False)  # 7/12 utara
    land_record_number = models.CharField(max_length=50, blank=True)
    land_record_doc  = models.ImageField(upload_to="profile_docs/land/", blank=True, null=True)
    has_soil_health_card = models.BooleanField(default=False)
    soil_health_card_number = models.CharField(max_length=50, blank=True)
    soil_health_card_doc = models.ImageField(upload_to="profile_docs/soil/", blank=True, null=True)

    # Farming Details (20 pts)
    annual_income    = models.CharField(max_length=20, blank=True)
    has_income_cert  = models.BooleanField(default=False)
    income_cert_number = models.CharField(max_length=50, blank=True)
    income_cert_doc  = models.ImageField(upload_to="profile_docs/income/", blank=True, null=True)
    caste_category   = models.CharField(max_length=20, blank=True, choices=[
        ("General","General"),("OBC","OBC"),("SC","SC"),("ST","ST"),
    ])
    has_caste_cert   = models.BooleanField(default=False)
    caste_cert_number = models.CharField(max_length=50, blank=True)
    caste_cert_doc   = models.ImageField(upload_to="profile_docs/caste/", blank=True, null=True)

    # Contact & Other (20 pts)
    email            = models.EmailField(blank=True)
    has_photo        = models.BooleanField(default=False)
    farmer_photo     = models.ImageField(upload_to="farmer_photos/", blank=True, null=True)
    has_ration_card  = models.BooleanField(default=False)
    ration_card_number = models.CharField(max_length=50, blank=True)
    ration_card_doc  = models.ImageField(upload_to="profile_docs/ration/", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def score(self):
        """Calculate 0-100 profile completeness score."""
        pts = 0
        # Personal (20)
        if self.has_aadhar and self.aadhar_number: pts += 10
        if self.has_pan and self.pan_number: pts += 10
        # Bank (20)
        if self.has_bank_account and self.bank_name and self.account_number and self.ifsc_code: pts += 20
        # Land (20)
        if self.has_land_record: pts += 10
        if self.has_soil_health_card: pts += 10
        # Farming (20)
        if self.annual_income: pts += 5
        if self.has_income_cert: pts += 5
        if self.caste_category: pts += 5
        if self.has_caste_cert: pts += 5
        # Other (20)
        if self.email: pts += 5
        if self.has_photo and self.farmer_photo: pts += 5
        if self.has_ration_card: pts += 5
        if self.farmer.mobile_verified: pts += 5
        return pts

    def __str__(self):
        return f"Profile – {self.farmer.full_name} ({self.score()}%)"


class SchemeNotification(models.Model):
    """Notifications specific to govt schemes — new scheme added, application status changed."""
    TYPE_CHOICES = [
        ("new_scheme", "New Scheme"),
        ("status_update", "Application Status Update"),
        ("reminder", "Apply Reminder"),
    ]
    farmer     = models.ForeignKey(FarmerRegistration, on_delete=models.CASCADE, related_name="scheme_notifications", null=True, blank=True)
    scheme     = models.ForeignKey("GovtScheme", on_delete=models.CASCADE, related_name="scheme_notifications", null=True, blank=True)
    application= models.ForeignKey("FarmerSchemeApplication", on_delete=models.CASCADE, related_name="scheme_notifications", null=True, blank=True)
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="new_scheme")
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notif_type} – {self.title}"


class Buyer(models.Model):
    STATE_CHOICES = FarmerRegistration.STATE_CHOICES

    CROP_CHOICES = [
        ("Wheat", "Wheat / ઘઉં"),
        ("Rice", "Rice / ચોખા"),
        ("Cotton", "Cotton / કપાસ"),
        ("Groundnut", "Groundnut / મગફળી"),
        ("Maize", "Maize / મકાઈ"),
        ("Soybean", "Soybean / સોયાબીન"),
        ("Mustard", "Mustard / સરસવ"),
        ("Sugarcane", "Sugarcane / શેરડી"),
        ("Tomato", "Tomato / ટામેટા"),
        ("Onion", "Onion / ડુંગળી"),
        ("Potato", "Potato / બટાટા"),
        ("Bajra", "Bajra / બાજરો"),
        ("Jowar", "Jowar / જુવાર"),
        ("Turmeric", "Turmeric / હળદર"),
        ("Chilli", "Chilli / મરચું"),
        ("Garlic", "Garlic / લસણ"),
        ("Sesame", "Sesame / તલ"),
        ("Castor", "Castor / એરંડા"),
        ("Banana", "Banana / કેળા"),
        ("Mango", "Mango / કેરી"),
    ]

    full_name   = models.CharField(max_length=150)
    mobile      = models.CharField(max_length=10, unique=True)
    mobile_verified = models.BooleanField(default=False)
    company     = models.CharField(max_length=150, blank=True, null=True)
    # Multiple locations stored as JSON: [{"state":"Gujarat","district":"Ahmedabad","taluka":"Daskroi"},...]
    locations   = models.JSONField(default=list, help_text="List of {state, district, taluka} dicts")
    # crops they want to buy — comma separated
    interested_crops = models.CharField(max_length=500, help_text="Comma separated crop names")
    notes       = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} – {self.mobile}"

    def crop_list(self):
        return [c.strip() for c in self.interested_crops.split(",") if c.strip()]

    def primary_location(self):
        if self.locations:
            return self.locations[0]
        return {}

    def all_districts(self):
        return [loc.get("district","") for loc in self.locations if loc.get("district")]

    def all_states(self):
        return list(set(loc.get("state","") for loc in self.locations if loc.get("state")))


# ─── Signal: New GovtScheme → notify all farmers ─────────────────────────────
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=GovtScheme)
def notify_farmers_new_scheme(sender, instance, created, **kwargs):
    if created and instance.is_active:
        # SchemeNotification broadcast (farmer=None)
        SchemeNotification.objects.create(
            farmer=None,
            scheme=instance,
            notif_type="new_scheme",
            title=f"🆕 New Scheme: {instance.title}",
            message=f"Navi government scheme available che: '{instance.title}'. Category: {instance.get_category_display()}. Apply karo!",
        )
        # Individual Notification for each farmer so bell icon shows it
        farmers = FarmerRegistration.objects.all()
        notifs = [
            Notification(
                farmer=farmer,
                notif_type="general",
                title=f"🏛️ New Govt Scheme: {instance.title}",
                message=f"Navi government scheme available che: '{instance.title}'. Tamari eligibility check karo ane apply karo!",
            )
            for farmer in farmers
        ]
        Notification.objects.bulk_create(notifs)

@receiver(post_save, sender=FarmerSchemeApplication)
def notify_scheme_status_change(sender, instance, created, **kwargs):
    if not created:  # status update
        SchemeNotification.objects.create(
            farmer=instance.farmer,
            scheme=instance.scheme,
            application=instance,
            notif_type="status_update",
            title=f"📋 Scheme Update: {instance.scheme.title}",
            message=f"Tamari '{instance.scheme.title}' application status update thayi: {instance.get_status_display()}.",
        )


class ContactMessage(models.Model):
    name       = models.CharField(max_length=150)
    email      = models.EmailField(blank=True, null=True)
    phone      = models.CharField(max_length=15, blank=True, null=True)
    message    = models.TextField()
    farmer     = models.ForeignKey(FarmerRegistration, on_delete=models.SET_NULL, null=True, blank=True, related_name="contact_messages")
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.created_at.strftime('%d %b %Y')}"

    class Meta:
        ordering = ["-created_at"]
