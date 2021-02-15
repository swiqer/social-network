from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.cache import cache_page

from posts.models import Group, Post, User, Follow
from posts.forms import PostForm, CommentForm


def index(request):
    post = Post.objects.select_related().all()
    paginator = Paginator(post, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page,
                                          "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    all_group_posts = group.posts.all()
    paginator = Paginator(all_group_posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page,
                                          "paginator": paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect("index")
    return render(request, "posts/new_post.html", {"form": form,
                                                   "title": "Новая запись",
                                                   "button": "Добавить"})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    posts_count = user_posts.count()
    paginator = Paginator(user_posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    # Кнопака подписаться/отписаться
    if request.user.is_anonymous:
        following = False
    elif Follow.objects.filter(user=request.user, author=user).exists():
        following = True
    else:
        following = False

    # Количество подписок у автора
    author_follow = Follow.objects.filter(user=user).count()

    # Количество подписчиков на автора
    followers = Follow.objects.filter(author=user).count()

    return render(request, "profile.html", {"page": page,
                                            "posts_count": posts_count,
                                            "paginator": paginator,
                                            "user_title": user.get_full_name(),
                                            "username": user,
                                            "following": following,
                                            "followers": followers,
                                            "author_follow": author_follow})


def post_view(request, username, post_id):
    user_post = get_object_or_404(Post,
                                  author__username=username,
                                  pk=post_id)
    comments = user_post.comments.all()
    posts_count = Post.objects.filter(author=user_post.author).count()
    form = CommentForm()

    if request.user.is_anonymous:
        following = False
    elif Follow.objects.filter(user=request.user,
                               author__username=username).exists():
        following = True
    else:
        following = False

    # Количество подписок у автора
    author_follow = Follow.objects.filter(user=user_post.author).count()

    # Количество подписчиков на автора
    followers = Follow.objects.filter(author=user_post.author).count()

    return render(request, "posts/post.html", {
        "post": user_post,
        "posts_count": posts_count,
        "user_title": user_post.author.get_full_name(),
        "username": user_post.author,
        "form": form,
        "comments": comments,
        "following": following,
        "followers": followers,
        "author_follow": author_follow
    })


def post_edit(request, username, post_id):
    user_post = get_object_or_404(Post,
                                  author__username=username,
                                  pk=post_id)
    if request.user != user_post.author:  # есть ли права на редактирование
        return redirect(reverse("post", kwargs={"username": username,
                                                "post_id": post_id}))
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=user_post)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.save()
        return redirect("post", username, post_id)
    return render(request, "posts/new_post.html",
                  {"form": form,
                   "test": user_post,
                   "title": "Редактировать запись",
                   "button": "Сохранить"
                   })


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.post = post
        new_form.author = request.user
        new_form.save()
    return redirect("post", username, post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "follow.html",
                  {"page": page,
                   "paginator": paginator,
                   })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(Follow, author__username=username).delete()
    return redirect("profile", username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/505.html", status=500)
