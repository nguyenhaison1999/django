from django.contrib import admin
from django.urls import path

from pages.views import home_view
from products.views import product_detail_view

urlpatterns = [
    path('', home_view, name='home'),
    path('product/', product_detail_view),
    path('admin/', admin.site.urls),
]
