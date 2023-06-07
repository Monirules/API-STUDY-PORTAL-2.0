"""studentstudyportal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import auth
from django.urls import path, re_path
from django.urls.conf import include
from dashboard import views as dash_views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
#from django.conf.urls import url
from django.conf import settings
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from dashboard.views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('dashboard.urls')),
    #path('', include(router.urls)),
    path('api/', include(router.urls)),
    path('register/',dash_views.register,name="register"),
    path('login/',auth_views.LoginView.as_view(template_name="dashboard/login.html"),name="login"),
    path('profile/',dash_views.profile,name="profile"),
    path('wikidata/',dash_views.WikiData,name="wikidata"),
    path('fetch_books/', dash_views.fetch_books_from_api, name='fetch_books'),
    path('fetch/', dash_views.fetch_and_store_data, name='fetch_and_store_data'),
    path('logout/',auth_views.LogoutView.as_view(template_name="dashboard/logout.html"),name="logout"),
    #path('complain', dash_views.complain, name="complain"),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})
]

handler404 = 'dashboard.views.error_404'
handler500 = 'dashboard.views.error_500'