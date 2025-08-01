# email_scheduler/urls.py

from django.contrib import admin
from django.urls import path
from scheduler import views as scheduler_views
from django.contrib.auth import views as auth_views
from scheduler.auth_views import authorize, callback


urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/',
         auth_views.LoginView.as_view(template_name='scheduler/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='login'),
         name='logout'),
    path('signup/', scheduler_views.signup, name='signup'),

    # Root must be ONLY this:
    path('', scheduler_views.schedule_create, name='schedule_create'),
    
    path('auth/login/', scheduler_views.start_oauth, name='start_oauth'),
    path('auth/callback/', scheduler_views.oauth_callback, name='oauth_callback'),
#     path('getAtoken/', scheduler_views.oauth_callback, name='oauth_callback'),  # Changed

]    
