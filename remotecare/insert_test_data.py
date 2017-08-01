import sys
import os
import django
import time
import random
sys.path.append('/srv/remotecare/default/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'remotecare.settings'
django.setup()
#settings.configure()
from django.contrib.auth.models import Group
from apps.account.models import User, EncryptionKey
from core.encryption.random import randomid
from apps.questionnaire.models import QuestionnaireRequest, RequestStep,\
    AVAILABLE_CONTROL_QUESTIONNAIRE_LIST
from apps.healthperson.patient.models import Patient, DIAGNOSIS_CHOICES,\
    REGULAR_CONTROL_FREQ, BLOOD_SAMPLE_FREQ, CLINIC_VISIT_CHOICES
from apps.healthperson.healthprofessional.models import HealthProfessional,\
    FUNCTION_CHOICES, SPECIALISM_CHOICES
from apps.healthperson.secretariat.models import Secretary
from apps.lists.models import Hospital

from apps.healthperson.management.models import Manager
#sys.path.append('/srv/remotecare/default/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'remotecare.settings'
#django.setup()
#settings.configure()


def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%Y-%m-%d', prop)


def add_group(group_name):
    if Group.objects.filter(name=group_name).count() == 0:
        g = Group()
        g.name = group_name
        g.save()


def add_groups():
    add_group('managers')
    add_group('secretariat')
    add_group('healthprofessionals')
    add_group('patients')


def add_profile_to_default_user():
    print(('adding manager@example.com'))

    if User.objects.filter(hmac_email='manager@example.com').count() == 0:
        user = User()
        key = EncryptionKey(key=randomid())
        key.save()
        user.personal_encryption_key = key
        user.mobile_number = '0612345678'
        user.initials = 'M.'
        user.gender = 'male'
        user.BSN = '1234567890'
        user.set_password('remotecare')
        user.date_of_birth =\
            randomDate("1980-01-01", "2001-01-01", random.random())

        user.is_staff = True
        user.is_superuser = True

        # Set extra data
        user.hospital = random.choice(Hospital.objects.all())
        user.last_name = 'Anager'
        user.first_name = 'M.'
        user.email = 'manager@example.com'
        user.disable_auditing = True
        user.save()

        user.groups = [Group.objects.get(name='managers')]
        manager = Manager()
        manager.save()
        user.healthperson = manager
        user.save()


def add_questionnaires():
    # random add a questionnaire to all patients
    print('adding questionnaires')
    # for q in QuestionnaireRequest.objects.all():
    #    q.delete()

    patients = Patient.objects.all()
    for patient in patients:
        # add request

        questionnaire_list = None
        for l in AVAILABLE_CONTROL_QUESTIONNAIRE_LIST:
            if l[0] == patient.diagnose:
                questionnaire_list = l[1]

        # questionnaire_list =
        # random.choice(AVAILABLE_CONTROL_QUESTIONNAIRE_LIST)[1]
        qr = QuestionnaireRequest(patient=patient)
        qr.deadline = randomDate("2013-01-23", "2013-01-25", random.random())
        qr.deadline_nr = 1
        qr.patient_diagnose = patient.diagnose
        qr.practitioner = patient.current_practitioner
        qr.disable_auditing = True
        qr.save()

        # add steps of request.
        step = 1
        for questionnaire in questionnaire_list:
            qr_step = RequestStep()
            qr_step.questionnairerequest = qr
            qr_step.step_nr = step
            qr_step.model = questionnaire
            step = step + 1
            qr_step.save()


def add_secretariat():
    add_secretary('Monica', 'Spencer', 'monica@example.com', '0612345678')
    add_secretary('Jim', 'Dunn', 'jim@example.com', '0612345678')


def add_healthprofessionals():
    add_healthprofessional(
        'Gerald', 'Smith', 'gerald@example.com', '0612345678')
    add_healthprofessional(
        'Henry', 'Jones', 'henry@example.com', '0612345678')


def add_patients():
    add_patient('Frank', 'Davis', 'frank@example.com', '0612345678')
    add_patient('Jeffrey', 'Moore', 'jeffrey@example.com', '0612345678')
    add_patient('Dominique', 'Jeffreysen', 'dominique@example.com', '0612345678')
    add_patient('Patrick', 'Henrys', 'patrick@example.com', '0612345678')
    add_patient('Maria', 'Cook', 'maria@example.com', '0612345678')

    add_patient('Henry', 'Lewis', 'harry@example.com', '0612345678')
    add_patient('Bill', 'Murphy', 'bill@example.com', '0612345678')
    add_patient('Hobart', 'Stevens', 'hobart@example.com', '0612345678')
    add_patient('Cindy', 'Stone', 'cindy@example.com', '0612345678')
    add_patient('Trudy', 'Hunter', 'trudy@example.com', '0612345678')


def add_healthprofessional(firstname, surname, email, mobile_number):
    print(('adding healthprofessional ' + firstname + ' ' + surname))
    if User.objects.filter(hmac_email=email).count() == 0:
        user = User()
        key = EncryptionKey(key=randomid())
        key.save()
        user.personal_encryption_key = key
        user.first_name = firstname
        user.last_name = surname

        user.email = email
        user.set_password('remotecare')
        user.date_of_birth =\
            randomDate("1980-01-01", "2001-01-01", random.random())
        user.mobile_number = mobile_number
        user.gender = 'male'
        user.initials = firstname[0].upper() + '.'
        user.BSN = '1234567890'
        user.hospital = random.choice(Hospital.objects.all())
        user.local_hospital_number = '1234567890'
        user.disable_auditing = True
        user.save()
        user.groups = [Group.objects.get(name='healthprofessionals')]
        user.save()

        healthprofessional = HealthProfessional()
        healthprofessional.function = random.choice(FUNCTION_CHOICES)[0]
        healthprofessional.specialism = random.choice(SPECIALISM_CHOICES)[0]
        healthprofessional.telephone = '0503049281'
        healthprofessional.changed_by_user = user
        healthprofessional.save()
        user.healthperson = healthprofessional
        user.save()


def add_patient(firstname, surname, email, mobile_number):
    print(('adding patient ' + firstname + ' ' + surname))
    if User.objects.filter(hmac_email=email).count() == 0:
        user = User()
        key = EncryptionKey(key=randomid())
        key.save()
        user.personal_encryption_key = key
        user.first_name = firstname
        user.last_name = surname
        user.email = email
        user.set_password('remotecare')
        user.date_of_birth =\
            randomDate("1980-01-01", "2001-01-01", random.random())
        user.mobile_number = mobile_number
        user.gender = 'male'
        user.initials = firstname[0].upper() + '.'
        user.BSN = '1234567890'
        user.hospital = random.choice(Hospital.objects.all())
        user.local_hospital_number = '1234567890'
        user.disable_auditing = True
        user.save()

        user.groups = [Group.objects.get(name='patients')]
        user.save()

        patient = Patient()
        patient.rc_registration_number = randomid()
        patient.diagnose = random.choice(DIAGNOSIS_CHOICES)[0]
        patient.current_practitioner =\
            random.choice(HealthProfessional.objects.all())
        patient.regular_control_frequency =\
            random.choice(REGULAR_CONTROL_FREQ)[0]
        patient.blood_sample_frequency = random.choice(BLOOD_SAMPLE_FREQ)[0]
        patient.always_clinic_visit = random.choice(CLINIC_VISIT_CHOICES)[0]
        patient.changed_by_user = user
        patient.save()
        user.healthperson = patient
        user.save()


def add_secretary(firstname, surname, email, mobile_number):
    print(('adding secretary ' + firstname + ' ' + surname))
    if User.objects.filter(hmac_email=email).count() == 0:
        user = User()
        key = EncryptionKey(key=randomid())
        key.save()
        user.personal_encryption_key = key
        user.first_name = firstname
        user.last_name = surname
        user.email = email
        user.set_password('remotecare')
        user.date_of_birth =\
            randomDate("1980-01-01", "2001-01-01", random.random())
        user.mobile_number = mobile_number
        user.gender = 'male'
        user.initials = firstname[0].upper() + '.'
        user.BSN = '1234567890'
        user.hospital = random.choice(Hospital.objects.all())
        user.local_hospital_number = '1234567890'
        user.disable_auditing = True
        user.save()

        user.groups = [Group.objects.get(name='secretariat')]
        user.save()

        secretary = Secretary()
        secretary.specialism = random.choice(SPECIALISM_CHOICES)[0]
        secretary.changed_by_user = user
        secretary.save()
        user.healthperson = secretary
        user.save()

if __name__ == '__main__':
    print('inserting')
    add_groups()
    add_profile_to_default_user()

    add_healthprofessionals()
    add_patients()
    add_secretariat()

    add_questionnaires()
