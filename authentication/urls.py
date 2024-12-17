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
    path('view_user_leader/', views.view_user_leader, name='view_user_leader'),  
    path('add-task/', views.add_task, name='add-task'),
    path('delete-task/', views.delete_task, name='delete-task'),
    path('edit-task/', views.edit_task, name='edit-task'),
    path('edit-task-member/', views.edit_task_member, name='edit-task-member'),
    path('upload', views.upload_file, name='upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)