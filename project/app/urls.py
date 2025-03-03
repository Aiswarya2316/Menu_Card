from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stafhome/', views.stafhome, name='stafhome'),  # ✅ Ensure it's correctly defined
    path('adminhome/', views.adminhome, name='adminhome'), 
    path("registerpatient/", views.customer_register, name="customer_register"),
    path("registerstaf/", views.seller_register, name="seller_register"),
    path("registeradmin/", views.admin_register, name="admin_register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path('add-menu/', views.add_menu_item, name='add_menu'),
    path('menu/', views.menu_list, name='menu_list'),
   

]
