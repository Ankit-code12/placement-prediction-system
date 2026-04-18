from django.urls import path
from . import views

urlpatterns = [
    # Root URL - Login page khulega
    path('', views.login_view, name='login'),
    
    # Auth URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main Pages (Login required)
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('compare/', views.compare, name='compare'),
    path('change-password/', views.change_password, name='change_password'),
    
    # APIs
    path('predict/api/', views.predict_api, name='predict_api'),
    path('compare/api/', views.compare_api, name='compare_api'),
    path('set-dark-mode/', views.set_dark_mode, name='set_dark_mode'),
    
    # Export
    path('download-report/', views.download_report, name='download_report'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('share-result/', views.share_result_api, name='share_result_api'),
]