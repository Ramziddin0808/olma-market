"""
URL configuration for market project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sayt.views import home_views,detail_views,add_malumot,delet,login_view,register_view,profil_views,logout_view,edit_market
from django.conf import settings
from django.conf.urls.static import static
from sayt import views  # To'g'ri yo'nalish

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home_views,name='home'),
    path("index/<int:pk>/",detail_views,name="market_detail"),
    path("add/",add_malumot,name='add_market'),
    path('delet/<int:id>/', delet, name='delet'),
    path('register/',register_view,name="register"),
    path('login/',login_view,name="login"),
    path('logout/', logout_view, name='logout'),
    path('profil/',profil_views,name='profil'),
    path('edit/<int:id>/',edit_market,name='edit_qilish'),
    path('saralangan/toggle/<int:pk>/', views.toggle_saralangan, name='toggle_saralangan'),
    path('saralanganlarim/', views.saralanganlar_sahifasi, name='saralanganlar_sahifasi'),
    path('ai-chat/', views.ai_chatbot, name='ai_chat'),
    path('savat/', views.savat_sahifasi, name='savat_sahifasi'),
    path('savat/qoshish/<int:pk>/', views.savatga_qoshish, name='savatga_qoshish'),
    path('savat/ochirish/<int:pk>/', views.savatdan_ochirish, name='savatdan_ochirish')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
