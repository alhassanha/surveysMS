from rest_framework import serializers
from .models import *
from collections import OrderedDict


class SurveySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True)
    start_date = serializers.DateTimeField(required=False, default=datetime.now())
    end_date = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = Survey
        fields = ('__all__')

    def update(self, instance, validated_data):
        validated_data.pop('start_date', None)
        return super().update(instance, validated_data)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('__all__')


class OptionListSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField(source='id')

    class Meta:
        model = Option
        fields = ('option_id', 'text')


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'text', 'type', 'survey', 'options')

    def to_representation(self, instance):
        self.fields['options'] = OptionListSerializer(source='get_options', many=True)
        return super().to_representation(instance)

    def create(self, validated_data):
        options = validated_data.pop('options') if ('options' in validated_data) else []
        question = Question.objects.create(**validated_data)
        for option in options:
            Option.objects.create(question=question, text=option)
        return question

    def update(self, instance, validated_data):
        options = validated_data.pop('options') if ('options' in validated_data) else []
        super().update(instance, validated_data)
        deleted_options = []
        for option in instance.options.all():
            if option.text in options:
                options.remove(option.text)
            else:
                deleted_options.append(option)
        for deleted_option in deleted_options:
            if options:
                deleted_option.text = options.pop()
                deleted_option.save()
            else:
                deleted_option.delete()
        for option in options:
            Option.objects.create(question=instance, text=option)
        return instance

class DetailedSurveySerializer(SurveySerializer):
    questions = QuestionSerializer(many=True)


class AnswerSerializer(serializers.ModelSerializer):
    option = OptionListSerializer()

    class Meta:
        model=Answer
        fields = ('option', 'text')

    def to_representation(self, instance):
        result = super(AnswerSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class AnsweredQuestionSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='id')
    answer = serializers.SerializerMethodField('get_answer')

    class Meta:
        model = Question
        fields = ('question_id', 'text', 'answer')

    def get_answer(self, obj):
        queryset = obj.answers.filter(user__id=self.context['request'].query_params.get('user'))
        return AnswerSerializer(queryset, many=True).data


class UserSolvedSurveysSerializer(serializers.ModelSerializer):
    survey_id = serializers.IntegerField(source='id')
    answers = serializers.SerializerMethodField('get_answers')

    class Meta:
        model = Survey
        fields = ('survey_id', 'name', 'answers')

    def get_answers(self, obj):
        return AnsweredQuestionSerializer(obj.questions.all(), many=True, context=self.context).data
