from django.contrib import admin
from django.utils.html import format_html

from .models import (
    mother_food,
    FoodRawMaterial,
    RestaurantBranch,
    SoldOutStatus,
)


# ============================================================
# غذای مادر
# ============================================================

@admin.register(mother_food)
class MotherFoodAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )

    list_per_page = 30

    # --------------------------------------------------------
    # برچسب‌های فارسی
    # --------------------------------------------------------
    def get_model_perms(self, request):
        return super().get_model_perms(request)


# ============================================================
# ماده اولیه غذا
# ============================================================

@admin.register(FoodRawMaterial)
class FoodRawMaterialAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "is_active",
        "image_preview",
        "foodsoft_id",
        "name",
        "mother",
        "price",
        "discount",
        "discounted_price_display",
        "priority",
        "is_new",
        "updated_at",
    )

    list_filter = (
        "mother",
        "is_new",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "details",
        "mother__name",
    )

    autocomplete_fields = (
        "mother",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
        "discounted_price_display",
    )

    fieldsets = (
        (
            "اطلاعات پایه",
            {
                "fields": (
                    "name",
                    "foodsoft_id",
                    "is_active",
                    "mother",
                    "image",
                    "details",
                )
            },
        ),

        (
            "قیمت‌گذاری",
            {
                "fields": (
                    "price",
                    "discount",
                    "discounted_price_display",
                )
            },
        ),

        (
            "تنظیمات محصول",
            {
                "fields": (
                    "priority",
                    "is_new",
                )
            },
        ),

        (
            "داده‌های JSON",
            {
                "fields": (
                    "data",
                ),
                "classes": (
                    "collapse",
                ),
                "description": (
                    "داده‌های اضافی محصول که به‌صورت JSON ذخیره می‌شود."
                ),
            },
        ),

        (
            "پیش‌نمایش تصویر",
            {
                "fields": (
                    "image_preview",
                ),
            },
        ),

        (
            "تاریخ‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    ordering = (
        "-priority",
        "-price",
    )

    list_per_page = 50

    # --------------------------------------------------------
    # پیش‌نمایش تصویر
    # --------------------------------------------------------

    @admin.display(description="تصویر")
    def image_preview(self, obj):

        if obj.image:
            return format_html(
                '<img src="static{}" '
                'style="'
                'width:80px;'
                'height:60px;'
                'object-fit:cover;'
                'border-radius:8px;'
                'border:1px solid #ddd;'
                '" />',
                obj.image.url,
            )

        return "بدون تصویر"

    # --------------------------------------------------------
    # قیمت نهایی (پس از تخفیف)
    # --------------------------------------------------------

    @admin.display(description="قیمت نهایی")
    def discounted_price_display(self, obj):

        if obj.price is None:
            return "-"

        try:
            final_price = obj.discounted_price()
        except Exception:
            return "-"

        if obj.discount and obj.discount > 0:

            return format_html(
                '<span style="'
                'color:#d32f2f;'
                'font-weight:bold;'
                '">'
                '{}'
                '</span>',
                f"{final_price:,.0f}",
            )

        return f"{final_price:,.0f}"


# ============================================================
# شعبه رستوران
# ============================================================

@admin.register(RestaurantBranch)
class RestaurantBranchAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "location",
        "capacity",
        "sold_out_count",
    )

    search_fields = (
        "name",
        "location",
    )

    list_filter = (
        "location",
    )

    ordering = (
        "name",
    )

    list_per_page = 30

    # --------------------------------------------------------
    # تعداد محصولات تمام‌شده
    # --------------------------------------------------------

    @admin.display(description="محصولات تمام‌شده")
    def sold_out_count(self, obj):

        return obj.sold_out_status.filter(
            is_sold_out=True
        ).count()


# ============================================================
# وضعیت اتمام موجودی
# ============================================================

@admin.register(SoldOutStatus)
class SoldOutStatusAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "branch",
        "product",
        "is_sold_out",
        "updated_at",
    )

    list_filter = (
        "branch",
        "is_sold_out",
        "updated_at",
    )

    search_fields = (
        "branch__name",
        "product__name",
    )

    autocomplete_fields = (
        "branch",
        "product",
    )

    readonly_fields = (
        "updated_at",
    )

    ordering = (
        "-updated_at",
    )

    list_per_page = 50