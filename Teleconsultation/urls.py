from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Home ),
    path('Consultaion/', views.Consultaion ),
    path('Results/', views.Results ),
    path('Learn/<Learn_id>', views.Learn ),
    path('Doctor/', views.Doctor ),
    path('Admin/', views.Admin ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)