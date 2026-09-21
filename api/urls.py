from django.urls import path
from .views import  receive_food

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('receive_food', receive_food, name='receive_food'),

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
