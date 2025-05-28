# twitter_clone/tests/test_system.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import uuid

from twitter_clone.models import TweetModel, CustomUser


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ["user-data.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        cls.selenium = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=opts,
        )
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    # ======================================================================
    # 1. サインアップ
    # ======================================================================
    def signup(self, email: str, password: str = "pass12345"):
        self.selenium.get(f"{self.live_server_url}{reverse('account_signup')}")

        if self.selenium.find_elements(By.NAME, "username"):
            self.selenium.find_element(By.NAME, "username").send_keys(f"u_{uuid.uuid4().hex[:6]}")

        self.selenium.find_element(By.NAME, "email").send_keys(email)
        self.selenium.find_element(By.NAME, "password1").send_keys(password)
        self.selenium.find_element(By.NAME, "password2").send_keys(password)
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # --- 正常系
    def test_signup_success(self):
        email = f"e2e_{uuid.uuid4().hex[:6]}@example.com"
        self.signup(email)

        assert not self.selenium.current_url.endswith(reverse("account_signup"))
        assert "メールアドレスを確認" in self.selenium.page_source
        assert CustomUser.objects.filter(email=email).exists()

    # --- 異常系
    def test_signup_invalid_email(self):
        self.signup("baduser", "invalid-email")
        assert self.selenium.current_url.endswith(reverse("account_signup"))
        page = self.selenium.page_source
        assert ("Enter a valid email address" in page) or ("有効なメールアドレスを入力してください" in page)
        assert not CustomUser.objects.filter(username="baduser").exists()

    # # ======================================================================
    # # 2. ログイン
    # # ======================================================================
    def login(self, email="myuser@example.com", password="secret"):
        self.selenium.get(f"{self.live_server_url}{reverse('account_login')}")
        self.selenium.find_element(By.NAME, "login").send_keys(email)
        self.selenium.find_element(By.NAME, "password").send_keys(password)
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # --- 成功系 -----------------------------------------------------------
    def test_login_success(self):
        self.login()

        assert not self.selenium.current_url.endswith(reverse("account_login"))
        assert reverse("main") in self.selenium.current_url
        assert self.selenium.find_elements(By.NAME, "tweet-sentence")

    # --- 異常系 -----------------------------------------------------------
    def test_login_failure(self):
        self.selenium.get(f"{self.live_server_url}{reverse('account_login')}")
        self.selenium.find_element(By.NAME, "login").send_keys("myuser@example.com")
        self.selenium.find_element(By.NAME, "password").send_keys("wrongpass")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        assert self.selenium.current_url.endswith(reverse("account_login"))
        page = self.selenium.page_source
        assert ("メールアドレスを入力してください" in page)

    # # ======================================================================
    # # 3. ツイート
    # # ======================================================================
    # # --- 正常系
    def test_tweet_success(self):
        self.login()
        self.selenium.get(f"{self.live_server_url}{reverse('main')}")

        before = TweetModel.objects.count()
        msg = f"E2E tweet {uuid.uuid4().hex[:4]}"
        self.selenium.find_element(By.NAME, "tweet-sentence").send_keys(msg)
        self.selenium.find_element(By.ID, "tweet-submit").click()

        assert reverse("main") in self.selenium.current_url
        assert msg in self.selenium.page_source
        assert TweetModel.objects.count() == before + 1

    # # --- 異常系
    def test_tweet_empty(self):
        self.login()
        self.selenium.get(f"{self.live_server_url}{reverse('main')}")

        before = TweetModel.objects.count()
        self.selenium.find_element(By.ID, "tweet-submit").click()

        assert reverse("main") in self.selenium.current_url
        assert TweetModel.objects.count() == before