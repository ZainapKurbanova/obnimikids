# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.utils import send_push_notification
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    domain = "https://obnimikids.ru"
    if created:
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            send_push_notification(
                user=admin,
                title=f"Новый заказ #{instance.id}",
                body=f"Новый заказ от {instance.user.email} на сумму {instance.get_total_with_delivery()}",
                url=f"{domain}/admin/orders/order/{instance.id}/change/"
            )
    else:
        send_push_notification(
            user=instance.user,
            title=f"Обновление заказа #{instance.id}",
            body=f"Статус вашего заказа изменён на: {instance.get_status_display()}",
            url=f"{domain}/accounts/profile/orders/{instance.id}/"
        )
