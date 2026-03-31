from django.contrib.admin import AdminSite
from django.contrib import admin
from django.template.response import TemplateResponse
from .models import Buyer, BuyRequest


class BuyerAdminSite(AdminSite):
    site_header  = "KisanBazaar Buyer Admin"
    site_title   = "Buyer Admin"
    index_title  = "Buyer Management Panel"
    site_url     = "/buyer/dashboard/"
    index_template     = "admin/buyer_admin/buyer_dashboard.html"
    base_site_template = "admin/buyer_admin/base_site.html"

    def index(self, request, extra_context=None):
        ctx = self.each_context(request)
        ctx.update({
            "title": self.index_title,
            "total_buyers":    Buyer.objects.count(),
            "active_buyers":   Buyer.objects.filter(is_active=True).count(),
            "total_requests":  BuyRequest.objects.count(),
            "accepted_count":  BuyRequest.objects.filter(status="accepted").count(),
            "pending_count":   BuyRequest.objects.filter(status="pending").count(),
            "recent_buyers":   Buyer.objects.order_by("-created_at")[:6],
            "recent_requests": BuyRequest.objects.select_related("crop","buyer").order_by("-created_at")[:6],
        })
        if extra_context:
            ctx.update(extra_context)
        return TemplateResponse(request, self.index_template, ctx)


buyer_admin_site = BuyerAdminSite(name="buyer_admin")


@admin.register(Buyer, site=buyer_admin_site)
class BuyerModelAdmin(admin.ModelAdmin):
    list_display   = ("full_name", "mobile", "company", "interested_crops", "is_active", "created_at")
    list_filter    = ("is_active",)
    search_fields  = ("full_name", "mobile", "interested_crops", "company")
    list_editable  = ("is_active",)
    list_per_page  = 25
    ordering       = ("-created_at",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Personal Info", {
            "fields": ("full_name", "mobile", "mobile_verified", "company")
        }),
        ("Buying Preferences", {
            "fields": ("interested_crops", "notes")
        }),
        ("Locations", {
            "fields": ("locations",)
        }),
        ("Status", {
            "fields": ("is_active", "created_at")
        }),
    )


@admin.register(BuyRequest, site=buyer_admin_site)
class BuyRequestModelAdmin(admin.ModelAdmin):
    list_display   = ("crop", "buyer", "quantity", "status", "created_at")
    list_filter    = ("status",)
    search_fields  = ("crop__name", "buyer__full_name", "buyer__mobile")
    list_editable  = ("status",)
    list_per_page  = 25
    ordering       = ("-created_at",)
    readonly_fields = ("created_at",)
