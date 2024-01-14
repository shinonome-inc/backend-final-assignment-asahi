from turtle import end_fill

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")
        # ツイートを作成
        self.tweet1 = Tweet.objects.create(user=self.user, content="Test tweet 1")
        self.tweet2 = Tweet.objects.create(user=self.user, content="Test tweet 2")

    def test_success_get(self):
        response = self.client.get(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        context_tweets = response.context['tweets']
        db_tweets = Tweet.objects.all()
        # context内に含まれるツイート一覧が、DBに保存されているツイート一覧と同一である
        self.assertQuerysetEqual(context_tweets, db_tweets, ordered=False)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.client.login(username="tester", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {"content":"test tweet!"}
        response = self.client.post(self.url,valid_data)
        # Response Status Code: 302、ホームにリダイレクトしている
        self.assertRedirects(
            response,
            "/tweets/home/",
            status_code=302,
        )
        # DBにデータが追加されている、追加されたデータのcontentが送信されたcontentと同一である
        self.assertTrue(Tweet.objects.filter(content=valid_data["content"]).exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {"content":""}
        response = self.client.post(self.url,invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["content"])
        # DBにレコードが追加されていない
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())


    def test_failure_post_with_too_long_content(self):
        # 216文字
        invalid_data = {"content":"testtesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttt"}
        response = self.client.post(self.url,invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn(f"この値は 140 文字以下でなければなりません( {len(invalid_data['content'])} 文字になっています)。", form.errors["content"])
        # DBにレコードが追加されていない
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())

# class TestTweetDetailView(TestCase):
#     def test_success_get(self):


# class TestTweetDeleteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
