from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Survey(models.Model):
    """опрос"""
    name = models.CharField(null=False, max_length=255)
    start_date = models.DateTimeField(null=False, editable=False)
    end_date = models.DateTimeField(null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    """Вопрос из опроса"""
    ANSWER_TYPES = (
        ('TEXT', _('ответ текстом')),
        ('SINGLE', _('ответ с выбором одного варианта')),
        ('MULTIPLE', _('ответ с выбором нескольких вариантов')),
    )

    text = models.TextField(blank=False, null=False)
    type = models.CharField(choices=ANSWER_TYPES, default='TEXT', max_length=127)
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)

    @property
    def get_options(self):
        return self.options.all()
        # return [option.text for option in self.options.all()]

class Option(models.Model):
    """Вариант ответа на вопрос"""
    text = models.TextField(blank=False, null=False)
    question = models.ForeignKey(
        Question,
        related_name='options',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.text


# class SurveyQuestion(models.Model):
#     """Связь вопросов с опросами"""
#     survey = models.ForeignKey(
#         Survey,
#         related_name='survey_questions',
#         on_delete=models.CASCADE
#     )
#     question = models.ForeignKey(
#         Question,
#         related_name='survey_questions',
#         on_delete=models.CASCADE
#     )

# class SurveyQuestionOption(models.Model):
#     """Связь варианта в вопросом в определенном опросе.
#     Так как варианты вопроса могут отличаться в зависимости от опроса"""
#
#     survey_question = models.ForeignKey(
#         SurveyQuestion,
#         related_name='question_options',
#         on_delete=models.CASCADE
#     )
#     option = models.ForeignKey(
#         Option,
#         related_name='question_options',
#         on_delete=models.CASCADE
#     )

class Participant(models.Model):
    """Пользователь: он может быть аутентифицирован (связан с реальным
    пользователем в таблице auth_user) или анонимным."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='participant')

class Answer(models.Model):
    """ответ ползователя"""
    user = models.ForeignKey(
        Participant,
        related_name='answers',
        on_delete=models.CASCADE
    )
    survey = models.ForeignKey(
        Survey,
        null=False,
        related_name='answers',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question,
        null=False,
        related_name='answers',
        on_delete=models.CASCADE
    )
    option = models.ForeignKey(
        Option,
        null=True,
        related_name='answers',
        on_delete=models.CASCADE
    )

    text = models.TextField(null=True)

