from django.contrib import admin
from django.urls import path
from signature_verification import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verification/', views.verification, name='verification'),
    path('result/', views.result_view, name='result'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
