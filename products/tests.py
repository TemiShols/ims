from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal
from .models import Product, Supplier, Inventory
from django.core.files.uploadedfile import SimpleUploadedFile


class ProductAPITests(APITestCase):
    def setUp(self):
        # Create test supplier
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_info="test@supplier.com"
        )

        # Create test product
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal("99.99"),
            supplier=self.supplier
        )

        # URLs
        self.list_create_url = reverse('product-list-create')
        self.detail_url = reverse('product-detail', kwargs={'pk': self.product.pk})

    def test_create_product(self):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': '199.99',
            'supplier': self.supplier.id,
            'supplier_id': self.supplier.id
        }

        # Print the response data to debug validation errors
        response = self.client.post(self.list_create_url, data, format='json')#

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        new_product = Product.objects.get(name='New Product')
        self.assertEqual(new_product.price, Decimal('199.99'))

    def test_list_products(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Check pagination

    def test_retrieve_product(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_update_product(self):
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': '299.99',
            'supplier': self.supplier.id,
            'supplier_id': self.supplier.id
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(id=self.product.id).name, 'Updated Product')

    def test_delete_product(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)


class SupplierAPITests(APITestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_info="test@supplier.com"
        )
        self.list_create_url = reverse('supplier-list-create')
        self.detail_url = reverse('supplier-detail', kwargs={'pk': self.supplier.pk})

    def test_create_supplier(self):
        data = {
            'name': 'New Supplier',
            'contact_info': 'new@supplier.com'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 2)

    def test_list_suppliers(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_supplier(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Supplier')

    def test_update_supplier(self):
        data = {
            'name': 'Updated Supplier',
            'contact_info': 'updated@supplier.com'
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Supplier.objects.get(id=self.supplier.id).name, 'Updated Supplier')

    def test_delete_supplier(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Supplier.objects.count(), 0)


class InventoryAPITests(APITestCase):
    def setUp(self):
        # Create test data
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_info="test@supplier.com"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=Decimal("99.99"),
            supplier=self.supplier
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=10
        )
        self.inventory_url = reverse('inventory-update')

    def test_get_inventory(self):
        response = self.client.get(self.inventory_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_inventory(self):
        data = {
            'product_id': self.product.id,
            'quantity': 20
        }
        response = self.client.post(self.inventory_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Inventory.objects.get(product=self.product).quantity, 20)


class FileUploadTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('file-upload')
        self.csv_content = b"name,description,price,supplier\nTest Product,Test Description,99.99,1"

    def test_upload_csv(self):
        file = SimpleUploadedFile(
            "test.csv",
            self.csv_content,
            content_type="text/csv"
        )

        response = self.client.post(
            self.upload_url,
            {'file': file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue('task_id' in response.data)

    def test_upload_non_csv(self):
        file = SimpleUploadedFile(
            "test.txt",
            b"This is not a CSV",
            content_type="text/plain"
        )

        response = self.client.post(
            self.upload_url,
            {'file': file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_no_file(self):
        response = self.client.post(self.upload_url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
