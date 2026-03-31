from django.contrib.admin import AdminSite
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import path
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.template.response import TemplateResponse
from .models import (
    FarmerSchemeApplication, GovtScheme, FarmerProfile,
    FarmerRegistration, FarmerLand, SchemeNotification
)


class GovtAdminSite(AdminSite):
    site_header  = "🌾 Kisan Govt Scheme Admin"
    site_title   = "Govt Scheme Admin"
    index_title  = "Government Scheme Management Panel"
    site_url     = "/"
    index_template     = "admin/govt_admin/govt_dashboard.html"
    base_site_template = "admin/govt_admin/base_site.html"

    def index(self, request, extra_context=None):
        ctx = self.each_context(request)
        ctx.update({
            "title": self.index_title,
            "total_schemes":       GovtScheme.objects.count(),
            "total_applications":  FarmerSchemeApplication.objects.count(),
            "approved_count":      FarmerSchemeApplication.objects.filter(status="approved").count(),
            "pending_count":       FarmerSchemeApplication.objects.filter(status__in=["applied","pending"]).count(),
            "total_profiles":      FarmerProfile.objects.count(),
            "recent_applications": FarmerSchemeApplication.objects.select_related("farmer","scheme").order_by("-applied_at")[:8],
            "active_schemes":      GovtScheme.objects.filter(is_active=True).order_by("-created_at")[:6],
        })
        if extra_context:
            ctx.update(extra_context)
        return TemplateResponse(request, self.index_template, ctx)


govt_admin_site = GovtAdminSite(name="govt_admin")


# ── Govt Scheme ───────────────────────────────────────────────────────────────
@admin.register(GovtScheme, site=govt_admin_site)
class GovtSchemeGovtAdmin(admin.ModelAdmin):
    list_display   = ("title", "category", "application_count", "is_active", "created_at")
    list_filter    = ("category", "is_active")
    search_fields  = ("title", "short_description", "keywords")
    list_editable  = ("is_active",)
    list_per_page  = 15
    ordering       = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Info", {"fields": ("title", "category", "icon_class", "is_active")}),
        ("Descriptions", {"fields": ("short_description", "full_description")}),
        ("Eligibility & Benefits", {"fields": ("eligibility", "benefits", "required_documents")}),
        ("Links", {"fields": ("official_details_url", "apply_url")}),
        ("Metadata", {"fields": ("created_at", "keywords")}),
    )

    def application_count(self, obj):
        c = obj.applications.count()
        return format_html('<b style="color:#2e7d32">{}</b>', c)
    application_count.short_description = "Applications"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("scheme-applications/<int:scheme_id>/",
                 self.admin_site.admin_view(self.scheme_applications_view),
                 name="govt_scheme_applications"),
        ]
        return custom + urls

    def scheme_applications_view(self, request, scheme_id):
        scheme = get_object_or_404(GovtScheme, pk=scheme_id)
        applications = FarmerSchemeApplication.objects.filter(
            scheme=scheme
        ).select_related("farmer").order_by("-applied_at")
        context = {
            **self.admin_site.each_context(request),
            "scheme": scheme,
            "applications": applications,
            "title": f"Applications — {scheme.title}",
        }
        return render(request, "admin/govt/scheme_applications.html", context)

    def view_applications(self, obj):
        url = f"scheme-applications/{obj.pk}/"
        return format_html('<a class="button" href="{}">📋 View Applications ({})</a>',
                           url, obj.applications.count())
    view_applications.short_description = "Applications"

    def get_list_display(self, request):
        return ("title", "category", "application_count", "view_applications", "is_active", "created_at")


# ── Scheme Application ────────────────────────────────────────────────────────
@admin.register(FarmerSchemeApplication, site=govt_admin_site)
class SchemeApplicationGovtAdmin(admin.ModelAdmin):
    list_display   = ("farmer_name", "scheme_name", "status_badge", "profile_score",
                      "has_docs", "applied_at", "view_farmer_profile")
    list_filter    = ("status", "scheme")
    search_fields  = ("farmer__full_name", "farmer__mobile", "scheme__title")
    list_per_page  = 20
    ordering       = ("-applied_at",)
    readonly_fields = ("applied_at", "farmer_profile_summary")

    fieldsets = (
        ("Application", {"fields": ("farmer", "scheme", "status", "notes", "applied_at")}),
        ("Farmer Profile Summary", {"fields": ("farmer_profile_summary",)}),
    )

    def farmer_name(self, obj):
        return format_html('<b>{}</b><br><small style="color:#888">{}</small>',
                           obj.farmer.full_name, obj.farmer.mobile)
    farmer_name.short_description = "Farmer"

    def scheme_name(self, obj):
        return obj.scheme.title
    scheme_name.short_description = "Scheme"

    def status_badge(self, obj):
        colors = {
            "pending":  ("#f39c12", "⏳"),
            "approved": ("#27ae60", "✅"),
            "rejected": ("#e74c3c", "❌"),
            "under_review": ("#2980b9", "🔍"),
        }
        color, icon = colors.get(obj.status, ("#888", "•"))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:.82rem">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def profile_score(self, obj):
        try:
            s = obj.farmer.profile_details.score()
            color = "#27ae60" if s >= 80 else "#f39c12" if s >= 50 else "#e74c3c"
            return format_html('<b style="color:{}">{}/100</b>', color, s)
        except Exception:
            return "—"
    profile_score.short_description = "Profile Score"

    def has_docs(self, obj):
        try:
            p = obj.farmer.profile_details
            docs = []
            if p.has_aadhar:   docs.append("🪪")
            if p.has_pan:      docs.append("🗂️")
            if p.has_land_record: docs.append("🗺️")
            if p.has_bank_account: docs.append("🏦")
            if p.has_income_cert: docs.append("📄")
            if p.has_ration_card: docs.append("🧾")
            return format_html('<span title="Docs available">{}</span>', " ".join(docs) or "—")
        except Exception:
            return "—"
    has_docs.short_description = "Docs"

    def view_farmer_profile(self, obj):
        url = f"../farmer-profile/{obj.farmer.pk}/"
        return format_html('<a class="button" href="{}">👤 Full Profile</a>', url)
    view_farmer_profile.short_description = "Profile"

    def farmer_profile_summary(self, obj):
        try:
            p = obj.farmer.profile_details
        except Exception:
            return "No profile data available."
        rows = [
            ("Aadhaar", p.aadhar_number or "—", p.has_aadhar),
            ("PAN", p.pan_number or "—", p.has_pan),
            ("Bank", f"{p.bank_name} / {p.account_number} / {p.ifsc_code}" if p.has_bank_account else "—", p.has_bank_account),
            ("Land Record No.", p.land_record_number or "—", p.has_land_record),
            ("Income Cert No.", p.income_cert_number or "—", p.has_income_cert),
            ("Caste Cert No.", p.caste_cert_number or "—", p.has_caste_cert),
            ("Ration Card No.", p.ration_card_number or "—", p.has_ration_card),
            ("Annual Income", p.annual_income or "—", bool(p.annual_income)),
            ("Caste Category", p.caste_category or "—", bool(p.caste_category)),
            ("Email", p.email or "—", bool(p.email)),
        ]
        html = '<table style="width:100%;border-collapse:collapse;">'
        html += '<tr style="background:#e8f5e9"><th style="padding:6px 10px;text-align:left">Field</th><th style="padding:6px 10px;text-align:left">Value</th><th style="padding:6px 10px">Available</th></tr>'
        for label, val, avail in rows:
            tick = "✅" if avail else "❌"
            html += f'<tr style="border-bottom:1px solid #e0e0e0"><td style="padding:6px 10px;color:#555">{label}</td><td style="padding:6px 10px;font-weight:600">{val}</td><td style="padding:6px 10px;text-align:center">{tick}</td></tr>'
        html += '</table>'
        return mark_safe(html)
    farmer_profile_summary.short_description = "Profile Data"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("farmer-profile/<int:farmer_id>/",
                 self.admin_site.admin_view(self.farmer_profile_view),
                 name="govt_farmer_profile"),
            path("update-status/<int:app_id>/",
                 self.admin_site.admin_view(self.update_status_view),
                 name="govt_update_status"),
        ]
        return custom + urls

    def farmer_profile_view(self, request, farmer_id):
        farmer = get_object_or_404(FarmerRegistration, pk=farmer_id)
        try:
            profile = farmer.profile_details
        except Exception:
            profile = None
        lands = farmer.lands.all()
        applications = farmer.scheme_applications.select_related("scheme").order_by("-applied_at")
        context = {
            **self.admin_site.each_context(request),
            "farmer": farmer,
            "profile": profile,
            "lands": lands,
            "applications": applications,
            "title": f"Farmer Profile — {farmer.full_name}",
        }
        return render(request, "admin/govt/farmer_profile.html", context)

    def update_status_view(self, request, app_id):
        if request.method == "POST":
            app = get_object_or_404(FarmerSchemeApplication, pk=app_id)
            new_status = request.POST.get("status")
            notes = request.POST.get("notes", "")
            valid = [s[0] for s in FarmerSchemeApplication.STATUS_CHOICES]
            if new_status in valid:
                app.status = new_status
                app.notes = notes
                app.save()
                messages.success(request, f"Status updated to '{app.get_status_display()}' for {app.farmer.full_name}")
        return redirect(request.META.get("HTTP_REFERER", "../"))


# ── Farmer Profile ────────────────────────────────────────────────────────────
@admin.register(FarmerProfile, site=govt_admin_site)
class FarmerProfileGovtAdmin(admin.ModelAdmin):
    list_display   = ("farmer_name", "score_bar", "aadhar_status", "pan_status",
                      "land_status", "bank_status", "income_status", "ration_status", "updated_at")
    search_fields  = ("farmer__full_name", "farmer__mobile")
    list_filter    = ("has_aadhar", "has_pan", "has_land_record", "has_bank_account",
                      "has_income_cert", "has_ration_card")
    list_per_page  = 20
    readonly_fields = ("updated_at", "doc_preview_section")

    fieldsets = (
        ("Farmer", {"fields": ("farmer",)}),
        ("Personal Documents", {"fields": (
            "has_aadhar", "aadhar_number", "aadhar_doc",
            "has_pan", "pan_number", "pan_doc",
        )}),
        ("Bank Details", {"fields": (
            "has_bank_account", "bank_name", "account_number", "ifsc_code",
        )}),
        ("Land Documents", {"fields": (
            "has_land_record", "land_record_number", "land_record_doc",
            "has_soil_health_card", "soil_health_card_number", "soil_health_card_doc",
        )}),
        ("Income & Category", {"fields": (
            "annual_income", "has_income_cert", "income_cert_number", "income_cert_doc",
            "caste_category", "has_caste_cert", "caste_cert_number", "caste_cert_doc",
        )}),
        ("Other", {"fields": (
            "email", "has_ration_card", "ration_card_number", "ration_card_doc",
            "has_photo", "farmer_photo",
        )}),
        ("Document Previews", {"fields": ("doc_preview_section",)}),
        ("Metadata", {"fields": ("updated_at",)}),
    )

    def farmer_name(self, obj):
        name = obj.farmer.full_name
        mobile = obj.farmer.mobile
        return mark_safe(f'<b>{name}</b><br><small style="color:#888">{mobile}</small>')
    farmer_name.short_description = "Farmer"

    def score_bar(self, obj):
        s = obj.score()
        color = "#27ae60" if s >= 80 else "#f39c12" if s >= 50 else "#e74c3c"
        html = (
            f'<div style="display:flex;align-items:center;gap:6px">'
            f'<div style="width:80px;background:#eee;border-radius:10px;height:10px;overflow:hidden">'
            f'<div style="width:{s}%;background:{color};height:100%;border-radius:10px"></div></div>'
            f'<b style="color:{color}">{s}</b></div>'
        )
        return mark_safe(html)
    score_bar.short_description = "Score"

    def _doc_icon(self, has, number=None, doc=None):
        if has:
            detail = number or ("📎" if doc else "")
            return mark_safe(f'<span style="color:#27ae60">✅ {detail}</span>')
        return mark_safe('<span style="color:#ccc">—</span>')

    def aadhar_status(self, obj):  return self._doc_icon(obj.has_aadhar, obj.aadhar_number, obj.aadhar_doc)
    def pan_status(self, obj):     return self._doc_icon(obj.has_pan, obj.pan_number, obj.pan_doc)
    def land_status(self, obj):    return self._doc_icon(obj.has_land_record, obj.land_record_number, obj.land_record_doc)
    def bank_status(self, obj):    return self._doc_icon(obj.has_bank_account, obj.account_number)
    def income_status(self, obj):  return self._doc_icon(obj.has_income_cert, obj.income_cert_number, obj.income_cert_doc)
    def ration_status(self, obj):  return self._doc_icon(obj.has_ration_card, obj.ration_card_number, obj.ration_card_doc)

    aadhar_status.short_description = "Aadhaar"
    pan_status.short_description    = "PAN"
    land_status.short_description   = "Land"
    bank_status.short_description   = "Bank"
    income_status.short_description = "Income"
    ration_status.short_description = "Ration"

    def doc_preview_section(self, obj):
        docs = [
            ("Aadhaar", obj.aadhar_doc),
            ("PAN", obj.pan_doc),
            ("Land Record", obj.land_record_doc),
            ("Soil Health Card", obj.soil_health_card_doc),
            ("Income Certificate", obj.income_cert_doc),
            ("Caste Certificate", obj.caste_cert_doc),
            ("Ration Card", obj.ration_card_doc),
            ("Passport Photo", obj.farmer_photo),
        ]
        html = '<div style="display:flex;flex-wrap:wrap;gap:16px;margin-top:8px;">'
        for label, doc in docs:
            if doc:
                html += (
                    f'<div style="text-align:center">'
                    f'<img src="{doc.url}" style="width:100px;height:100px;object-fit:cover;border-radius:8px;border:2px solid #c8e6c9;" alt="{label}">'
                    f'<div style="font-size:.75rem;color:#555;margin-top:4px">{label}</div>'
                    f'<a href="{doc.url}" target="_blank" style="font-size:.72rem;color:#2e7d32">View Full</a>'
                    f'</div>'
                )
        html += '</div>'
        if html == '<div style="display:flex;flex-wrap:wrap;gap:16px;margin-top:8px;"></div>':
            return "No documents uploaded yet."
        return mark_safe(html)
    doc_preview_section.short_description = "Uploaded Documents"


# ── Scheme Notification ───────────────────────────────────────────────────────
@admin.register(SchemeNotification, site=govt_admin_site)
class SchemeNotifGovtAdmin(admin.ModelAdmin):
    list_display  = ("title", "farmer", "scheme", "notif_type", "is_read", "created_at")
    list_filter   = ("notif_type", "is_read")
    search_fields = ("title", "farmer__full_name", "scheme__title")
    list_editable = ("is_read",)
    list_per_page = 25
    readonly_fields = ("created_at",)
