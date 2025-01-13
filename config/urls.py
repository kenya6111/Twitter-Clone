from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from twitter_clone import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path("accounts/login/", views.login_view, name="account_login"),
    # path("accounts/logout/", views.logout_view, name="account_logout"),
    path('accounts/', include("allauth.urls")),
    path('', include('twitter_clone.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)