from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from allauth.account.models import EmailAddress
from twitter_clone.models import CustomUser, TweetModel

User = get_user_model()

SIGNUP_URL = reverse("account_signup")
LOGIN_URL  = reverse("account_login")
LOGOUT_URL = reverse("account_logout")
CONFIRM_URL = reverse("account_email_verification_sent")


class AllAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "testtets@example.com"
        self.password = "Password@"

        with patch("allauth.account.utils.send_email_confirmation"):
            self.signup_res = self.client.post(
                SIGNUP_URL,
                {
                    "email": self.email,
                    "password1": self.password,
                    "password2": self.password,
                    "username": "test??user!!!",
                },
            )

        self.user = User.objects.first()
        self.email_addr = self.user.emailaddress_set.first()

        self.email_addr.verified = True
        self.email_addr.save()
        print("-------")
        print(self.user)
        print(self.password)
        print(self.email)
        print(self.signup_res.status_code, self.signup_res.url)# 302 /accounts/confirm-email/
        print(self.email_addr)
        print(self.email_addr.verified)
        print("-------")
    # ---------- サインアップ ----------------------------------------
    def test_signup_redirect(self):
        self.assertEqual(self.signup_res.status_code, 302)
        self.assertEqual(self.signup_res.url, CONFIRM_URL)

    def test_user_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.email, self.email)

    def test_email_verified_flag(self):
        self.assertTrue(self.email_addr.verified)

    # ---------- ログイン -------------------------------------------
    def test_login_success(self):
        data = {"login": self.email, "password": self.password}
        res = self.client.post(LOGIN_URL, data)
        self.assertRedirects(res, "/main/")

    def test_login_fail(self):
        data = {"login": self.email, "password": "wrongpass"}
        res = self.client.post(LOGIN_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.wsgi_request.user.is_authenticated)

    def test_client_login_true_when_verified(self):
        c = Client()
        ok = c.login(email=self.email, password=self.password)
        self.assertTrue(ok)

    def test_client_login_false_when_not_verified(self):
        res = self.client.post(
            SIGNUP_URL,
            {
                "email": "nv@example.com",
                "password1": "AnotherP@ss1",
                "password2": "AnotherP@ss1",
                "username": "nouser",
            },
        )
        self.assertEqual(res.status_code, 302)

        c = Client()
        self.assertTrue(c.login(email="nv@example.com", password="AnotherP@ss1"))

class TweetViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="poster",
            email="poster@example.com",
            password="pass1234",
            is_active=True,
        )
        # 認証済みにしておく
        self.client.force_login(self.user)

    # ───────────────────────────────────────────
    def test_tweet_success(self):
        data = {"tweet-sentence": "hello world", "user_id": self.user.id}
        resp = self.client.post(reverse("tweet"), data)

        self.assertRedirects(resp, reverse("main"))
        self.assertEqual(TweetModel.objects.filter(user=self.user).count(), 1)

    # ───────────────────────────────────────────
    def test_tweet_invalid_user(self):
        data = {"tweet-sentence": "invalid", "user_id": 9999}

        with self.assertRaises(User.DoesNotExist):
            self.client.post(reverse("tweet"), data)

        self.assertEqual(TweetModel.objects.count(), 0)