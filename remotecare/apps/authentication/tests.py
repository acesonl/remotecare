from datetime import datetime, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.hashers import check_password
from apps.account.models import User, PasswordChangeRequest, OldPassword
from core.unittest.baseunittest import BaseUnitTest
from core.encryption.hash import create_hmac
from apps.authentication.password_check import clean_data_mobile_number,\
    clean_data_password


class MockForm:
    errors = {}
    cleaned_data = {}
    user = None


class AuthenticationTest(BaseUnitTest):
    fixtures = ['test_data/test_users.json']

    def check_get_reset_password_email(self):
        PasswordChangeRequest.objects.all().delete()
        user = User.objects.all()[0]

        res = self.get(reverse('forgot_password'))
        res = self.post(reverse('forgot_password'), {'email': user.email})
        res = self.get(res.url)

        change_request = PasswordChangeRequest.objects.get(user=user)

        email = self.mail_outbox[0]
        request_sms_url = reverse('request_sms_code')
        index = email.body.index(request_sms_url)

        index_start = email.body.index('=', index)
        index_end = email.body.index('\n', index)
        key = email.body[index_start + 1:index_end]

        hmac_email_key = create_hmac(settings.EMAIL_KEY, str(key))

        self.assertEqual(
            change_request.hmac_email_key,
            hmac_email_key)

        return key

    def check_email_dob_validation(self, key):
        user = User.objects.all()[0]
        url = reverse('request_sms_code') + '?key=' + key
        res = self.get(url)

        form = res.context['form']
        form1 = form.__class__(initial={'email': user.email,
                                        'date_of_birth': user.date_of_birth})

        if form.prefix:
            prefix = form.prefix + '-'
        else:
            prefix = ''

        post_data = self.get_post_data(form1, prefix)
        res = self.post(url, post_data)

        self.assertEqual(self.SMS_STORE[0]['recipients'],
                         user.mobile_number)

        sms_code = settings.SMS_STORE[0]['message']
        hmac_sms_code = create_hmac(settings.SMS_KEY, str(sms_code))

        change_request = PasswordChangeRequest.objects.get(user=user)

        self.assertEqual(change_request.hmac_sms_code,
                         hmac_sms_code)

        return (res.url, sms_code)

    def check_sms_code_and_reset_password(self, url, sms_code):
        # Note: all passwords checks are checked in the test-cases
        # on the password check function directly
        password = 'Ae@d21Fls'

        res = self.get(url)
        res = self.post(url, {'password': password,
                              'password2': password,
                              'sms_code': sms_code})

        res = self.get(res.url)

        user = res.context['user']

        self.assertEqual(check_password(password, user.password), True)
        self.assertEqual(user.is_authenticated(), True)

    def check_timeouts_and_invalid_keys(self):
        self.reset_stores()
        user = User.objects.all()[0]
        PasswordChangeRequest.objects.all().delete()
        key = self.check_get_reset_password_email()

        # Check invalid e-mail key
        url = reverse('request_sms_code') + '?key=' + 'blaaaaaaaaat'
        res = self.get(url)
        self.assertIn('password_change_request_invalid.html',
                      res.templates[0].name)

        # Check valid e-mail key which is expired
        # Need to do a queryset update to bypass 'auto_now' of added_on field
        PasswordChangeRequest.objects.filter(user=user).update(
            added_on=datetime.now() - timedelta(days=+2))

        url = reverse('request_sms_code') + '?key=' + key
        res = self.get(url)
        self.assertIn('password_change_request_invalid.html',
                      res.templates[0].name)

        # Also check reset password
        url = reverse('reset_password') + '?key=' + key
        res = self.get(url)
        self.assertIn('password_change_request_invalid.html',
                      res.templates[0].name)

    def check_password_and_mobile_number_validation(self):
        # Mobile number invalid checks
        invalid_numbers = ['06421001av', '+31612345', '+3161234512312312',
                           '06123456781231', 'A0612345678', '0061231231']

        for mobile_number in invalid_numbers:
            form = MockForm()
            form.errors = {}
            form.cleaned_data = {'mobile_number': mobile_number}
            clean_data_mobile_number(form)
            self.assertEqual(len(form.errors), 1)

        # Mobile number valid checks
        valid_numbers = ['0612345678', '+31612345678']

        for mobile_number in valid_numbers:
            form = MockForm()
            form.errors = {}
            form.cleaned_data = {'mobile_number': mobile_number}
            clean_data_mobile_number(form)
            self.assertEqual(len(form.errors), 0)

        # Password invalid checks
        user = User.objects.all()[0]
        user.set_password('TestTestTest12@')
        user.changed_by_user = user
        user.save()

        old_password = OldPassword(user=user, password_hash=user.password)
        old_password.save()

        user.set_password('remoteCare12@')
        user.save()

        invalid_passwords = [
            '1234567', 'a2aaa#12Dafde@', '#1a23sDhij@#',
            '#1as12Djih@#', '@Afs23adDF456', '@Afsa12dDF654', '@Afsa23dDFqwe',
            '@Afsa23dDFewq', '@Afsa12dDFasd', '@Afs23adDFdsa', '@Af12sadDFzxc',
            '@Afs23adDFcxz', '@AfsgdDFzxc', 'aslkafdAGD@#', 'AGSDGA@#$132',
            'aagdga@#$132', 'TestTestTest12@', 'remoteCare12@']

        for password in invalid_passwords:
            form = MockForm()
            form.user = user
            form.errors = {}
            form.cleaned_data = {'password': password,
                                 'password2': password}
            clean_data_password(form)
            self.assertEqual(len(form.errors), 1)

        valid_passwords = ['mif19ieG', 'Dou43Kop', 'INgang51']

        for password in valid_passwords:
            form = MockForm()
            form.user = user
            form.errors = {}
            form.cleaned_data = {'password': password,
                                 'password2': password}
            clean_data_password(form)
            self.assertEqual(len(form.errors), 0)

    def test_forgot_password(self):
        self.reset_stores()

        # Step 1: fill in password an get e-mail
        key = self.check_get_reset_password_email()

        # Step 2: browse to link and fillin email + DOB and get smscode
        (url, sms_code) = self.check_email_dob_validation(key)

        # Step 3: filling smscode and new password
        self.check_sms_code_and_reset_password(url, sms_code)

        # Check reset password e-mail timeouts
        self.check_timeouts_and_invalid_keys()

        self.check_password_and_mobile_number_validation()
