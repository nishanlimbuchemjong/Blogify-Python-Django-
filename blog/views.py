from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Post, Like, Category, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
import json

def LandingPage(request):
    return render(request, 'landing_page.html')


def CategoryList(request):
    categories = Category.objects.all()
    print(" categories:",categories)
    return render(request, 'category_list.html', {'categories':categories})


def CategoryPosts(request, category_id):
    # Get the category based on the ID
    category = get_object_or_404(Category, id=category_id)

    # Filter posts by the category
    posts = Post.objects.filter(category=category)

    # Render the posts to the template
    return render(request, 'category_posts.html', {'category': category, 'posts': posts})


# def PostDetails(request, post_id):
#     # Retrieve the post by its ID
#     post = get_object_or_404(Post, id=post_id)
#
#     # Render the post details page
#     return render(request, 'post_detail.html', {'post': post})

@login_required
def PostDetails(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)

    # Fetch all comments for the post
    comments = post.comments.all()

    # Fetch like status
    user_like = post.likes.filter(user=request.user, is_like=True).exists()
    like_count = post.likes.filter(is_like=True).count()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'user_like': user_like,
        'like_count': like_count,
    })




@login_required
def toggle_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        like_obj, created = Like.objects.get_or_create(post=post, user=user)

        if like_obj.is_like:
            like_obj.is_like = False  # Unlike
            action = 'unliked'
        else:
            like_obj.is_like = True  # Like
            action = 'liked'

        like_obj.save()

        return JsonResponse({
            "like_count": post.likes.filter(is_like=True).count(),
            "user_like": like_obj.is_like,
        })

    return HttpResponse("Invalid request method.", status=405)

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            post = get_object_or_404(Post, id=post_id)

            if content:
                comment = Comment.objects.create(
                    post=post,
                    author=request.user,
                    content=content
                )
                return JsonResponse({
                    "author": comment.author.first_name,
                    "content": comment.content,
                })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return HttpResponse("Invalid request method.", status=405)