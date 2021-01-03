from django.contrib import admin
from django.urls import path, include

from pages.views import home_view

urlpatterns = [
    path('courses/', include('courses.urls')),
    path('blog/', include('blog.urls')),
    path('products/', include('products.urls')),
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
]
