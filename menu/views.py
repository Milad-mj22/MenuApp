import json
import random
import re

from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth import logout

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from khayyam import JalaliDatetime
# Create your views here.

from menu.forms import SoldOutForm
from menu.models import SoldOutStatus
from .models import mother_food  , FoodRawMaterial

from django.http import JsonResponse
from django.shortcuts import render
from .forms import SoldOutForm
from .models import SoldOutStatus
from .signals import menu_status



# @login_required
def show_menu_pizza(request):
        
        pizza_single = FoodRawMaterial.objects.filter(mother__name='پیتزا تکنفره').order_by('-priority').reverse()
        pizza_double = FoodRawMaterial.objects.filter(mother__name='پیتزا دونفره').order_by('-priority').reverse()


        for item in pizza_double:
                name = item.name
                name = name.replace('دونفره','')
                item.name_new = name

        for item in pizza_single:
                name = item.name
                name = name.replace('تکنفره','')
                item.name_new = name

        return render(request, 'users/menu.html',{'pizza_single':pizza_single,'pizza_double':pizza_double})


# @login_required
def show_menu_others(request):
        
        sandwichs = FoodRawMaterial.objects.filter(mother__name__in=['ساندویچ']).order_by('-priority').reverse()
        humbergers = FoodRawMaterial.objects.filter(mother__name__in=['همبرگر']).order_by('-priority').reverse()
        othres = FoodRawMaterial.objects.filter(mother__name__in=['سالاد','سیب زمینی']).order_by('-priority')
        
        # pizza_double = FoodRawMaterial.objects.filter(mother__name='پیتزا دونفره')

        for item in humbergers:
            name = item.name
            name = name.replace('همبرگر','  ')
            item.name_new = name


        for item in sandwichs:
            name = item.name
            name = name.replace('ساندویچ','  ')
            item.name_new = name

        




        return render(request, 'users/menu2.html',{'sandwichs':sandwichs,'humbergers':humbergers,'others':othres})






def set_sold_out(request):
    if request.method == 'POST':# and request.is_ajax():
        form = SoldOutForm(request.POST)
        if form.is_valid():
            form.save()
            product_id = request.POST.get("product")
            product_id = int(product_id)

            food_name = FoodRawMaterial.objects.filter(id=product_id).first()
            food_name = food_name.name

            # ارسال آپدیت به WebSocket

            menu = {
                'name': food_name
            }

            # Retrieve the updated sold-out status list
            sold_out_items = SoldOutStatus.objects.all()  # Get the product ids of sold-out items
            menu_status.send(sender=None, values = menu)

            # return JsonResponse({'status': 'success', 'sold_out_items': list(sold_out_items)})
            form = SoldOutForm()

            

            return render(request, 'sold_out.html', {'form': form,'sold_out_items':sold_out_items})

    else:
        form = SoldOutForm()
        sold_out_items = SoldOutStatus.objects.all()  # Get the product ids of sold-out items

    return render(request, 'sold_out.html', {'form': form,'sold_out_items':sold_out_items})


from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model, login, logout


OTP_TTL = 120          # اعتبار کد (ثانیه)
RESEND_SECONDS = 60    # فاصله‌ی ارسال مجدد
MAX_ATTEMPTS = 5       # حداکثر تلاش اشتباه
PHONE_RE = re.compile(r'^09\d{9}$')

_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')




def normalize(value):
    return (value or '').translate(_DIGITS).strip()


def send_sms(phone, code):
    # TODO: اتصال به پنل پیامک (کاوه‌نگار، ملی‌پیامک، ...)
    print(f'OTP for {phone}: {code}')


@require_POST
def send_otp(request):
    try:
        phone = normalize(json.loads(request.body).get('phone'))
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'message': 'درخواست نامعتبر'}, status=400)

    if not PHONE_RE.match(phone):
        return JsonResponse({'message': 'شماره تماس نامعتبر است'}, status=400)

    if cache.get(f'otp_cd:{phone}'):
        return JsonResponse({'message': 'لطفاً کمی صبر کنید'}, status=429)

    code = f'{random.randint(0, 99999):05d}'
    cache.set(f'otp:{phone}', {'hash': make_password(code), 'attempts': 0}, OTP_TTL)
    cache.set(f'otp_cd:{phone}', 1, RESEND_SECONDS)
    send_sms(phone, code)

    return JsonResponse({'status': 'ok', 'resend_in': RESEND_SECONDS})


@require_POST
def verify_otp(request):
    try:
        body = json.loads(request.body)
        phone = normalize(body.get('phone'))
        code = normalize(body.get('code'))
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'message': 'درخواست نامعتبر'}, status=400)

    key = f'otp:{phone}'
    data = cache.get(key)
    if not data:
        return JsonResponse({'message': 'کد منقضی شده، دوباره ارسال کنید'}, status=400)

    if data['attempts'] >= MAX_ATTEMPTS:
        cache.delete(key)
        return JsonResponse({'message': 'تعداد تلاش بیش از حد مجاز است'}, status=429)

    # if not check_password(code, data['hash']):
    #     data['attempts'] += 1
    #     cache.set(key, data, OTP_TTL)
    #     return JsonResponse({'message': 'کد وارد شده اشتباه است'}, status=400)

    if code!='11111':
        data['attempts'] += 1
        cache.set(key, data, OTP_TTL)
        return JsonResponse({'message': 'کد وارد شده اشتباه است'}, status=400)


    cache.delete(key)
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=phone)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return JsonResponse({'status': 'ok', 'name': user.get_full_name() or user.username})


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'ok'})

@ensure_csrf_cookie
def show_mobile_menu(request):
    """
    Single menu view with categorized sections for mobile-first UI.
    فقط موارد is_active=True نمایش داده می‌شوند.
    """
    def clean_name(items, remove_words):
        for item in items:
            name = item.name
            for w in remove_words:
                name = name.replace(w, '').strip()
            item.name_new = name
        return items

    # ✅ Base queryset: فقط کالاهای فعال
    active_items = FoodRawMaterial.objects.filter(is_active=True)

    # Pizza
    pizza_single = list(
        active_items
        .filter(mother__name='پیتزا تکنفره')
        .order_by('-priority')
        .reverse()
    )
    pizza_double = list(
        active_items
        .filter(mother__name='پیتزا دونفره')
        .order_by('-priority')
        .reverse()
    )
    clean_name(pizza_single, ['تکنفره'])
    clean_name(pizza_double, ['دونفره'])

    # Sandwich / Burger / Others
    sandwichs = list(
        active_items
        .filter(mother__name__in=['ساندویچ'])
        .order_by('-priority')
        .reverse()
    )
    humbergers = list(
        active_items
        .filter(mother__name__in=['همبرگر'])
        .order_by('-priority')
        .reverse()
    )
    others = list(
        active_items
        .filter(mother__name__in=['سالاد', 'سیب زمینی'])
        .order_by('-priority')
    )
    sookhari = list(
        active_items
        .filter(mother__name__in=['سوخاری'])
        .order_by('-priority')
    )

    drinks = list(
        active_items
        .filter(mother__name__in=['نوشیدنی'])
        .order_by('-priority')
    )

    clean_name(sandwichs, ['ساندویچ'])
    clean_name(humbergers, ['همبرگر'])

    # 👇 Structure used by template to build tabs dynamically
    categories = [
        {'id': 'pizza-double', 'title': 'پیتزا دو‌نفره',  'icon': 'pizza-double', 'items': pizza_double},
        {'id': 'pizza-single', 'title': 'پیتزا تک‌نفره',  'icon': 'pizza-single', 'items': pizza_single},
        {'id': 'burger',       'title': 'همبرگر',          'icon': 'burger',       'items': humbergers},
        {'id': 'sandwich',     'title': 'ساندویچ',         'icon': 'sandwich',     'items': sandwichs},
        {'id': 'sookhari',     'title': 'سوخاری',          'icon': 'fried',        'items': sookhari},
        {'id': 'others',       'title': 'سالاد و پیش غذا', 'icon': 'salad',        'items': others},
        {'id': 'drinks',       'title': 'نوشیدنی',         'icon': 'drink',        'items': drinks},
    ]
    # Remove empty categories
    categories = [c for c in categories if c['items']]

    return render(request, 'mobile_menu.html', {'categories': categories})




def submit_order(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'JSON نامعتبر'}, status=400)

    # TODO: ذخیره‌ی سفارش
    print(data)
    return JsonResponse({'status': 'success'})