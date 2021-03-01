from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('target/', views.EliminationFormView.as_view(), name='target'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/',
         PasswordChangeView.as_view(template_name='change_password.html', success_url=reverse_lazy('target')),
         name='change_password'),
    path('email_settings/', views.ChangeMailSettingsView.as_view(), name='email_settings'),
]
