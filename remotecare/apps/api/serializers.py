# -*- coding: utf-8 -*-
from rest_framework import serializers
from apps.account.models import User
from apps.questionnaire.models import QuestionnaireRequest, RequestStep


class UserSerializer(serializers.ModelSerializer):
    hospital = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                  'title', 'initials', 'prefix',
                  'mobile_number', 'gender', 'hospital',
                  'date_of_birth')


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireRequest
        fields = ('id', 'urgent', 'created_on', 'finished_on', 'handled_on', 'deadline')