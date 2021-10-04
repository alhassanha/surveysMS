from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework.decorators import action
from django.utils import timezone
# Create your views here.


class SurveyViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticatedOrReadOnly()]
        elif self.action == 'submit':
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Survey.objects.all()
        else:
            now = timezone.now()
            print(now)
            condition = Q(end_date__gte=now)
            condition.add(Q(end_date__isnull=True), Q.OR)
            condition.add(Q(start_date__lte=now), Q.AND)
            return Survey.objects.filter(condition)

    def get_serializer_class(self):
        if 'retrieve' == self.action:
            return DetailedSurveySerializer
        else:
            return SurveySerializer

    def create(self, request, *args, **kwargs):
        serializer = SurveySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_survey = serializer.create(serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = SurveySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_obj = serializer.update(obj, serializer.validated_data)
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self.perform_destroy(obj)
        return Response(
            {"success": "element was deleted!"},
            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def submit(self, request, pk=None):
        survey = self.get_object()
        if request.user.is_authenticated and None != request.user.participant:
            participant = request.user.participant
        elif 'participant' in request.data:
            participant_id = request.data.get('participant')
            participant, created = Participant.objects.get_or_create(id=participant_id)
            if request.user.is_authenticated:
                participant.user = request.user
                participant.save()
        else:
            return Response(
                {"detail": "no participant id was provided"},
                status.HTTP_400_BAD_REQUEST
            )
        answers = request.data.get('answers', [])
        for answer in answers:
            if 'question' not in answer:
                return Response(
                    {"detail": "question id was not provided"},
                    status.HTTP_400_BAD_REQUEST
                )
            question = Question.objects.get(id=answer.get('question'))
            if 'options' in answer:
                answer_options = answer.get('options')
                for option in question.options.all():
                    if option.id in answer_options:
                        Answer.objects.create(
                            user=participant,
                            survey=survey,
                            question=question,
                            option=option
                        )
            elif 'text' in answer:
                Answer.objects.create(
                    user=participant,
                    survey=survey,
                    question=question,
                    text=answer.get('text')
                )
            else:
                return Response(
                    {"detail": "every answer should have \"options\" field or \"text\" field"},
                    status.HTTP_400_BAD_REQUEST)
        return Response(
            {"success": "All answers was submitted successfully"},
            status=status.HTTP_200_OK)

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        if 'survey_id' in self.request.query_params and self.request.query_params['survey_id'] != '':
            survey_id = self.request.query_params['survey_id']
            return Question.objects.filter(survey__id = survey_id)
        else:
            return Question.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticatedOrReadOnly()]
        else:
            return [permissions.IsAdminUser()]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self.perform_destroy(obj)
        return Response(
            {"success": "element was deleted!"},
            status=status.HTTP_200_OK)


class UserSurveysListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSolvedSurveysSerializer

    def get_queryset(self):
        if 'user' not in self.request.query_params:
            return []
        user = self.request.query_params.get('user')
        return Survey.objects.filter(answers__user__id=user).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

