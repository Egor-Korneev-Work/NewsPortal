from django.urls import path
# Импортируем созданное нами представление
from .views import PostsList, PostDetail, PostUpdate, PostDelete, PostCreate, CatogoryListView, subscribe
from . import views


urlpatterns = [

   path('', PostsList.as_view(), name = 'post_list'),
   path('<int:pk>', PostDetail.as_view(), name = 'post_detail'),
   path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('create/', PostCreate.as_view(), name='news_create'),
   path('categories/<int:pk>', CatogoryListView.as_view(), name='category_list'),
   path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
   path('unsubscribe/<int:pk>/', views.unsubscribe, name='unsubscribe'),

]