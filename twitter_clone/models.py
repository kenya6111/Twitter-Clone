# import random
from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        db_table = 'custom_user'


    # user_name = models.CharField(max_length=50,blank=True, null=True)
    email = models.EmailField(max_length=100,blank=True, null=True)
    tel = models.EmailField(max_length=100,blank=True, null=True)
    date_of_birth = models.EmailField(max_length=100,blank=True, null=True)
    # age = models.IntegerField('年齢', blank=True, null=True)


class EmailVerificationModel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_verification', null=True, blank=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def __str__(self):
        return "user_id:" + str(self.user.id) +", user_name:"+ str(self.user.username)+ ", code:"+str(self.code) + ", created_at:" + str(self.created_at)
