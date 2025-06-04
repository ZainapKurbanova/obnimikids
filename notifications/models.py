from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    subscription_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Подписка на уведомления"
        verbose_name_plural = "Подписки на уведомления"

    def __str__(self):
        return f"Подписка для {self.user.email}"
