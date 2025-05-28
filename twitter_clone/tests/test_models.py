from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserModelValidationTests(TestCase):
    def test_jikken(self):
        x = 1
        y = 1
        self.assertEqual(x, y)
        # self.assertEqual(2, 1)
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])

    def test_is_empty(self):
        saved_user = CustomUser.objects.all()
        self.assertEqual(saved_user.count(), 0)
    def test_is_valid_email_true(self):
        self.assertTrue(CustomUser.is_valid_email('test@example.com'))

    def test_is_valid_email_false(self):
        self.assertFalse(CustomUser.is_valid_email('invalid-email'))

    def test_is_valid_phone_number_true(self):
        self.assertTrue(CustomUser.is_valid_phone_number('08012345678'))

    def test_is_valid_phone_number_false(self):
        self.assertFalse(CustomUser.is_valid_phone_number('12345'))

    def test_get_user_from_session(self):
        user = CustomUser.objects.create(username='user', email='user@example.com', tel='08012345678')
        session = {'user_id': user.id}
        self.assertEqual(CustomUser.get_user_from_session(session), user)

    def test_get_user_from_session_raise(self):
        with self.assertRaises(ObjectDoesNotExist):
            CustomUser.get_user_from_session({})