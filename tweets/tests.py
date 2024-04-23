from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Like, Tweet

User = get_user_model()


class AbstractTestCase(TestCase):
    is_need_kwargs: bool = False
    url_name: str
    not_exist_tweet_pk = 999

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpassword")
        self.user2 = User.objects.create_user(username="tester2", password="testpassword2")
        self.client.login(username="tester", password="testpassword")
        # ツイートを作成
        self.tweet1 = Tweet.objects.create(user=self.user, content="Test tweet 1")
        self.tweet2 = Tweet.objects.create(user=self.user, content="Test tweet 2")
        if self.is_need_kwargs:
            self.url = reverse(self.url_name, kwargs={"pk": self.tweet1.pk})
        else:
            self.url = reverse(self.url_name)
        Like.objects.create(user=self.user, tweet=self.tweet1)


class TestHomeView(AbstractTestCase):
    url_name = "tweets:home"

    def test_success_get(self):
        response = self.client.get(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        context_tweets = response.context["tweets"]
        db_tweets = Tweet.objects.all()
        # context内に含まれるツイート一覧が、DBに保存されているツイート一覧と同一である
        self.assertQuerysetEqual(context_tweets, db_tweets, ordered=False)


class TestTweetCreateView(AbstractTestCase):
    url_name = "tweets:create"

    def test_success_get(self):
        response = self.client.get(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {"content": "test tweet!"}
        response = self.client.post(self.url, valid_data)
        # Response Status Code: 302、ホームにリダイレクトしている
        self.assertRedirects(response, "/tweets/home/", status_code=302)
        # DBにデータが追加されている、追加されたデータのcontentが送信されたcontentと同一である
        self.assertTrue(Tweet.objects.filter(content=valid_data["content"]).exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {"content": ""}
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["content"])
        # DBにレコードが追加されていない
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())

    def test_failure_post_with_too_long_content(self):
        # 216文字
        invalid_data = {
            "content": "testtesttesttesttttesttesttesttesttttesttesttesttesttttes"
            "ttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttt"
            "testtesttesttesttttesttesttesttesttttesttesttesttesttttesttesttesttesttt"
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn(
            f"この値は 140 文字以下でなければなりません( {len(invalid_data['content'])} 文字になっています)。",
            form.errors["content"],
        )
        # DBにレコードが追加されていない
        self.assertFalse(Tweet.objects.filter(content=invalid_data["content"]).exists())


class TestTweetDetailView(AbstractTestCase):
    is_need_kwargs = True
    url_name = "tweets:detail"

    def test_success_get(self):
        response = self.client.get(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # context内に含まれるツイートがDBと同一である
        self.assertTrue(Tweet.objects.filter(content=self.tweet1.content).exists())


class TestTweetDeleteView(AbstractTestCase):
    is_need_kwargs = True
    url_name = "tweets:delete"

    def test_success_post(self):
        response = self.client.post(self.url)
        # Response Status Code: 302 ホームにリダイレクトしている
        self.assertRedirects(response, "/tweets/home/", status_code=302)
        # DBのデータが削除されている
        self.assertFalse(Tweet.objects.filter(pk=self.tweet1.pk).exists())

    def test_failure_post_with_not_exist_tweet(self):
        queryset_before_deletion = Tweet.objects.all()
        response = self.client.post(reverse(self.url_name, kwargs={"pk": self.not_exist_tweet_pk}))
        # 期待通りのステータスコードが返されることを確認
        self.assertEqual(response.status_code, 404)
        # DBの中身が削除されていない
        self.assertQuerysetEqual(Tweet.objects.all(), queryset_before_deletion, ordered=False)

    def test_failure_post_with_incorrect_user(self):
        queryset_before_deletion = Tweet.objects.all()
        # ユーザー2によるログイン
        self.client.login(username="tester2", password="testpassword2")
        response = self.client.post(self.url)
        # Response Status Code: 403
        self.assertEqual(response.status_code, 403)
        # DBのデータが削除されていない
        self.assertQuerysetEqual(Tweet.objects.all(), queryset_before_deletion, ordered=False)


class TestLikeView(AbstractTestCase):
    is_need_kwargs = True
    url_name = "tweets:like"

    def test_success_post(self):
        response = self.client.post(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # DBにデータが追加されている
        self.assertTrue(Like.objects.filter(user=self.user, tweet=self.tweet1).exists())

    def test_failure_post_with_not_exist_tweet(self):
        queryset_before_like = Like.objects.all()
        response = self.client.post(reverse(self.url_name, kwargs={"pk": self.not_exist_tweet_pk}))
        # 期待通りのステータスコードが返されることを確認
        self.assertEqual(response.status_code, 404)
        # DBの中身が削除されていない
        self.assertQuerysetEqual(Like.objects.all(), queryset_before_like)

    def test_failure_post_with_liked_tweet(self):
        queryset_before_like = Like.objects.all()
        self.client.post(self.url)
        response = self.client.post(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # DBにレコードが追加されていない
        self.assertQuerySetEqual(Like.objects.all(), queryset_before_like)


class TestUnLikeView(AbstractTestCase):
    is_need_kwargs = True
    url_name = "tweets:unlike"

    def test_success_post(self):
        response = self.client.post(self.url)
        #  Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # DBにデータが削除されている
        self.assertFalse(Like.objects.filter(user=self.user, tweet=self.tweet1).exists())

    def test_failure_post_with_not_exist_tweet(self):
        queryset_before_delete = Like.objects.all()
        response = self.client.post(reverse(self.url_name, kwargs={"pk": self.not_exist_tweet_pk}))
        # 期待通りのステータスコードが返されることを確認
        self.assertEqual(response.status_code, 404)
        # DBの中身が削除されていない
        self.assertQuerysetEqual(Like.objects.all(), queryset_before_delete)

    def test_failure_post_with_unliked_tweet(self):
        self.client.post(self.url)
        response = self.client.post(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
