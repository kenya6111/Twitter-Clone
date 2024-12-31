from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

CustomUser = get_user_model()
class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': '',
            'placeholder': '',
            'autocomplete': 'off',
            'id': 'username',
            'name':'',
            'required': 'required',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': '',
            'placeholder': '',
            'autocomplete': 'off',
            'id': 'password',
            'name':'',
            'required': 'required',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'text-white bg-black form-control border-gray'})
            # カスタムラベルのクラスを追加
            # self.fields['username'].widget.attrs["class"] = "text-white bg-black form-control border-gray"
            # self.fields['password'].widget.attrs["class"] = "text-white bg-black form-control border-gray"
