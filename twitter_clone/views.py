from datetime import datetime
import random
# from urllib.parse import urlencode
from django.shortcuts import render,redirect
from django.contrib import messages
# from django.contrib.auth import login
# from django.urls import reverse_lazy
# from django.views.generic import CreateView
# from django.core.mail import BadHeaderError
from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from twitter_clone.forms import CustomLoginForm
from twitter_clone.models import CustomUser,EmailVerificationModel
# from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
# from django.urls import reverse
# from allauth.account.views import LoginView
# from allauth.account.forms import LoginForm



# from .forms import SignupForm
# Create your views here.


def signup_view(request):
    request.session.clear()
    if request.method == 'POST':
        name = request.POST.get("name", None)
        email = request.POST.get("email", None)
        tel = request.POST.get("tel", None)
        day = request.POST.get("day", None)
        month = request.POST.get("month", None)
        year = request.POST.get("year", None)

        dt = datetime.strptime(year+month + day, '%Y%m%d')

        # 認証するまでログイン不可
        custom_user = CustomUser.objects.create()
        custom_user.username = name
        custom_user.email = email
        custom_user.tel = tel
        custom_user.date_of_birth = dt
        custom_user.is_active = False
        custom_user.save()

        # 認証コードを生成
        authenticate_code= str(random.randint(100000,999999))
        email_verification = EmailVerificationModel(user=custom_user, code=authenticate_code)
        email_verification.save()

        email = "kenyanke6111@gmail.com"# TODO 画面入力のメアドを入れる
        """題名"""
        subject = f"Xの認証コードは{authenticate_code}です"
        """本文"""
        message = f"""メールアドレスを確認してください\n\nXアカウントの作成に必要なステップとして、このメールアドレスが正しいことを確認しましょう。新しいアカウントにこのアドレスを使うことを確認してください。\n\nXを使い始めるには、以下の認証コードを入力してください。\n {authenticate_code}\n認証コードの有効時間は{1}時間です。\n\nよろしくお願いします。\nX"""
        """送信元メールアドレス"""
        from_email = "kenyanke6111@gmail.com"
        """宛先メールアドレス"""
        recipient_list = [
            email
        ]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)


        request.session['user_id'] = custom_user.id

        return redirect('email_verify')

    return render(request, 'account/signup.html')


def email_verify_view(request):
    print(111)
    if request.method == 'POST':
        print("post")
        try:
            code = request.POST.get("authenticate-code", None)

            user_id = request.session.get('user_id')
            custom_user = CustomUser.objects.get(id=user_id)

            email_verification = EmailVerificationModel.objects.get(user=custom_user, code=code)

            custom_user.is_active=True
            custom_user.save()
            email_verification.delete()
            messages.success(request, "メールアドレスの認証が完了しました。")

            return redirect('password_input')

        except ObjectDoesNotExist:
            messages.error(request, "無効な認証コードです。")
            return redirect('email_verify')

        except Exception:
            return render(request, 'account/signup_email_verify.html')

    return render(request, 'account/signup_email_verify.html')

def password_input_view(request):
    if request.method == 'POST':
        try:
            password = request.POST.get("password", None)
            user_id = request.session.get('user_id')
            custom_user = CustomUser.objects.get(id=user_id)
            custom_user.password = password
            custom_user.save()
            messages.success(request, "パスワードの登録が完了しました。")
            return redirect('top')

        except Exception:
            return render(request, 'account/signup_password_input.html')

    return render(request, 'account/signup_password_input.html')

def login_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get("name", None)
            password = request.POST.get("password", None)
            custom_user = CustomUser.objects.get(username=username,password=password)
            if not custom_user.is_active:
                raise Exception("無効なユーザです。")
            request.session['user_id'] = custom_user.id
            messages.success(request, "ログインに成功しました。")
            return redirect('main')
        except ObjectDoesNotExist:
            messages.error(request, "ログインに失敗しました。")
            return render(request, 'account/login.html')
        except Exception:
            messages.error(request, "例外が発生しました。")
            return render(request, 'account/login.html',{})
    return render(request, 'account/login.html')

def logout_view(request):
    print(1234)
    try:
        print(4444)
        request.session.clear()
        messages.success(request, "ログアウトが完了しました。")
        return redirect('top')
    except Exception:
        messages.error(request, "例外が発生しました。")
        return redirect('top')

def top_view(request):
    return render(request, 'twitter_clone/top.html')
def main_view(request):
    user_id = request.session.get('user_id')
    login_user = CustomUser.objects.get(id=user_id)


    return render(request, 'twitter_clone/main.html', {'login_user':login_user})