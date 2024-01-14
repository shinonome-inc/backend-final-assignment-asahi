from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)
        # 設定したLOGIN_REDIRECT_URLにリダイレクトしている
        self.assertRedirects(
            response,
            settings.LOGIN_REDIRECT_URL,
            status_code=302,
            target_status_code=200,
        )
        # データベースにvalid_dataが追加されている
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        # valid_dataによってログインされている
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_duplicated_user(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        duplicated_user_data = {
            "username": "testuser",
            "email": "test2@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        self.client.post(self.url, valid_data)
        response = self.client.post(self.url, duplicated_user_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])
        # DBにレコードが追加されていない
        self.assertFalse(
            User.objects.filter(
                username=duplicated_user_data["username"], email=duplicated_user_data["email"]
            ).exists()
        )

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "testtest.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testp",
            "password2": "testp",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "abc@test.com",
            "password1": "testusertest",
            "password2": "testusertest",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "abc@test.com",
            "password1": "13243588",
            "password2": "13243588",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "abc@test.com",
            "password1": "password1",
            "password2": "password2",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])
        # DBにレコードが追加されていない
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse(settings.LOGIN_URL)
        # ログイン用ユーザーの作成
        self.user = User.objects.create_user(username="tester", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_login_data = {
            "username": "tester",
            "password": "testpassword",
        }
        response = self.client.post(self.url, valid_login_data)
        # Response Status Code: 302、設定のLOGIN_REDIRECT_URLにリダイレクトしている
        self.assertRedirects(
            response,
            settings.LOGIN_REDIRECT_URL,
            status_code=302,
            target_status_code=200,
        )
        # client.sessionにSESSION_KEYが含まれている
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_login_data = {
            "username": "tester2",
            "password": "testpassword",
        }
        response = self.client.post(self.url, invalid_login_data)
        form = response.context["form"]

        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])
        # client.sessionにSESSION_KEYが含まれていない
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        invalid_login_data = {
            "username": "tester",
            "password": "",
        }
        response = self.client.post(self.url, invalid_login_data)
        form = response.context["form"]

        # Response Status Code: 200
        self.assertEqual(response.status_code, 200)
        # フォームに適切なエラーメッセージが含まれている
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        # client.sessionにSESSION_KEYが含まれていない
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse(settings.LOGOUT_URL)
        # ログアウト用ユーザーの作成
        self.user = User.objects.create_user(username="tester", password="testpassword")
        # ログイン
        self.client.login(username="tester", password="testpassword")

    def test_success_post(self):
        response = self.client.post(self.url)

        # Response Status Code: 302, 設定のLOGOUT_REDIRECT_URLにリダイレクトしている
        self.assertRedirects(response, settings.LOGOUT_REDIRECT_URL, status_code=302)
        # client.sessionにSESSION_KEYが含まれていない
        self.assertNotIn(SESSION_KEY, self.client.session)


# class TestUserProfileView(TestCase):
#     def test_success_get(self):


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_user(self):

#     def test_failure_post_with_self(self):


# class TestUnfollowView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFollowingListView(TestCase):
#     def test_success_get(self):


# class TestFollowerListView(TestCase):
#     def test_success_get(self):
