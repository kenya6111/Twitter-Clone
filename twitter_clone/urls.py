from django.urls import path
from . import views

urlpatterns = [
    path('', views.top_view, name='top'),
    path("users/signup", views.signup_view, name="signup"),
    path('users/email_verify/', views.email_verify_view, name='email_verify'),
    path('users/password_input/', views.password_input_view, name='password_input'),
    path('main/', views.main_view, name='main'),
]
