from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import request
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from unicodedata import category

from .models import Post, PostCategory, Category
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .filters import PostFilter
from .forms import PostForm, SubscriptionForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin



class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = 'title'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'post.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context

    def news_list(request):
        # Получаем все новости, отсортированные по дате публикации (от более свежей к самой старой)
        news = Post.objects.filter(post_type='news').order_by('-created_at')
        return render(request, 'post.html', {'news': news})

class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — product.html
    template_name = 'posts.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'posts'


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('NewsPortal.add_Post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/news/create/':
            post.post_type = 'news'
        elif self.request.path == '/articles/create/':
            post.post_type = 'article'
        post.save()
        return super().form_valid(form)

class PostUpdate(PermissionRequiredMixin, UpdateView,):
    permission_required = ('NewsPortal.change_Post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class CatogoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(categories= self.category).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id= pk)
    category.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку новостей категории'
    return redirect('category_list', pk=pk)

@login_required
def unsubscribe(request, pk):
    user = request.user
    category = get_object_or_404(Category, id=pk)  # безопаснее, чем .get()
    category.subscribers.remove(user)  # отписываем пользователя

    # Можно добавить сообщение (если используешь messages framework)
    from django.contrib import messages
    messages.success(request, f'Вы успешно отписались от категории "{category.name}"')
    return redirect('category_list', pk=pk)  # ← только если URL ожидает pk

