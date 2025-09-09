# NewsPortal/management/commands/send_weekly_newsletter.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from NewsPortal.models import Post, Category, User  # ← замени NewsPortal на имя твоего приложения, если нужно

class Command(BaseCommand):
    help = 'Отправляет еженедельную рассылку подписчикам категорий'

    def handle(self, *args, **kwargs):
        # Получаем всех пользователей, подписанных хотя бы на одну категорию
        users = User.objects.filter(categories__isnull=False).distinct()

        for user in users:
            if not user.email:
                self.stdout.write(self.style.WARNING(f'У пользователя {user.username} нет email'))
                continue

            # Находим категории, на которые подписан пользователь
            categories = user.categories.all()

            # Находим все посты за последние 7 дней в этих категориях
            one_week_ago = timezone.now() - timezone.timedelta(days=7)
            posts = Post.objects.filter(
                categories__in=categories,
                created_at__gte=one_week_ago
            ).distinct()

            if posts.exists():
                # Генерируем HTML-письмо
                subject = "📰 Ваши новости за неделю"
                html_message = render_to_string('email/weekly_newsletter.html', {
                    'user': user,
                    'posts': posts,
                })
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL

                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=from_email,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f'Письмо отправлено {user.email}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка при отправке {user.email}: {e}'))
            else:
                self.stdout.write(self.style.NOTICE(f'Нет новых статей для {user.username}'))

        self.stdout.write(self.style.SUCCESS('Рассылка завершена.'))