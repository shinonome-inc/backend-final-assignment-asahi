from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()  # グローバル変数としてUser変数を宣言すること。


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
