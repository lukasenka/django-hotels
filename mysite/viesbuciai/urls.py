from django.urls import path, include
from . import views
from .views import profile, register, my_orders, edit_order, orders, delete_hotel

urlpatterns = [
    path('', views.main_page, name='index'),
    path('hotels/', views.hotels, name='hotels'),
    path('reservation/', views.make_reservation, name='reservation'),
    path('create_order/<int:hotel_id>/', views.create_order, name='create_order'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('myorders/', my_orders, name='orders'),
    path('orders/', orders, name='orders_'),
    path('editorder/<int:pk>', edit_order, name='edit_order'),
    path('hotels/filter/', views.hotel_filter, name='hotel_filter'),
    path('hotels/<int:pk>/delete/', delete_hotel, name='delete_hotel'),
    path('add_balance/<int:user_id>', views.add_user_balance_view, name="add_balance"),
    path('users/', views.all_users_view, name="all_users"),
    path('addhotel', views.add_hotel_view, name="add_hotel")

]
