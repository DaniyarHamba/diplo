from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('registration/', views.SignUpView.as_view(), name='registration'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('main/', views.MainPage.as_view(), name='mainpage'),
    path('posts/', views.PostList.as_view(), name='post_list'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    path('profile/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('cp/', views.UserPasswordChangeView.as_view(), name='change_password'),
    path('comment/<int:pk>/edit/', views.CommentUpdate.as_view(), name='comment_edit'),
    path('comment/<int:pk>/delete/', views.CommentDelete.as_view(), name='comment_delete'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('video/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('video/create/', views.VideoCreateView.as_view(),name='video_create'),
    path('stream/<int:pk>/', views.get_streaming_video, name='stream'),
    path('video/<int:pk>/update/', views.VideoUpdateView.as_view(), name='video_update'),
    path('video/<int:pk>/delete/', views.VideoDeleteView.as_view(), name='video_delete'),
    path('password_change/done/', views.BPasswordChangeDoneView.as_view(), name='password_change_done')
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
