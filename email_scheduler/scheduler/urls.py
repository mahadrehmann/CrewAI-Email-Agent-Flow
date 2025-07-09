from django.urls import path
from .views import schedule_create

urlpatterns = [
    path('', schedule_create, name='schedule_create'),
]
