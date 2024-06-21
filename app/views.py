from django.views.generic.edit import CreateView, FormMixin, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import SignUpForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, redirect
from .models import Profile, Post, Like, Dislike, Comment, Video
from django.http import StreamingHttpResponse
from django.views.generic.base import TemplateView
from .forms import PostForm, CommentForm, ProfileForm, UserForm, VideoForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .services import open_file
from django.contrib.auth.models import User


class VideoUpdateView(UserPassesTestMixin, UpdateView):
    model = Video
    form_class = VideoForm
    success_url = reverse_lazy('video_list')
    template_name = 'app/form_video.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class VideoDeleteView(UserPassesTestMixin, DeleteView):
    model = Video
    template_name = 'app/form_delete_video.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class VideoListView(ListView):
    model = Video
    context_object_name = 'videos'
    template_name = 'app/video_list.html'


class VideoDetailView(DetailView):
    model = Video
    context_object_name = 'video'
    template_name = 'app/video_detail.html'


class VideoCreateView(CreateView):
    model = Video
    form_class = VideoForm
    success_url = reverse_lazy('video_list')
    template_name = 'app/form_video.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def get_streaming_video(request, pk: int):
    file, status_code, content_length, content_range = open_file(request, pk)
    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')

    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range
    return response


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'account/change_password.html'
    success_url = '/'


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'account/profile.html'
    context_object_name = 'profile'

    def get_object(self, **kwargs):
        return get_object_or_404(Profile, username=self.request.user)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'account/form_acc.html'
    success_url = reverse_lazy('profile')

    def get_object(self, **kwargs):
        return get_object_or_404(Profile, username=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        if user_form.is_valid():
            user_form.save()
        else:
            return self.form_invalid(form)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.username != self.request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'


class UserLoginView(LoginView):
    template_name = 'login/log.html'
    success_url = reverse_lazy('profile')


class MainPage(TemplateView):
    template_name = 'main/navbar.html'


class CommentUpdate(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'app/form_comment.html'

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post_id.pk})

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDelete(DeleteView):
    model = Comment
    template_name = 'app/form_delete_comment.html'

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post_id.pk})

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'app/form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'app/post_list.html'
    paginate_by = 5
    paginate_orphans = 1


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'app/form_update_post.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'app/form_delete_post.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class UserLogoutView(LogoutView):
    success_url = reverse_lazy('login')

    def dispatch(self, request, **kwargs):
        response = super().dispatch(request)
        return redirect(self.success_url)


class PostDetail(LoginRequiredMixin, FormMixin, DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'app/post_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['likes_count'] = self.object.likes.count()
        context['dislikes_count'] = self.object.dislikes.count()
        context['user_has_liked'] = self.object.likes.filter(user=self.request.user).exists()
        context['user_has_disliked'] = self.object.dislikes.filter(user=self.request.user).exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'like' in request.POST:
            return self.like_post(request)
        elif 'dislike' in request.POST:
            return self.dislike_post(request)
        else:
            form = self.get_form()
            if form.is_valid():
                if request.user.is_authenticated:
                    comment = form.save(commit=False)
                    comment.post_id = self.object
                    comment.author = self.request.user
                    comment.save()
                    return redirect(self.get_success_url())
                else:
                    return redirect('login')
            else:
                return self.form_invalid(form)

    def like_post(self, request):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        Dislike.objects.filter(user=request.user, post=post).delete()
        return redirect(self.get_success_url())

    def dislike_post(self, request):
        post = self.get_object()
        dislike, created = Dislike.objects.get_or_create(user=request.user, post=post)
        if not created:
            dislike.delete()
        Like.objects.filter(user=request.user, post=post).delete()
        return redirect(self.get_success_url())
