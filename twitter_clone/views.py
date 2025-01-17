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
import re
import secrets
from django.contrib.auth.hashers import make_password,check_password

# ヘルパー関数
def get_user_from_session(request):
    user_id = request.session.get('user_id')
    if not user_id:
        raise ObjectDoesNotExist("セッションにユーザIDがありません。")
    return CustomUser.objects.get(id=user_id)

def send_verification_email(user,code):
    email = "kenyanke6111@gmail.com"
    """題名"""
    subject = f"Xの認証コードは{code}です"
    """本文"""
    message = f"""メールアドレスを確認してください\n\nXアカウントの作成に必要なステップとして、このメールアドレスが正しいことを確認しましょう。新しいアカウントにこのアドレスを使うことを確認してください。\n\nXを使い始めるには、以下の認証コードを入力してください。\n {code}\n認証コードの有効時間は{1}時間です。\n\nよろしくお願いします。\nX"""
    """送信元メールアドレス"""
    from_email = "kenyanke6111@gmail.com"
    """宛先メールアドレス"""
    recipient_list = [
        user.email
    ]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

def signup_view(request):
    request.session.clear()
    if request.method == 'POST':
        try:
            name = request.POST.get("name", None)
            email = request.POST.get("mail", None)
            tel = request.POST.get("tel", None)
            day = request.POST.get("day", None)
            month = request.POST.get("month", None)
            year = request.POST.get("year", None)

            dt = None
            if all([day,month,year]):
                dt = datetime.strptime(year+month + day, '%Y%m%d')

            # 認証するまでログイン不可
            custom_user = CustomUser(username=name, email=email, tel=tel, date_of_birth=dt, is_active=False)
            if not CustomUser.is_valid_email(custom_user.email):
                raise Exception("メールアドレスの形式が不正です。")
            if not CustomUser.is_valid_phone_number(custom_user.tel):
                raise Exception("電話番号の形式が不正です。")
            else:
                custom_user.save()

            # 認証コードを生成
            # authenticate_code= str(random.randint(100000,999999))
            authenticate_code= str(secrets.token_hex(16))
            # email_verification = EmailVerificationModel(user=custom_user, code=authenticate_code)
            # email_verification.save()
            custom_user.email_verifications.create(code=authenticate_code)

            # 認証コード付きメールを送信
            send_verification_email(custom_user, authenticate_code)
            request.session['user_id'] = custom_user.id

            return redirect('email_verify')

        except Exception:
            return render(request,'account/signup.html')
    return render(request, 'account/signup.html')


def email_verify_view(request):
    # user_idがセッションに存在しない場合、サインアップ画面へリダイレクト
    if 'user_id' not in request.session:
        messages.error(request, "セッションが無効です。サインアップを最初からやり直してください。")
        return redirect('signup')
    # 既に認証済みの場合はトップ画面へリダイレクト
    custom_user = CustomUser.objects.get(id=request.session['user_id'])
    if custom_user.is_active:
        messages.info(request, "既に認証が完了しています。")
        return redirect('top')
    if request.method == 'POST':
        try:
            code = request.POST.get("authenticate-code", None)
            # custom_user = get_user_from_session(request)
            custom_user = CustomUser.get_user_from_session(request.session)

            email_verification = EmailVerificationModel.objects.get(user=custom_user, code=code)

            custom_user.is_active=True
            custom_user.save()
            email_verification.delete()
            messages.success(request, "メールアドレスの認証が完了しました。")

            return redirect('password_input')

        except ObjectDoesNotExist:
            messages.error(request, "無効な認証コードです。")
            return redirect('email_verify')

        except Exception as e:
            messages.error(request, f"エラーが発生しました: {str(e)}")
            return render(request, 'account/signup_email_verify.html')

    return render(request, 'account/signup_email_verify.html')

def password_input_view(request):
    # 以下の場合はトップ画面へリダイレクト
    # --セッション情報なし
    if 'user_id' not in request.session:
        messages.error(request, "セッションが無効です。サインアップを最初からやり直してください。")
        return redirect('signup')
    # --パスワード設定済み
    custom_user = CustomUser.objects.get(id=request.session['user_id'])
    if custom_user.password:
        messages.info(request, "既にパスワード設定が完了しています。")
        return redirect('top')
    if request.method == 'POST':
        try:
            password = request.POST.get("password", None)
            # custom_user = get_user_from_session(request)
            custom_user = CustomUser.get_user_from_session(request.session)
            custom_user.password = make_password(password)
            custom_user.save()
            messages.success(request, "パスワードの登録が完了しました。")
            return redirect('top')

        except Exception as e:
            messages.error(request, f"エラーが発生しました: {str(e)}")
            return render(request, 'account/signup_password_input.html')

    return render(request, 'account/signup_password_input.html')

def login_view(request):
    if request.method == 'POST':
        try:
            tel_email_name = request.POST.get("tel_email_name", None)
            input_password = request.POST.get("password", None)

            custom_user = None
            # if is_valid_email(tel_email_name):
            custom_user = CustomUser.objects.get(email=tel_email_name)
            # elif is_valid_phone_number(tel_email_name):
            #     custom_user = CustomUser.objects.get(tel=tel_email_name)
            # else:
            #     custom_user = CustomUser.objects.get(username=tel_email_name)

            # パスワード一致チェック
            if not check_password(input_password ,custom_user.password):
                raise Exception("パスワードが不正です。")

            # メール認証チェック
            if not custom_user.is_active:
                raise Exception("無効なユーザです。")

            request.session['user_id'] = custom_user.id
            messages.success(request, "ログインに成功しました。")
            return redirect('main')
        except ObjectDoesNotExist:
            messages.error(request, "ログインに失敗しました。")
            return render(request, 'account/login.html')
        except Exception as e:
            messages.error(request, f"エラーが発生しました: {str(e)}")
            return render(request, 'account/login.html',{})
    return render(request, 'account/login.html')

def logout_view(request):
        request.session.clear()
        messages.success(request, "ログアウトが完了しました。")
        return redirect('top')

def top_view(request):
    return render(request, 'twitter_clone/top.html')

def main_view(request):
    # try:
        # login_user = get_user_from_session(request)
        return render(request, 'twitter_clone/main.html')
    # except ObjectDoesNotExist:
    #     messages.error(request, "セッションが無効です。ログインしてください。")
    #     return redirect('login')