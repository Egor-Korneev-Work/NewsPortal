from celery import shared_task
from django.core.mail import send_mail
from .models import PostCategory, Post
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_notifications(post_id):
    post = Post.objects.get(id=post_id)
    subscriptions = PostCategory.objects.filter(category=post.category)
    for subscription in subscriptions:
        send_mail(
            'Новая статья в категории',
            f'В категории {post.category.name} появилась новая статья: {post.title}.',
            'Egor-Fivegor@yandex.ru',
            [subscription.user.email],
            fail_silently=False,
        )

@shared_task
def send_weekly_notifications():
    one_week_ago = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=one_week_ago)
    subscriptions = PostCategory.objects.all()
    for subscription in subscriptions:
        user_posts = posts.filter(category=subscription.category)
        if user_posts.exists():
            subject = 'Новые статьи в категории'
            message = f'В категории {subscription.category.name} появились новые статьи:\n'
            for post in user_posts:
                message += f'- {post.title}: {post.get_absolute_url()}\n'
            send_mail(
                subject,
                message,
                'Egor-Fivegor@yandex.ru',
                [subscription.user.email],
                fail_silently=False,
            )