# coding=utf-8
import datetime
from django.contrib.auth.models import Group
from apps.account.models import User, EncryptionKey
from apps.api.serializers import QuestionnaireSerializer
from apps.questionnaire.models import QuestionnaireRequest, get_model_class

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.api.models import APIUser, Token
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from core.encryption.hash import check_hash, create_hash
from core.encryption.random import randomkey, randomid
from django.conf import settings
from apps.api.models import TempPatientData, PatientCoupling, HealthProfessionalCoupling
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.lists.models import Hospital
from django.forms.models import model_to_dict
from core.models import ChoiceOtherField, ManyToManyField
from django.db.models.fields.related import OneToOneField

class MissingParameters(Exception):
    pass


class LoginException(Exception):
    pass


class IncorrectPatient(Exception):
    pass


class IncorrectHealthProfessional(Exception):
    pass



# Redirect views

class LoginAndShowPatient(View):
    """
    Redirect to patient details page
    """
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(LoginAndShowPatient, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if (('external_healthprofessional_id' not in request.POST or 'random_key' not in request.POST or 'values_hash' not in request.POST
             or 'external_patient_id' not in request.POST)):
            raise MissingParameters('external_healthprofessional_id, random_key, values_hash and external_patient_id are mandatory')

        username = 'drift'
        external_healthprofessional_id = request.POST['external_healthprofessional_id']
        values_hash = request.POST['values_hash']
        random_key = request.POST['random_key']
        external_patient_id = request.POST['external_patient_id']
        hash_to_check = "{0}{1}{2}{3}".format(external_healthprofessional_id, random_key, external_patient_id, settings.API_HASH_KEY)

        if check_hash(hash_to_check, values_hash):
            try:
                patient_coupling = PatientCoupling.objects.get(
                    external_patient_id=external_patient_id,
                    api_user__username=username)
            except PatientCoupling.DoesNotExist:
                raise IncorrectPatient("Coupling for patient not found")

            patient = patient_coupling.patient

            try:
                healthprofessional = HealthProfessionalCoupling.objects.get(
                    external_healthprofessional_id=external_healthprofessional_id).healthprofessional
            except HealthProfessionalCoupling.DoesNotExist:
                raise IncorrectHealthProfessional("Healthprofessional not found")

            # login as the user_id..
            user = healthprofessional.user
            user.backend = 'core.backends.EmailBackend'
            login(request, user)
        else:
            raise LoginException("Incorrect hash or other parameters")

        patient_session_id = randomkey()
        request.session[patient_session_id] = 'storage_' + str(patient.id)
        next_url = reverse('patient_view_personalia', args=[patient_session_id])


        # Redirect the user to change password if password is unusable
        if not user.has_usable_password():
            request.session['next_url'] = next_url
            healthprofessional_id = randomkey()
            request.session[healthprofessional_id] = 'storage_' + str(healthprofessional.id)
            next_url = reverse('healthprofessional_set_password', args=[healthprofessional_id])

        return HttpResponseRedirect(next_url)


class LoginAndAddNewPatient(View):
    """
    Redirect to new patient page
    """
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(LoginAndAddNewPatient, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # try to login and redirect

        # validate request

        if (('external_healthprofessional_id' not in request.POST or 'random_key' not in request.POST or 'values_hash' not in request.POST
             or 'temppatientdata_id' not in request.POST)):
            raise MissingParameters('external_healthprofessional_id, random_key, values_hash and temppatientdata_id are mandatory')

        external_healthprofessional_id = request.POST['external_healthprofessional_id']
        values_hash = request.POST['values_hash']
        random_key = request.POST['random_key']
        temppatientdata_id = request.POST['temppatientdata_id']
        hash_to_check = "{0}{1}{2}{3}".format(external_healthprofessional_id, random_key, temppatientdata_id, settings.API_HASH_KEY)


        if check_hash(hash_to_check, values_hash):
            # login as the user_id..
            try:
                healthprofessional = HealthProfessionalCoupling.objects.get(
                    external_healthprofessional_id=external_healthprofessional_id).healthprofessional
            except HealthProfessionalCoupling.DoesNotExist:
                raise IncorrectHealthProfessional("Healthprofessional not found")

            user = healthprofessional.user
            user.backend = 'core.backends.EmailBackend'
            login(request, user)
        else:
            raise LoginException("Incorrect hash or other parameters")

        next_url = reverse('patient_add') + "?temppatientdata_id={0}".format(temppatientdata_id)

        # Redirect the user to change password if password is unusable
        if not user.has_usable_password():
            request.session['next_url'] = next_url
            healthprofessional_id = randomkey()
            request.session[healthprofessional_id] = 'storage_' + str(healthprofessional.id)
            next_url = reverse('healthprofessional_set_password', args=[healthprofessional_id])

        return HttpResponseRedirect(next_url)


# API VIEWS


class ObtainAuthToken(APIView):
    permission_classes = ()

    def post(self, request):
        try:
            user = APIUser.objects.get(username='drift')

            # validate user

        except APIUser.DoesNotExist:
            return Response({'Incorrect username or password'}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': unicode(token.key)})


class PatientExists(APIView):
    """
    Checks if the patiënt exists
    """
    def get(self, request, username, external_patient_id, format=None):
        try:
            PatientCoupling.objects.get(
                external_patient_id=external_patient_id,
                api_user__username=username)
            exists = True
        except PatientCoupling.DoesNotExist:
            exists = False

        return Response({'exists': exists})


class HealthProfessionalExists(APIView):
    """
    Checks if the patiënt exists
    """
    def get(self, request, username, external_healthprofessional_id, format=None):
        try:
            HealthProfessionalCoupling.objects.get(
                external_healthprofessional_id=external_healthprofessional_id,
                api_user__username=username)
            exists = True
        except HealthProfessionalCoupling.DoesNotExist:
            exists = False

        return Response({'exists': exists})


class AddHealthProfessional(APIView):
    """
    Checks if the patiënt exists
    """
    def add_healthprofessional(self, first_name, last_name, email, mobile_number):
        if User.objects.filter(hmac_email=email).count() == 0:
            user = User()
            key = EncryptionKey(key=randomid())
            key.save()
            user.personal_encryption_key = key
            user.first_name = first_name
            user.last_name = last_name

            user.email = email
            user.set_password('!')
            user.date_of_birth = datetime.date(1980, 5, 1)
            user.mobile_number = mobile_number
            user.gender = 'male'
            user.initials = first_name[0].upper() + '.'
            user.BSN = ''
            user.hospital = Hospital.objects.get(id=1)
            user.local_hospital_number = ''
            user.disable_auditing = True
            # Cannot be null??
            user.last_login = datetime.datetime.now()
            user.save()
            user.groups = [Group.objects.get(name='healthprofessionals')]
            user.save()

            healthprofessional = HealthProfessional()
            healthprofessional.function = 'specialist'
            healthprofessional.specialism = 'gastro_liver_disease'
            healthprofessional.telephone = mobile_number
            healthprofessional.changed_by_user = user
            healthprofessional.save()
            user.healthperson = healthprofessional
            user.save()

            return healthprofessional
        else:
            return User.objects.filter(hmac_email=email)[0].healthperson


    def post(self, request, username, external_healthprofessional_id, format=None):
        validate_list = ['first_name', 'last_name', 'mobile_number', 'email']
        for item in validate_list:
            if item not in request.data:
                raise MissingParameters("Parameter: {0} is mandatory".format(item))

        try:
            api_user = APIUser.objects.get(username=username)
        except APIUser.DoesNotExist:
            raise LoginException("API user does not exist")

        healthprofessional = self.add_healthprofessional(
            first_name=request.data['first_name'],
            last_name=request.data["last_name"],
            email=request.data['email'],
            mobile_number=request.data['mobile_number']
        )


        healthprofessional_coupling = HealthProfessionalCoupling(
            api_user=api_user,
            external_healthprofessional_id=external_healthprofessional_id,
            healthprofessional=healthprofessional)
        healthprofessional_coupling.save()

        return Response({'added': True})


class PrepareNewPatient(APIView):
    """
    Prepare a new patient.
    Returns the URL for direct login & adding the new patient
    """
    def post(self, request, username, external_patient_id, external_healthprofessional_id, format=None):
        # save the temporary patient data
        initial = request.data
        try:
            healthprofessional = HealthProfessionalCoupling.objects.get(
                external_healthprofessional_id=external_healthprofessional_id).healthprofessional
        except HealthProfessionalCoupling.DoesNotExist:
            raise IncorrectHealthProfessional("Healthprofessional not found")

        # initial.update({'gender': 'male'})
        # initial.update({'date_of_birt': 'YYYY-MM-DD'})

        if username == 'drift':
            initial.update({'hospital': '1',
                            'diagnose': 'intestinal_transplantation'})

        initial.update({'current_practitioner': healthprofessional.id,
                        'external_patient_id': external_patient_id,
                        'API_username': username})

        temp_patient_data = TempPatientData()
        temp_patient_data.set_json_data(initial)
        temp_patient_data.save()

        # return URL for adding patient
        random_key = randomkey()
        values_hash = "{0}{1}{2}{3}".format(
            external_healthprofessional_id, random_key, temp_patient_data.id, settings.API_HASH_KEY)
        return Response(
            {'url': reverse('login_and_add_patient'),
             'data': {'temppatientdata_id': temp_patient_data.id,
                      'random_key': random_key,
                      'external_healthprofessional_id': external_healthprofessional_id,
                      'values_hash': create_hash(values_hash)}})


class PrepareLoginAndShowPatient(APIView):
    """
    Prepare a new patient.
    Returns the URL for direct login & adding the new patient
    """
    def get(self, request, username, external_patient_id, external_healthprofessional_id, format=None):
        # return URL & params to post for login and showing patient

        try:
            HealthProfessionalCoupling.objects.get(
                external_healthprofessional_id=external_healthprofessional_id)
        except HealthProfessionalCoupling.DoesNotExist:
            return Response({'error': 'Healthprofessional could not be found'})

        try:
            PatientCoupling.objects.get(
                external_patient_id=external_patient_id)
        except PatientCoupling.DoesNotExist:
            return Response({'error': 'Patient could not be found'})

        random_key = randomkey()
        values_hash = "{0}{1}{2}{3}".format(
            external_healthprofessional_id, random_key, external_patient_id, settings.API_HASH_KEY)
        return Response(
            {'url': reverse('login_and_show_patient'),
             'data': {'external_patient_id': external_patient_id,
                      'random_key': random_key,
                      'external_healthprofessional_id': external_healthprofessional_id,
                      'values_hash': create_hash(values_hash)}})


class QuestionnaireList(APIView):
    """
    List all questionnaires for a given external_patient_id
    """
    def get(self, request, username, external_patient_id,  format=None):

        try:
            patient = PatientCoupling.objects.get(
                external_patient_id=external_patient_id,
                api_user__username=username).patient
        except PatientCoupling.DoesNotExist:
            return Response({'error': 'Patient could not be found'})

        questionaire_requests = QuestionnaireRequest.objects.filter(
            patient=patient)
        serializer = QuestionnaireSerializer(questionaire_requests, many=True)

        return Response(serializer.data)


class QuestionnaireDetails(APIView):
    """
    List all questionnaires for a given external_patient_id
    """
    def process_request_step(self, request_step):
        questionnaire = request_step.questionnaire
        new_data = {}
        if questionnaire is not None:
            data = model_to_dict(questionnaire)
            del data['id']
            del data['request_step']

            new_data = {}
            for attname in data:
                field = questionnaire._meta.get_field_by_name(attname)[0]
                value = data[attname]

                process = True
                if value is not None:
                    if isinstance(field, OneToOneField):
                        process = False
                    elif isinstance(field, ChoiceOtherField):
                        test_value = [x[1] for x in field.choices if x[0] == value]
                        if len(test_value) > 0:
                            value = test_value[0]
                    elif isinstance(field, ManyToManyField):
                        manager = getattr(questionnaire, field.attname)
                        value = [x[0] for x in manager.all().values_list('name')]
                    elif hasattr(field, 'choices') and len(field.choices) > 0:
                        value = [x[1] for x in field.choices if x[0] == value][0]

                if process:
                    new_data.update({field.verbose_name: value})

        data = {'name': request_step.model_class.display_name,
                'step_nr': request_step.step_nr,
                'data': new_data}

        return data

    def get(self, request, username, external_patient_id, questionnaire_id,  format=None):

        try:
            patient = PatientCoupling.objects.get(
                external_patient_id=external_patient_id,
                api_user__username=username).patient
        except PatientCoupling.DoesNotExist:
            return Response({'error': 'Patient could not be found'})

        try:
            questionnaire_request = QuestionnaireRequest.objects.get(
                patient=patient, id=questionnaire_id)
        except QuestionnaireRequest.DoesNotExist:
            return Response({'error': 'Questionnaire does not exist'})

        serializer = QuestionnaireSerializer(questionnaire_request, many=False)

        data = serializer.data
        qr_data = []
        for request_step in questionnaire_request.requeststep_set.all().order_by('step_nr'):
            qr_data.append(self.process_request_step(request_step))
        data.update({'steps': qr_data})

        return Response(data)
