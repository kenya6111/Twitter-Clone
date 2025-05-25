from django.db import models
import re
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import AbstractUser
from django.db.models import Q, F
# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        db_table = 'users'

    email = models.EmailField(max_length=100, null=False, unique=True)
    tel = models.EmailField(max_length=100,blank=True, null=True)
    date_of_birth = models.CharField(max_length=100,blank=True, null=True)
    image = models.ImageField(upload_to='images', verbose_name='イメージ画像', null=True, blank=True)
    introduction = models.TextField(blank=True, null=True)
    head_image = models.ImageField(upload_to='images', verbose_name='イメージ画像_ヘッダー', null=True, blank=True)
    place = models.TextField(max_length=500,blank=True, null=True)
    web_site = models.CharField(max_length=100,blank=True, null=True)

    @classmethod
    def is_valid_email(email):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(regex, email))

    @classmethod
    def is_valid_phone_number(phone_number):
        phone_number_pattern = r"^0[789]0\d{8}$"
        return bool(re.match(phone_number_pattern, phone_number))

    @classmethod
    def get_user_from_session(cls, session):
        """セッションからユーザを取得する"""
        user_id = session.get('user_id')
        if not user_id:
            raise ObjectDoesNotExist("セッションにユーザIDがありません。")
        return cls.objects.get(id=user_id)


class EmailVerificationModel(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_verification', null=True, blank=True)
    code = models.CharField(max_length=6)

    class Meta:
        db_table = "email_verifications"

    def __str__(self):
        return "user_id:" + str(self.user.id) +", user_name:"+ str(self.user.username)+ ", code:"+str(self.code) + ", created_at:" + str(self.created_at)

class TweetModel(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tweet', null=False, blank=True)
    sentense = models.TextField(max_length=270, null=True, blank=True)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    is_retweet = models.BooleanField(default=False)
    retweet = models.ForeignKey("TweetModel", on_delete=models.CASCADE,default='',null=True, blank=True)

    class Meta:
        db_table = "tweets"

class FollowModel(BaseModel):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followings')

    class Meta:
        db_table = "follows"
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="follow_unique"
            ),
        ]

class LikeModel(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    tweet = models.ForeignKey(TweetModel, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = "likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="like_unique"
            ),
        ]

class RetweetModel(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='retweets')
    tweet = models.ForeignKey(TweetModel, on_delete=models.CASCADE, related_name='retweets')

    class Meta:
        db_table = "retweets"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="retweet_unique"
            ),
        ]

class ReplyModel(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='replies')
    origin_tweet = models.ForeignKey(TweetModel, on_delete=models.CASCADE, related_name='origin_tweets')
    reply_tweet = models.ForeignKey(TweetModel, on_delete=models.CASCADE, related_name='reply_tweets')

    class Meta:
        db_table = "replies"

class BookmarkModel(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookmarks')
    tweet = models.ForeignKey(TweetModel, on_delete=models.CASCADE, related_name='bookmarks')

    class Meta:
        db_table = "bookmarks"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="bookmark_unique"
            ),
        ]

class MessageRoomModel(BaseModel):
    participants = models.ManyToManyField(
        CustomUser,
        related_name='message_rooms',
        symmetrical=False,   # A↔B を同じペアとみなすなら True でも可
    )
    class Meta:
        db_table = "message_rooms"

class MessageModel(BaseModel):
    room = models.ForeignKey(MessageRoomModel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(max_length=270, null=True, blank=True)

    class Meta:
        db_table = "messages"

class NotificationModel(BaseModel):
    class ActionType(models.TextChoices):
        LIKE     = "like",     "Like"
        RETWEET  = "retweet",  "Retweet"
        COMMENT  = "comment",  "Comment"

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='sent_notifications')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='received_notifications')
    action_type = models.CharField(default="",choices=ActionType.choices,max_length=8)
    related_tweet = models.ForeignKey('TweetModel', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
