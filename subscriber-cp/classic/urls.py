from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('host/<slug:slug>/', views.show_host, name='show_host')
    # path('articles/<int:year>/', views.year_archive),
    # path('articles/<int:year>/<int:month>/', views.month_archive),
    # path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail),
]