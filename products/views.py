from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product, Supplier, Inventory
from .serializers import ProductSerializer, SupplierSerializer, InventorySerializer
from .tasks import process_csv_file


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_description="List all products with pagination",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: ProductSerializer(many=True),
            400: "Bad Request"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new product",
        request_body=ProductSerializer,
        responses={
            201: ProductSerializer(),
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a specific product by its ID",
        responses={
            200: ProductSerializer(),
            404: "Product not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a specific product by its ID",
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer(),
            400: "Bad Request",
            404: "Product not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class SupplierListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating suppliers
    """
    queryset = Supplier.objects.all().order_by('id')
    serializer_class = SupplierSerializer

    @swagger_auto_schema(
        operation_description="List all suppliers",
        responses={200: SupplierSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new supplier",
        request_body=SupplierSerializer,
        responses={201: SupplierSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SupplierDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a supplier by ID",
        responses={200: SupplierSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a supplier",
        request_body=SupplierSerializer,
        responses={200: SupplierSerializer()}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a supplier",
        responses={204: "No content"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class InventoryView(APIView):

    @swagger_auto_schema(
        operation_description="Get inventory details",
        manual_parameters=[
            openapi.Parameter(
                'product_id',
                openapi.IN_QUERY,
                description="ID of the product to get inventory for",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: InventorySerializer(many=True),
            404: openapi.Response(
                description="Product not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def get(self, request):
        try:
            product_id = request.query_params.get('product_id')

            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response(
                        {'error': 'Product not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                inventory = Inventory.objects.filter(product=product).first()
                if not inventory:
                    return Response(
                        {'error': 'Inventory not found for this product'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                serializer = InventorySerializer(inventory)
                return Response(serializer.data, status=status.HTTP_200_OK)

            inventory = Inventory.objects.all()
            serializer = InventorySerializer(inventory, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred: ' + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update inventory quantity",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id', 'quantity'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: InventorySerializer(),
            400: "Bad Request",
            404: "Product not found"
        }
    )
    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity')

            if product_id is None or quantity is None:
                return Response(
                    {'error': 'Both product_id and quantity are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            inventory, created = Inventory.objects.get_or_create(
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                inventory.quantity = quantity
                inventory.save()

            serializer = InventorySerializer(inventory)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred: ' + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        operation_description="Upload a CSV file for processing",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='CSV file to upload'
            )
        ],
        responses={
            202: openapi.Response(
                description="Accepted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']

        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {'error': 'Only CSV files are supported'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_content = uploaded_file.read()
            task = process_csv_file.delay(file_content)

            return Response({
                'message': 'File processing started',
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
