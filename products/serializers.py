from rest_framework import serializers
from .models import Product, Supplier, Inventory


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_info', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source="supplier",
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'supplier', 'supplier_id', 'created_at', 'updated_at']


class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_id', 'quantity', 'created_at', 'updated_at']