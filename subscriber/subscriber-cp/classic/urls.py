from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('open_session/', views.open_session, name='open_session'),
    path('open_session/<int:known_host_id>/', views.open_session, name='open_session_known_host'),
    path('delete_known_host/<int:known_host_id>/', views.delete_known_host, name='delete_known_host'),
    path('host/<slug:slug>/', views.show_host, name='show_host'),
    path('host/<int:session_id>/add_subscription/', views.add_subscription, name='add_subscription'),
    path('host/<int:session_id>/close_session/', views.close_session, name='close_session'),
    path('host/<slug:slug>/del_subscription/<int:sub_id>', views.del_subscription, name='del_subscription')
]
