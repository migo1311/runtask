from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('dashboard/', views.dashboard, name='dashboard'),  # For member dashboard
    path('dashboard_leader/', views.dashboard_leader, name='dashboard_leader'),  # For leader dashboard
    path('upload', views.upload_file, name='upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)