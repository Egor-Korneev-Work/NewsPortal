from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Category
from .tasks import send_notification_to_subscribers

@receiver(post_save, sender=Post)
def send_email_on_new_post(sender, instance, created, **kwargs):
    if created:
        send_notification_to_subscribers.delay(instance.id)# Только при создании нового поста



        # # Получаем все категории поста через промежуточную модель PostCategory
        # categories = instance.categories.all()
        #
        # # Собираем всех уникальных подписчиков этих категорий
        # subscribers = set()
        # for category in categories:
        #     subscribers.update(category.subscribers.all())
        #
        # # Отправляем письмо каждому подписчику
        # for user in subscribers:
        #     if user.email:  # Убедимся, что email указан
        #         send_mail(
        #             subject=f'Новая публикация в категории "{category.name}"',
        #             message=f'Здравствуйте, {user.username}!\n\n'
        #                     f'В категории "{category.name}" вышла новая статья: "{instance.title}".\n'
        #                     f'Прочитать можно здесь: http://127.0.0.1:8000{instance.get_absolute_url()}\n\n'
        #                     f'С уважением, Администрация портала',
        #             from_email=settings.DEFAULT_FROM_EMAIL,
        #             recipient_list=[user.email],
        #         )