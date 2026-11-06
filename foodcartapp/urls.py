from django.urls import include, path

from .views import banners_list_api, product_list_api, register_order

app_name = "foodcartapp"

urlpatterns = [
    path("products/", product_list_api),
    path("banners/", banners_list_api),
    path("order/", register_order),
    path("api-auth/", include("rest_framework.urls")),
]
