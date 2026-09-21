import json
import logging
import traceback

from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from menu.models import FoodRawMaterial

# Create your views here.
from .models import APIKey

logger = logging.getLogger(__name__)


def _authenticate(request):
    """اعتبارسنجی API Key"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return None, 'API Key ارائه نشده'
    
    try:
        key_obj = APIKey.objects.get(key=api_key, is_active=True)
        return key_obj, None
    except APIKey.DoesNotExist:
        return None, 'API Key نامعتبر است'


def _get_client_ip(request):
    """استخراج IP واقعی کلاینت (با در نظر گرفتن proxy)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')



@csrf_exempt
def receive_food(request):
    # اعتبارسنجی
    key_obj, error = _authenticate(request)
    if error:
        logger.warning(f"Auth failed: {error}")
        return JsonResponse({'success': False, 'error': error}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON نامعتبر'}, status=400)

    # اعتبارسنجی حداقلی
    required_fields = ['timestamp', 'count', 'changes']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return JsonResponse(
            {'success': False, 'error': f'فیلدهای الزامی: {", ".join(missing)}'},
            status=400
        )

    changes = data.get('changes', [])
    if not isinstance(changes, list):
        return JsonResponse(
            {'success': False, 'error': 'changes باید یک لیست باشد'},
            status=400
        )

    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []

    for c in changes:
        try:
            foodsoft_id = c.get('id')
            name = c.get('name', '')
            price = c.get('price', 0)
            price = price / 10000
            change_type = c.get('change_type', 'unknown')

            if foodsoft_id is None:
                skipped_count += 1
                logger.warning(f"رکورد بدون id رد شد: {c}")
                continue

            # جستجو بر اساس foodsoft_id
            try:
                obj = FoodRawMaterial.objects.get(foodsoft_id=int(foodsoft_id))
            except FoodRawMaterial.DoesNotExist:
                obj = None
            except FoodRawMaterial.MultipleObjectsReturned:
                # اگر چند رکورد با این id وجود دارد، اولین را می‌گیریم
                obj = FoodRawMaterial.objects.filter(
                    foodsoft_id=int(foodsoft_id)
                ).first()
                logger.warning(
                    f"چند رکورد با foodsoft_id={foodsoft_id} یافت شد"
                )

            if obj is None:
                # ---------- ایجاد رکورد جدید ----------
                obj = FoodRawMaterial.objects.create(
                    foodsoft_id=int(foodsoft_id),
                    name=name,
                    price=int(price) if price is not None else 0,
                )
                created_count += 1
                logger.info(
                    f"کالای جدید ساخته شد | id={foodsoft_id} | "
                    f"name={name} | price={price} | type={change_type}"
                )
            else:
                # ---------- به‌روزرسانی رکورد موجود ----------
                old_price = obj.price
                old_name = obj.name
                changed_fields = []

                new_price = int(price) if price is not None else 0
                if obj.price != new_price:
                    obj.price = new_price
                    changed_fields.append(f"price: {old_price} -> {new_price}")

                if name and obj.name != name:
                    obj.name = name
                    changed_fields.append(f"name: '{old_name}' -> '{name}'")

                if changed_fields:
                    obj.save(update_fields=['price', 'name', 'updated_at'])
                    updated_count += 1
                    logger.info(
                        f"کالا به‌روزرسانی شد | id={foodsoft_id} | "
                        f"تغییرات: {' | '.join(changed_fields)} | "
                        f"type={change_type}"
                    )
                else:
                    skipped_count += 1
                    logger.info(
                        f"کالا بدون تغییر | id={foodsoft_id} | "
                        f"name={name} | price={price}"
                    )

        except Exception as e:
            errors.append({
                'change': c,
                'error': str(e)
            })
            logger.error(f"خطا در پردازش تغییر {c}: {e}")
            logger.error(traceback.format_exc())

    # خروجی نهایی
    result = {
        'success': True,
        'created': created_count,
        'updated': updated_count,
        'skipped': skipped_count,
        'errors_count': len(errors),
    }

    logger.info(
        f"پردازش کامل شد | created={created_count} | "
        f"updated={updated_count} | skipped={skipped_count} | "
        f"errors={len(errors)}"
    )

    try:
        print(f'updated : {updated_count}')
        print(result)
    except Exception:
        pass

    if errors:
        result['errors'] = errors[:20]  # فقط 20 خطای اول برگردانده شود

    return JsonResponse(result, status=200)