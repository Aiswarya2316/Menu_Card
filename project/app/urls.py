from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stafhome/', views.stafhome, name='stafhome'),  # ✅ Ensure it's correctly defined
    path('adminhome/', views.adminhome, name='adminhome'), 
    path('customerhome/', views.customerhome, name='customerhome'),  # ✅ Ensure it's correctly defined
    path("registerpatient/", views.customer_register, name="customer_register"),
    path("registerstaf/", views.seller_register, name="seller_register"),
    path("registeradmin/", views.admin_register, name="admin_register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path('add-menu/', views.add_menu_item, name='add_menu'),
    path("menu-edit/<int:item_id>/", views.edit_menu_item, name="edit_menu_item"),
    path("menu-delete/<int:item_id>/", views.delete_menu_item, name="delete_menu_item"),
    path('menu/', views.menu_list, name='menu_list'),
    path('about/', views.about, name='about'),
    path('menulist/', views.menulist, name='menulist'),
    path("order/<int:item_id>/", views.order_item, name="order_item"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("order-details/<int:order_id>/", views.order_details, name="order_details"),


   

]
