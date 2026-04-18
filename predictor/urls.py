from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='landing'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('predict/api/', views.predict_api, name='predict_api'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('compare/', views.compare, name='compare'),
    path('compare/api/', views.compare_api, name='compare_api'),
    path('register/', views.register_view, name='register'),
    
    # NEW URLs for Feature 7, 8, 9
    path('download-report/', views.download_report, name='download_report'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('share-result/', views.share_result_api, name='share_result_api'),
    
]