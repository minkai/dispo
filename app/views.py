from rest_framework.decorators import api_view
from .models import *
from django.contrib.auth import login
from django.db.models import Count
from django.http import HttpResponse, JsonResponse


@api_view(["POST"])
def create_user(request):
    if request.POST:
        new_user = User(username=request.POST["username"],
                        password=request.POST["password"])
        new_user.save()
        login(request, new_user)

        return HttpResponse(status=201)

    return HttpResponse(status=404)


@api_view(["POST"])
def create_post(request):
    if request.POST:
        # make sure user is logged in
        if request.user.is_authenticated:
            new_post = Post(body=request.POST["body"], user=request.user)
            new_post.save()

            return HttpResponse(status=201)

    return HttpResponse(status=404)


def get_top_users(request):
    query = User.objects.annotate(post_count=Count("posts", distinct=True))
    query = query.filter(post_count__gt=0)
    query = query.order_by("-post_count")

    resp = []
    for user in list(query):
        resp.append({
            "username": user.username,
            "posts": user.post_count
        })

    return JsonResponse({"user_list": resp})

@api_view(["POST"])
def follow_user(request):
    if request.POST:
        user_obj = User.objects.get(pk=request.POST["user_id"])
        follow_obj = UserFollow(from_user=request.user,
                                to_user=user_obj)
        follow_obj.save()
        return HttpResponse(status=201)

    return HttpResponse(status=404)

def user_feed(request, **kwargs):
    if "user_id" in kwargs:
        uf_query = UserFollow.objects.filter(from_user__pk=kwargs["user_id"])
        uf_query = uf_query.values_list("to_user__pk", flat=True)
        user_list = list(uf_query)
        user_list.append(kwargs["user_id"])
        post_query = Post.objects.filter(user__pk__in=user_list)
        post_query = post_query.annotate(like_count=Count("liked_by", distinct=True))
        post_query = post_query.order_by("-like_count")

        resp = []
        for post in list(post_query):
            resp.append({
                "id": post.pk,
                "body": post.body,
                "author": post.user.username,
                "likes": post.like_count
            })
        return JsonResponse({"post_list": resp})

    return HttpResponse(status=404)
