from annoying.decorators import ajax_request
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from Insta.models import InstaUser, Post, Like, Comment, UserConnection
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
 
from Insta.forms import CustomUserCreationForm

from django.contrib.auth.mixins import  LoginRequiredMixin

# Create your views here.
class HellowWorld(TemplateView):
    template_name = 'test.html'

class PostsView(ListView):
    model = Post
    template_name = 'index.html'
    login_url = "login"
    
    def get_queryset(self):
        current_user = self.request.user
        following = set()
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
            following.add(conn.following)
        return Post.objects.filter(author__in=following)

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        liked = Like.objects.filter(post=self.kwargs.get('pk'), user=self.request.user).first()
        if liked:
            data['liked'] = 1
        else:
            data['liked'] = 0
        return data

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "post_create.html"
    fields = ['title','image']#选中所有的fields
    login_url = 'login'#如果没有log in 跳转到‘login’

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(UpdateView):
    model = Post
    template_name = "post_update.html"
    fields = ['title']
    
class PostDeleteView(DeleteView):
    model = Post
    template_name = "post_delete.html"
    success_url = reverse_lazy("posts")

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

class UserDetailView(LoginRequiredMixin, DetailView):
    model = InstaUser
    template_name = 'user_detail.html'
    login_url = 'login'

class ProfileUpdate(LoginRequiredMixin,UpdateView):
    model = InstaUser
    template_name = 'user_update.html'
    fields = ['profile_pic', 'username']
    login_url = 'login'
    success_url = 'user_detail', 
    
    def get_success_url(self):
        return reverse('user_detail', args=(self.object.pk,))



class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'
    success_url = reverse_lazy('user_profile'      )

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]



# 定义了下面的函数可以独立作为一个view来响应ajax request而不需要引用一个HTML as template 
# 需哟安装Django annoying 并且在pipfile里声明 在此文件import

@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }


@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(comment=comment_text, user=request.user, post=post)
        comment.save()

        username = request.user.username

        commenter_info = {
            'username': username,
            'comment_text': comment_text
        }

        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }


@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator=current_user, following=follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                UserConnection.objects.filter(creator=current_user, following=follow_user).delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'type': request.POST.get('type'),
        'follow_user_pk': follow_user_pk
    }
