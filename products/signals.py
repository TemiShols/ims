from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Inventory
from .tasks import send_low_stock_alert


@receiver(post_save, sender=Inventory)
def check_low_stock(sender, instance, **kwargs):
    if instance.quantity < 10:
        send_low_stock_alert.delay(
            product_name=instance.product.name,
            supplier_name=instance.product.supplier.name,
            quantity=instance.quantity
        )
