from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from paginaInicial.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('pontos/', include('registroDePontos.urls')),
    path('freelancers/', include('freelancers.urls')),
    path('escalas/', include('escalas.urls')),
    path('pagamentos/', include('pagamentos.urls')),
]
