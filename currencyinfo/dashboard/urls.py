from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_excel/', views.generate_excel_report, name='generate_excel_report'),
    path('home', views.home,name='home'),
    path('checkdollar/', views.checkdollar, name='checkdollar'),
]

