from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from blob.view import (
    home_page, add_tracking_no,
    updated_orders,
    display_order,
    completed_orders,
    load_orders,
    remove_order,
    deleted_orders,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home_page'),
    path('deleted-orders', deleted_orders, name='deleted_orders'),
    path('updated-orders', updated_orders, name='updated_orders'),
    path('add-tracking-no', add_tracking_no, name='add_tracking_no'),
    path('completed-orders', completed_orders, name='completed_orders'),
    path('load-orders/<str:redirect_url>', load_orders, name='load_orders'),
    path('remove-order/<str:container>/<int:order_no>/<str:date>', remove_order, name='remove_order'),
    path('display-order/<str:container>/<int:order_no>/<str:date>', display_order, name='display_order'),
]

if not settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
