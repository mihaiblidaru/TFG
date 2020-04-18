from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('open_session/', views.open_session, name='open_session'),
    path('host/<slug:slug>/', views.show_host, name='show_host'),
    path('host/<slug:slug>/add_subscription/', views.add_subscription, name='add_subscription'),
    path('host/<slug:slug>/del_subscription/<int:sub_id>', views.del_subscription, name='del_subscription')
]