from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, User
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def send_notification_to_subscribers(post_id):
    """
    Асинхронная задача: отправить email всем подписчикам категорий поста
    """
    try:
        post = Post.objects.prefetch_related('categories__subscribers').get(id=post_id)
    except Post.DoesNotExist:
        return f"Post with id {post_id} not found"

    subject = f'Новая публикация: "{post.title}"'

    sent_count = 0
    errors = []

    # Проходим по всем категориям поста
    for category in post.categories.all():
        # Получаем всех подписчиков этой категории
        for subscriber in category.subscribers.all():
            if not subscriber.email:
                continue  # Пропускаем пользователей без email

            message = (
                f"Здравствуйте, {subscriber.username}!\n\n"
                f"В категории \"{category.name}\" вышла новая статья: \"{post.title}\".\n"
                f"Прочитать можно здесь: http://127.0.0.1:8000{post.get_absolute_url()}\n\n"
                f"С уважением, Администрация портала"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                errors.append(f"Ошибка при отправке на {subscriber.email}: {str(e)}")

    result = f"Уведомления отправлены: {sent_count} из {sum(c.subscribers.count() for c in post.categories.all())} подписчиков."
    if errors:
        result += "\nОшибки: " + "; ".join(errors)

    return result

@shared_task
def send_weekly_newsletter():
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