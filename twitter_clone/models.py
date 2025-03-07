from django.db import models
import re
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import AbstractUser
# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        db_table = 'users'


    # user_name = models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(max_length=100, null=False, unique=True)
    tel = models.EmailField(max_length=100,blank=True, null=True)
    date_of_birth = models.CharField(max_length=100,blank=True, null=True)
    image = models.ImageField(upload_to='images', verbose_name='イメージ画像', null=True, blank=True)
    introduction=models.TextField(blank=True, null=True)
    head_image=models.ImageField(upload_to='images', verbose_name='イメージ画像_ヘッダー', null=True, blank=True)
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
    # created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    class Meta:
        db_table = "email_verifications"

    def __str__(self):
        return "user_id:" + str(self.user.id) +", user_name:"+ str(self.user.username)+ ", code:"+str(self.code) + ", created_at:" + str(self.created_at)

class TweetModel(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tweet', null=False, blank=True)
    sentense = models.TextField(max_length=270)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    # updated_at = models.DateTimeField(auto_now=True,blank=True,null=True)
    class Meta:
        db_table = "tweets"

class FollowModel(BaseModel):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followings')
    # created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

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
    # created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

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
    # created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

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
    tweet = models.ForeignKey(TweetModel, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField(max_length=270)
    # created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "replies"
