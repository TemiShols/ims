import csv
import io
from .models import Product, Inventory, Supplier
from celery import shared_task
from django.conf import settings
import logging
from django.core.mail import send_mail


@shared_task
def process_csv_file(file_content, encoding='utf-8'):
    results = {
        'processed': 0,
        'errors': []
    }

    try:
        csv_file = io.StringIO(file_content.decode(encoding))
        reader = csv.DictReader(csv_file)

        for row_num, row in enumerate(reader, start=1):
            try:
                supplier, _ = Supplier.objects.get_or_create(
                    name=row['supplier_name'],
                    defaults={'contact_info': row.get('supplier_contact', '')}
                )

                product, created = Product.objects.get_or_create(
                    name=row['product_name'],
                    supplier=supplier,
                    defaults={
                        'description': row.get('description', ''),
                        'price': float(row['price'])
                    }
                )

                if 'quantity' in row:
                    Inventory.objects.update_or_create(
                        product=product,
                        defaults={'quantity': int(row['quantity'])}
                    )

                results['processed'] += 1

            except Exception as e:
                results['errors'].append(f"Row {row_num}: {str(e)}")

        return results

    except Exception as e:
        results['errors'].append(f"File processing error: {str(e)}")
        return results


logger = logging.getLogger(__name__)


@shared_task
def send_low_stock_alert(product_name, supplier_name, quantity):
    message = (
        f"The product '{product_name}' supplied by '{supplier_name}' has low stock.\n"
        f"Current quantity: {quantity}."
    )
    try:
        send_mail(
            subject='Low Stock Alert',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['t.solesi@fusioncl.com'],
        )
    except Exception as e:
        logger.error(f"Failed to send low stock alert email for {product_name}: {str(e)}")
