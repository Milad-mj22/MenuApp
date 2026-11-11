from django.urls import path
from .views import  set_sold_out,submit_order, show_menu_others, show_menu_pizza, show_mobile_menu
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('pizza', show_menu_pizza, name='menu'),
    path('others', show_menu_others, name='menu'),
    path('sold-out', set_sold_out, name='set_sold_out'),
    path('mobile', show_mobile_menu, name='show_mobile_menu'),
    path('submit_order', submit_order, name='submit_order'),
    path('send-otp/',   views.send_otp,    name='send_otp'),
    path('/verify-otp/', views.verify_otp,  name='verify_otp'),
    path('logout/',     views.logout_view, name='logout'),
    path('', show_mobile_menu, name='show_mobile_menu'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
