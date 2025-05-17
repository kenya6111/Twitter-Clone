from datetime import datetime
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail

from django.db.models import Q
from twitter_clone.models import CustomUser, TweetModel,ReplyModel,LikeModel,RetweetModel,FollowModel,BookmarkModel,MessageRoomModel,MessageModel,NotificationModel
from django.core.exceptions import ObjectDoesNotExist
import secrets
from django.contrib.auth.hashers import make_password,check_password
from django.core.paginator import Paginator
from urllib.parse import urlencode
from cloudinary.uploader import upload
from django.http.response import JsonResponse
from django.db.models import Count

# ヘルパー関数
def send_verification_email(user,code):
    # email = "kenyanke6111@gmail.com"
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

def send_notification_email(user,receive_user, action_type):
    """アクション別テンプレート"""
    templates = {
        "like": {
            "subject": "あなたの投稿にいいねが付きました",
            "message": f"{receive_user.username}さん、あなたの投稿にいいねがありました。今すぐ確認しましょう。"
        },
        "retweet": {
            "subject": "あなたの投稿がリツイートされました",
            "message": f"{receive_user.username}さん、あなたの投稿がリツイートされました。通知をチェックしてください。"
        },
        "comment": {
            "subject": "あなたの投稿にコメントがありました",
            "message": f"{receive_user.username}さん、あなたの投稿に新しいコメントがあります。"
        }
    }

    # テンプレートが存在するかチェック
    if action_type not in templates:
        raise ValueError(f"未対応のアクションタイプです: {action_type}")

    template = templates[action_type]

    send_mail(
        subject=template["subject"],
        message=template["message"],
        from_email="kenyanke6111@gmail.com",
        recipient_list=[receive_user.email],
        fail_silently=False
    )

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
            authenticate_code= str(secrets.token_hex(16))
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
            custom_user = CustomUser.get_user_from_session(request.session)
            email_verification = custom_user.email_verification.get(code=code)

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
            custom_user = CustomUser.objects.get(email=tel_email_name)

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
    tweet_list=[]
    filter_type=''
    filter_type = request.GET.get("filter") or request.session.get('filtersession', '')
    request.session['filtersession'] = filter_type

    user = request.user
    custom_user = CustomUser.objects.get(id=user.id)

    # 返信に使われているツイートのID一覧
    reply_tweet_ids = ReplyModel.objects.values_list('reply_tweet_id', flat=True)
    if filter_type == 'foryou':
        tweet_list = TweetModel.objects.exclude(id__in=reply_tweet_ids).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-updated_at')
    elif filter_type == 'follow':
        following_users = CustomUser.objects.filter(
            id__in=custom_user.followings.values_list("follower_id", flat=True)
        )
        tweet_list = TweetModel.objects.filter(user__in=following_users).exclude(id__in=reply_tweet_ids).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-created_at')
    else:
        tweet_list = TweetModel.objects.exclude(id__in=reply_tweet_ids).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-updated_at')
    liked_article_ids = LikeModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)
    retweet_article_ids = RetweetModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)
    bookmark_article_ids = BookmarkModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)

    data_page = Paginator(tweet_list, 2)

    p = request.GET.get('p')
    articles = data_page.get_page(p)

    ## ログインユーザがフォローしてるユーザリスト取得
    follower_list= FollowModel.objects.filter(following=custom_user).values_list('follower',flat=True)
    follower_ids = list(follower_list)
    return render(request, 'twitter_clone/main.html', {'login_user':custom_user, 'tweet_list':tweet_list,'articles': articles, "liked_article_ids":liked_article_ids, "retweet_article_ids":retweet_article_ids,"bookmark_article_ids":bookmark_article_ids,"follower_ids":follower_ids})

def profile_view(request):
    user_id = request.GET.get("user_id")
    if request.method == 'POST':
        user_id = request.POST.get("user_id")
    custom_user = CustomUser.objects.get(id=user_id)
    tweet_list =[]
    filter_type = request.GET.get("filter") or request.session.get('filtersession', '')
    request.session['filtersession'] = filter_type

    if filter_type == 'post':
        tweet_list = TweetModel.objects.filter(user=custom_user).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-created_at')
    elif filter_type == 'comment':
        tweet_list = TweetModel.objects.filter(reply_tweets__user=custom_user).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-created_at')
    elif filter_type == 'retweet':
        tweet_list = TweetModel.objects.filter(retweets__user=custom_user).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-created_at')
    elif filter_type == 'like':
        tweet_list = TweetModel.objects.filter(likes__user=custom_user).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-created_at')
    else:
        tweet_list = TweetModel.objects.filter(user=custom_user).select_related('retweet').annotate(
            likes_count=Count('likes', distinct=True),
            retweets_count=Count('retweets', distinct=True),
        ).annotate(
            retweet_likes_count=Count('retweet__likes', distinct=True),
            retweet_retweets_count=Count('retweet__retweets', distinct=True),
        ).order_by('-created_at')

    liked_article_ids = LikeModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)
    retweet_article_ids = RetweetModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)

    data_page = Paginator(tweet_list, 2)
    p = request.GET.get('p')
    articles = data_page.get_page(p)
    return render(request, 'twitter_clone/profile.html', {'custom_user':custom_user, 'articles':articles,"liked_article_ids":liked_article_ids, "retweet_article_ids":retweet_article_ids})

def profile_edit_view(request):
    user_id = request.GET.get("user_id")
    custom_user=""

    if request.method == 'POST':
        try:
            user_id = request.POST.get("user_id", None)
            custom_user = CustomUser.objects.get(id=user_id)
            custom_user.username = request.POST.get("username", None)
            custom_user.introduction = request.POST.get("introduction", None)
            custom_user.place = request.POST.get("place", None)
            custom_user.web_site = request.POST.get("web_site", None)
            custom_user.birth = request.POST.get("birth", None)
            if 'head-image' in request.FILES:
                uploaded_head_image = upload(request.FILES['head-image'])
                custom_user.head_image = uploaded_head_image['secure_url']
            if 'image' in request.FILES:
                uploaded_image = upload(request.FILES['image'])
                custom_user.image = uploaded_image['secure_url']
            custom_user.save()
            redirect_url = reverse('profile')
            parameters = urlencode({'user_id': user_id})
            url = f'{redirect_url}?{parameters}'

            return redirect(url)
        except Exception:
            return render(request,'twitter_clone/profile.html')
    else:
        custom_user = CustomUser.objects.get(id=user_id)


    return render(request, 'twitter_clone/profile_edit.html', {'custom_user':custom_user})
def tweet_detail_view(request):
    user = request.user
    login_user = CustomUser.objects.get(id=user.id)
    origin_tweet_id=""

    if request.method == 'POST':

        origin_tweet_id = request.POST.get("tweet_id", None)
        tweet = TweetModel.objects.get(id=origin_tweet_id)

        tweet_sentence = request.POST.get("tweet-sentence", None)
        tweet_image=""
        if 'tweet-image' in request.FILES:
            uploaded_tweet_image = upload(request.FILES.get('tweet-image'))
            tweet_image = uploaded_tweet_image['secure_url']

        reply_tweet = TweetModel.objects.create(user=login_user, sentense=tweet_sentence, image=tweet_image)
        ReplyModel.objects.create(user=tweet.user, origin_tweet=tweet, reply_tweet=reply_tweet)

        if tweet.user.id != int(user.id):
            NotificationModel.objects.create(sender=login_user,receiver=tweet.user,action_flag="comment",notice_target=reply_tweet)
            send_notification_email(login_user,tweet.user,"comment")

        url = reverse('tweet_detail')
        parameters = urlencode({"tweet_id":origin_tweet_id})
        return redirect(f'{url}?{parameters}')

    origin_tweet_id = request.GET.get("tweet_id")

    tweet = TweetModel.objects.get(id=origin_tweet_id)
    display_tweet = TweetModel.objects.filter(id=origin_tweet_id).annotate(Count("likes"),Count('retweets'))

    reply_list = ReplyModel.objects.filter(origin_tweet=tweet).annotate(like_count=Count("reply_tweet__likes"),retweet_count=Count("reply_tweet__retweets")).order_by('-created_at')

    liked_article_ids = LikeModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)
    retweet_article_ids = RetweetModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)

    data_page = Paginator(reply_list, 2)
    p = request.GET.get('p')
    replies = data_page.get_page(p)

    return render(request, 'twitter_clone/tweet_detail.html',{"article":display_tweet[0], "login_user":login_user,"replies":replies,"liked_article_ids":liked_article_ids,"retweet_article_ids":retweet_article_ids})

def tweet_view(request):
    if request.method == 'POST':
        tweet_sentence = request.POST.get("tweet-sentence", None)
        user_id = request.POST.get("user_id", None)
        custom_user = CustomUser.objects.get(id=user_id)
        tweet_image=""
        if 'tweet-image' in request.FILES:
            uploaded_tweet_image = upload(request.FILES.get('tweet-image'))
            tweet_image = uploaded_tweet_image['secure_url']

        TweetModel.objects.create(user=custom_user, sentense=tweet_sentence, image=tweet_image)
    return redirect('main')

def like_view(request):
    if request.method == 'POST':
        tweet_id = request.POST.get("tweet_id", None)
        user_id = request.POST.get("user_id", None)
        tweet = TweetModel.objects.get(id=tweet_id)
        custom_user = CustomUser.objects.get(id=user_id)

        exist_record= LikeModel.objects.filter(user=custom_user, tweet=tweet).first()

        if exist_record:
            exist_record.delete()
            return JsonResponse({'is_registered': False})
        else:
            LikeModel.objects.create(user=custom_user, tweet=tweet)
            if tweet.user.id != int(user_id):
                # notificationModeへの追加とメール送信
                NotificationModel.objects.create(sender=custom_user,receiver=tweet.user,action_flag="like",notice_target=tweet)
                send_notification_email(custom_user,tweet.user,"like")
            return JsonResponse({'is_registered': True})

def retweet_view(request):
    if request.method == 'POST':
        tweet_id = request.POST.get("tweet_id", None)
        origin_tweet_id = request.POST.get("origin_tweet_id", None)
        user_id = request.POST.get("user_id", None)

        tweet = TweetModel.objects.get(id=tweet_id)
        origin_tweet=""
        if origin_tweet_id:
            origin_tweet = TweetModel.objects.get(id=origin_tweet_id)
        custom_user = CustomUser.objects.get(id=user_id)
        exist_record= RetweetModel.objects.filter(user=custom_user, tweet=tweet).first()
        if exist_record:
            exist_record.delete()
            origin_tweet.delete()
            return JsonResponse({'is_registered': False})
        else:
            RetweetModel.objects.create(user=custom_user, tweet=tweet)
            TweetModel.objects.create(user=custom_user,is_retweet=True,retweet=tweet)

            if tweet.user.id != int(user_id):
                NotificationModel.objects.create(sender=custom_user,receiver=tweet.user,action_flag="retweet",notice_target=tweet)
                send_notification_email(custom_user,tweet.user,"retweet")
            return JsonResponse({'is_registered': True})

def follow_unfollow(request):
    if request.method == 'POST':
        login_user_id = request.POST.get("login_user_id", None)
        tweet_user_id = request.POST.get("tweet_user_id", None)
        is_follow = request.POST.get("is_follow", None)
        login_user = get_object_or_404(CustomUser,id=login_user_id)
        tweet_user = get_object_or_404(CustomUser,id=tweet_user_id)

        if is_follow:
            FollowModel.objects.create(follower=tweet_user,following=login_user)
        else:
            exist_record = get_object_or_404(FollowModel,follower=tweet_user,following=login_user)
            exist_record.delete()
            return JsonResponse({'is_registered': False})
        return JsonResponse({'is_registered': True})

def bookmark(request):
    if request.method == 'POST':
        tweet_id = request.POST.get("tweet_id", None)
        user_id = request.POST.get("user_id", None)
        tweet = TweetModel.objects.get(id=tweet_id)
        custom_user = CustomUser.objects.get(id=user_id)

        exist_record= BookmarkModel.objects.filter(user=custom_user, tweet=tweet).first()

        if exist_record:
            exist_record.delete()
            return JsonResponse({'is_registered': False})
        else:
            BookmarkModel.objects.create(user=custom_user, tweet=tweet)
            return JsonResponse({'is_registered': True})
    user = request.user
    custom_user = CustomUser.objects.get(id=user.id)
    tweet_list = TweetModel.objects.filter(bookmarks__user=custom_user).annotate(likes_count=Count('likes', distinct=True),retweets_count=Count('retweets', distinct=True))

    liked_article_ids = LikeModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)
    retweet_article_ids = RetweetModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)
    bookmark_article_ids = BookmarkModel.objects.filter(user = request.user).values_list("tweet_id", flat=True)

    data_page = Paginator(tweet_list, 2)
    p = request.GET.get('p')
    articles = data_page.get_page(p)

    follower_list= FollowModel.objects.filter(following=custom_user).values_list('follower',flat=True)
    follower_ids = list(follower_list)
    return render(request, 'twitter_clone/bookmark.html', {'login_user':custom_user, 'tweet_list':tweet_list,'articles': articles, "liked_article_ids":liked_article_ids, "retweet_article_ids":retweet_article_ids,"bookmark_article_ids":bookmark_article_ids,"follower_ids":follower_ids})

def message(request):
    user_id=""
    if request.method == 'POST':
        user_id = request.POST.get("user_id", None)
        room_id = request.POST.get("room_id", None)
        content = request.POST.get("content", None)
        custom_user = get_object_or_404(CustomUser, id=user_id)
        message_room = get_object_or_404(MessageRoomModel, id=room_id)
        if content:
            MessageModel.objects.create(room=message_room ,sender=custom_user,content=content)
        redirect_url = reverse('message')
        parameters = urlencode({'user_id': user_id,'room_id': room_id})
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

    user_id = request.GET.get("user_id", None)
    custom_user = CustomUser.objects.get(id=user_id)
    message_rooms = MessageRoomModel.objects.filter(participants=custom_user)

    rooms_with_others = []
    for room in message_rooms:
        other = room.participants.exclude(id=custom_user.id).first()
        rooms_with_others.append({
            'room': room,
            'other_user': other
        })

    messages_data =""
    message_room=""
    other_user=""
    if "room_id" in request.GET:
        room_id = request.GET.get("room_id")
        message_room = MessageRoomModel.objects.get(id=room_id)
        messages_data = MessageModel.objects.filter(room=message_room)
        other_user = message_room.participants.exclude(id=custom_user.id).first()
    return render(request, 'twitter_clone/message.html', {"custom_user":custom_user,"message_rooms":message_rooms,"messages":messages_data, "message_room":message_room,"login_user":custom_user,"rooms_with_others":rooms_with_others,"other_user":other_user})

def make_message_room_view(request):
    if request.method == 'POST':
        login_user_id = request.POST.get("login_user_id", None)
        tweet_user_id = request.POST.get("tweet_user_id", None)
        login_user = get_object_or_404(CustomUser,id=login_user_id)
        tweet_user = get_object_or_404(CustomUser,id=tweet_user_id)

        exist_record= (
            MessageRoomModel.objects
            .filter(participants=login_user)
            .filter(participants=tweet_user)
            .first()
        )

        if exist_record:
            return JsonResponse({'is_registered': False,'room_id': exist_record.id})
        else:
            room = MessageRoomModel.objects.create()
            room.participants.set([login_user, tweet_user])
            return JsonResponse({'is_registered': True, 'room_id': room.id})

def notice(request):
    user_id = request.GET.get("user_id", None)
    custom_user = CustomUser.objects.get(id=user_id)
    notifications = NotificationModel.objects.filter(receiver=custom_user)
    return render(request, 'twitter_clone/notice.html', {"notifications":notifications})
