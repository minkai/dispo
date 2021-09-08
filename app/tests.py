from django.test import TestCase
from django.test import Client
from django.urls import reverse_lazy

# Enable if debugging with IDE
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dispo.settings')
import django
django.setup()

from django.contrib.auth.models import User
from app.models import Post, PostLike

import json

# Create your tests here.
class CreatePostTestCase(TestCase):
    def test_create_post(self):
        client = Client()
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": "test_user1@gmail.com",
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        create_post_resp = client.post(reverse_lazy("create_post"),
                                       {
                                           "body": "test body"
                                       })
        self.assertEqual(create_post_resp.status_code, 201)

    def test_users_list(self):
        # Create a user with no post
        client = Client()
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": "test_user2_1@gmail.com",
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        # Create a user with 2 posts
        user2 = "test_user2_2@gmail.com"
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": user2,
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        create_post_resp = client.post(reverse_lazy("create_post"),
                                       {
                                           "body": "test body"
                                       })
        self.assertEqual(create_post_resp.status_code, 201)
        create_post_resp = client.post(reverse_lazy("create_post"),
                                       {
                                           "body": "test body2"
                                       })
        self.assertEqual(create_post_resp.status_code, 201)

        # Create a user with one post
        user3 = "test_user2_3@gmail.com"
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": user3,
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        create_post_resp = client.post(reverse_lazy("create_post"),
                                       {
                                           "body": "test body"
                                       })
        self.assertEqual(create_post_resp.status_code, 201)

        # User list should return user2 followed by user3
        get_top_users_resp = client.get(reverse_lazy("get_top_users"))
        json_resp = json.loads(get_top_users_resp.content)
        self.assertEqual(json_resp["user_list"][0]["username"], user2)
        self.assertEqual(json_resp["user_list"][0]["posts"], 2)
        self.assertEqual(json_resp["user_list"][1]["username"], user3)
        self.assertEqual(json_resp["user_list"][1]["posts"], 1)

    def test_follow(self):
        client = Client()
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": "test_user3_1@gmail.com",
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": "test_user3_2@gmail.com",
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        follow_resp = client.post(reverse_lazy("follow_user"),
                                  {
                                      "user_id": 1
                                  })
        self.assertEqual(follow_resp.status_code, 201)

    def test_user_feed(self):
        # create user1
        client = Client()
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": "test_user4_1@gmail.com",
                                        "password": "abc123"
                                    })
        self.assertEqual(register_resp.status_code, 201)

        # create a post with 1 like
        user1 = User.objects.get(pk=1)
        post1 = Post(body="body1", user=user1)
        post1.save()

        PostLike(user=user1, post=post1).save()

        # create a post with 2 likes
        post2 = Post(body="body2", user=user1)
        post2.save()

        PostLike(user=user1, post=post2).save()
        register_resp = client.post(reverse_lazy("create_user"),
                                    {
                                        "username": "test_user4_2@gmail.com",
                                        "password": "abc123"
                                    })
        user2 = User.objects.get(pk=2)
        PostLike(user=user2, post=post2).save()

        # make user2 follow user1
        follow_resp = client.post(reverse_lazy("follow_user"),
                                  {
                                      "user_id": 1
                                  })
        self.assertEqual(follow_resp.status_code, 201)

        # create a post with 0 likes
        post3 = Post(body="body3", user=user2)
        post3.save()

        # Validate that user feed for user2 returns post2 and post1, post3
        user_feed_resp = client.get(reverse_lazy(
            "user_feed", kwargs={"user_id": user2.pk}))
        json_resp = json.loads(user_feed_resp.content)
        self.assertEqual(json_resp["post_list"][0]["id"], post2.pk)
        self.assertEqual(json_resp["post_list"][0]["likes"], 2)
        self.assertEqual(json_resp["post_list"][1]["id"], post1.pk)
        self.assertEqual(json_resp["post_list"][1]["likes"], 1)
        self.assertEqual(json_resp["post_list"][2]["id"], post3.pk)
        self.assertEqual(json_resp["post_list"][2]["likes"], 0)
