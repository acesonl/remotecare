import re
from django.utils.translation import ugettext_lazy as _
from django.forms.utils import ErrorList
from django.contrib.auth.hashers import check_password
from apps.account.models import OldPassword


def clean_data_mobile_number(form, field='mobile_number'):
    '''
    Performs checks on mobile number, should be one of the following:
    +31612345678
    0612345678
    '''
    cleaned_data = form.cleaned_data
    mobile_number = cleaned_data[field]
    error = False

    if not re.match(r'^[0-9+]*$', mobile_number):
        form.errors[field] = ErrorList(
            [_('Alleen cijfers en + aan het begin is toegestaan.')])
        error = True

    if not error:
        if(mobile_number[0:4] == '+316' and len(mobile_number) != 12):
            error = True
            form.errors[field] = ErrorList(
                [_('Formaat +31612345678, geen spaties.')])
        elif(mobile_number[0:2] == '06' and len(mobile_number) != 10):
            error = True
            form.errors[field] = ErrorList(
                [_('Formaat 0612345678, geen spaties.')])
        elif(mobile_number[0:4] != '+316' and mobile_number[0:2] != '06'):
            form.errors[field] = ErrorList(
                [_('Formaat 0612345678 of +31612345678, geen spaties.')])


def clean_data_password(form, field='password', field2='password2'):
    '''
    Performs an elaborate check on passwords
    conform the security demands of Amsterdam Medical Centrum (AMC)
    '''
    cleaned_data = form.cleaned_data
    # check if the password strength is good enough..
    # based on:
    #    * Minimum 8 characters in length
    #    * Minimum of 1 uppercase letter
    #    * Minimum of 1 lowercase letter
    #    * Minimum of 2 numbers
    #    * no repeating chars > 2
    #    * no subsection of alphabet > 2 (and reverse)
    #    * no subsection of numbers (0123456789) > 2 (and reverse)
    #    * no subsection of strokes on keyboard > 2 (and reverse)
    #    * Different from last 20 passwords

    password = cleaned_data[field]

    minimum_one_lower_case = r'.*[a-z]'
    minimum_one_upper_case = r'.*[A-Z]'
    minimum_two_numbers = r'.*[0-9].*[0-9]'
    range1 = 'abcdefghijklmnopqrstuvwxyz'
    range2 = '0123456789'
    range3 = 'qwertyuiop'
    range4 = 'asdfghjkl;'
    range5 = 'zxcvbnm,.'

    error = False
    if len(password) < 8:
        form.errors[field] = ErrorList(
            [_('Wachtwoord moet tenminste 8 tekens lang zijn.')])
        error = True

    reverse_password = password[::-1]

    # Check repeating characters
    if not error:
        for index in range(0, len(password) - 2):
            password_str = password[index:index + 3]
            # test repeating chars
            if ((not error and password_str[0] ==
                 password_str[1] and password_str[1] == password_str[2])):
                form.errors[field] = ErrorList(
                    [_('Wachtwoord bevat 3 dezelfde tekens.')])
                error = True

    # Check alphabet
    if not error:
        for index in range(0, len(range1) - 2):
            range_str = range1[index:index + 3]
            if not error:
                if re.search(range_str, password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende' +
                           ' letters uit alfabet')])
                    error = True
                elif re.search(range_str, reverse_password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende' +
                           'letters uit omgekeerd alfabet')])
                    error = True
    # Check 0-9
    if not error:
        for index in range(0, len(range2) - 2):
            range_str = range2[index:index + 3]
            if not error:
                if re.search(range_str, password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende' +
                           ' cijfers uit 0-9')])
                    error = True
                elif re.search(range_str, reverse_password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende' +
                           ' cijfers uit 9-0')])
                    error = True

    # Check keyboard
    if not error:
        for index in range(0, len(range3) - 2):
            range_str = range3[index:index + 3]
            if not error:
                # print range_str, password, re.I

                if re.search(range_str, password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende' +
                           'tekens uit een rij van het toetsenbord')])
                    error = True
                elif re.search(range_str, reverse_password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende' +
                           'tekens uit een omgekeerde rij van' +
                           ' het toetsenbord')])
                    error = True
    if not error:
        for index in range(0, len(range4) - 2):
            range_str = range4[index:index + 3]
            if not error:
                if re.search(range_str, password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende tekens' +
                           'uit een rij van het toetsenbord')])
                    error = True
                elif re.search(range_str, reverse_password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende tekens' +
                           'uit een omgekeerde rij van het toetsenbord')])
                    error = True
    if not error:
        for index in range(0, len(range5) - 2):
            range_str = range5[index:index + 3]
            if not error:
                if re.search(range_str, password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende tekens' +
                           'uit een rij van het toetsenbord')])
                    error = True
                elif re.search(range_str, reverse_password, re.I):
                    form.errors[field] = ErrorList(
                        [_('Wachtwoord bevat 3 opeenvolgende tekens' +
                           'uit een omgekeerde rij van het toetsenbord')])
                    error = True

    if not error:
        if not re.match(minimum_one_lower_case, password):
            form.errors[field] = ErrorList([_('1 kleine letter is verplicht')])
            error = True
        elif not re.match(minimum_one_upper_case, password):
            form.errors[field] = ErrorList([_('1 hoofdletter is verplicht')])
            error = True
        elif not re.match(minimum_two_numbers, password):
            form.errors[field] = ErrorList([_('2 cijfers zijn verplicht')])
            error = True

    if not error:
        # Check if not old password!!
        already_used = False
        oldpasswords = OldPassword.objects.filter(
            user=form.user).order_by('-pk')[:20]
        for oldpassword in oldpasswords:
            if check_password(password, oldpassword.password_hash):
                already_used = True

        # also check current password..
        if check_password(password, form.user.password):
            error = True
            form.errors[field] = ErrorList(
                [_('Wachtwoord is zelfde als huidig wachtwoord')])
        elif already_used:
            error = True
            form.errors[field] = ErrorList(
                [_('Zelfde als een van de laatste 20 wachtwoorden')])

    if error:
        del cleaned_data[field]
        del cleaned_data[field2]

    return error
