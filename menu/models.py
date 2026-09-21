from django.db import models

# مدل‌های این اپلیکیشن را اینجا بسازید.



class mother_food(models.Model):
    """
    دسته‌بندی اصلی غذاها (غذای مادر).
    هر غذای مادر می‌تواند چندین ماده اولیه داشته باشد.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="نام",
        help_text="نام دسته‌بندی اصلی غذا"
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['-name']
        verbose_name = "غذای مادر"
        verbose_name_plural = "غذاهای مادر"



class FoodRawMaterial(models.Model):
    """
    مواد اولیه / محصولات غذایی.
    شامل اطلاعات قیمت، تخفیف، تصویر و داده‌های اضافی به‌صورت JSON.
    """

    created_at = models.DateTimeField(
        auto_now_add=True, null=True, blank=True,
        verbose_name="تاریخ ایجاد",
        help_text="زمانی که این رکورد ایجاد شده است"
    )
    updated_at = models.DateTimeField(
        auto_now=True, null=True, blank=True,
        verbose_name="تاریخ بروزرسانی",
        help_text="آخرین زمانی که این رکورد ویرایش شده است"
    )
    mother = models.ForeignKey(
        mother_food,
        on_delete=models.CASCADE,
        related_name='mother_food_id',
        blank=True, null=True,
        verbose_name="غذای مادر",
        help_text="دسته‌بندی اصلی که این ماده اولیه به آن تعلق دارد"
    )
    name = models.CharField(
        max_length=200, null=True, blank=True,
        verbose_name="نام",
        help_text="نام ماده اولیه یا محصول"
    )
    # داده‌های JSON
    data = models.JSONField(
        blank=True, null=True,
        verbose_name="داده‌های اضافی",
        help_text="اطلاعات تکمیلی به‌صورت JSON"
    )
    price = models.IntegerField(
        default=0, blank=True, null=True,
        verbose_name="قیمت",
        help_text="قیمت محصول (بدون تخفیف)"
    )
    image = models.ImageField(
        upload_to='static/food_images/', blank=True, null=True,
        verbose_name="تصویر",
        help_text="تصویر محصول"
    )
    details = models.CharField(
        max_length=2000, default='', blank=True, null=True,
        verbose_name="جزئیات",
        help_text="توضیحات تکمیلی درباره محصول"
    )
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, blank=True, null=True,
        verbose_name="تخفیف",
        help_text="درصد تخفیف محصول (۰ تا ۱۰۰)"
    )
    priority = models.IntegerField(
        default=0,
        verbose_name="اولویت",
        help_text="اولویت نمایش محصول (عدد بزرگ‌تر = اولویت بالاتر)"
    )
    is_new = models.BooleanField(
        default=False,
        verbose_name="محصول جدید",
        help_text="مشخص می‌کند که محصول جدید است یا نه"
    )

    def __str__(self):
        return str(self.price)

    def discounted_price(self):
        """
        قیمت پس از اعمال تخفیف را محاسبه می‌کند.
        اگر تخفیف صفر باشد، قیمت اصلی برگردانده می‌شود.
        """
        if self.discount > 0:
            discount_amount = (self.discount / 100) * self.price
            return self.price - discount_amount
        return self.price

    class Meta:
        ordering = ['-price']
        verbose_name = "ماده اولیه غذا"
        verbose_name_plural = "مواد اولیه غذا"



class RestaurantBranch(models.Model):
    """
    شعبه‌های رستوران.
    هر شعبه دارای نام، موقعیت مکانی و ظرفیت انبار است.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="نام شعبه",
        help_text="نام شعبه رستوران"
    )
    location = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="موقعیت مکانی",
        help_text="آدرس یا موقعیت شعبه"
    )
    capacity = models.DecimalField(
        max_digits=10, decimal_places=0, blank=True, null=True,
        verbose_name="ظرفیت انبار",
        help_text="حداکثر ظرفیت انبار این شعبه"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "شعبه رستوران"
        verbose_name_plural = "شعبه‌های رستوران"



class SoldOutStatus(models.Model):
    """
    وضعیت اتمام موجودی یک محصول در یک شعبه خاص.
    برای هر ترکیب (شعبه، محصول) یک رکورد نگه‌داری می‌شود.
    """

    branch = models.ForeignKey(
        RestaurantBranch,
        on_delete=models.CASCADE,
        related_name="sold_out_status",
        verbose_name="شعبه",
        help_text="شعبه‌ای که این وضعیت مربوط به آن است"
    )
    product = models.ForeignKey(
        FoodRawMaterial,
        on_delete=models.CASCADE,
        related_name="sold_out_product",
        verbose_name="محصول",
        help_text="محصولی که وضعیت اتمام برای آن ثبت می‌شود"
    )
    is_sold_out = models.BooleanField(
        default=False,
        verbose_name="تمام شده",
        help_text="مشخص می‌کند که محصول در این شعبه تمام شده است یا نه"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
        help_text="آخرین زمانی که وضعیت به‌روزرسانی شده است"
    )

    def __str__(self):
        return f"{self.branch.name} - {self.product.name} - {'تمام شده' if self.is_sold_out else 'موجود'}"

    class Meta:
        verbose_name = "وضعیت اتمام موجودی"
        verbose_name_plural = "وضعیت‌های اتمام موجودی"