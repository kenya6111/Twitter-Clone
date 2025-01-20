from django.db import models
import re
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        db_table = 'users'


    # user_name = models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(max_length=100, null=False, unique=True)
    tel = models.EmailField(max_length=100,blank=True, null=True)
    date_of_birth = models.EmailField(max_length=100,blank=True, null=True)
    # age = models.IntegerField('年齢', blank=True, null=True)

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


class EmailVerificationModel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_verification', null=True, blank=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return "user_id:" + str(self.user.id) +", user_name:"+ str(self.user.username)+ ", code:"+str(self.code) + ", created_at:" + str(self.created_at)
