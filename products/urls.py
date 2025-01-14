from django.urls import path
from .views import (
    ProductListCreateAPIView,
    ProductDetailAPIView,
    SupplierListCreateAPIView,
    SupplierDetailAPIView,
    InventoryView,
    FileUploadView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Your API",
      default_version='v1',
      description="Inventory Management System API",
      terms_of_service="https://www.google.com/terms/",
      contact=openapi.Contact(email="tpsolesi@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    # Products
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

    # Suppliers
    path('suppliers/', SupplierListCreateAPIView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailAPIView.as_view(), name='supplier-detail'),

    # Inventory
    path('inventory/', InventoryView.as_view(), name='inventory-update'),
    # Csv file upload
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    #swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
