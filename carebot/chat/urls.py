from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('chat/', views.chat_view, name='chat'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('clear-session/', views.clear_session, name='clear_session'),
    path('about-us/', views.about_us_view, name='about-us'),
    path('deliverables/', views.deliverables_view, name='deliverables'),
    path('api/geolocation-data/', views.geolocation_data, name='geolocation_data'),
    path('api/table-data/', views.table_data, name='table-data'),
    path('documentation/', views.documentation_view, name='documentation'),
]
