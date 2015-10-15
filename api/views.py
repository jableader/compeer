from django.db.models import F

__author__ = 'Jableader'

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, detail_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from . import models
from .permissions import isOwnerOrReadOnly
from . import votes


####    User    ####

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        raw_password = validated_data['password']

        return User.objects.create_user(username, email, raw_password)

    def update(self, instance, validated_data):
        new_password = validated_data.get('password')
        if new_password is not None and not instance.check_password(new_password):
            instance.set_password(new_password)

@api_view(['POST', 'PUT'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

####    Item    ####

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        exclude = ('score',)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isOwnerOrReadOnly(models.Item))

####    List    ####

class ListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.List
        exclude = ('owner',)
        extra_kwargs = {'owner': {'write_only': True}}

    def create(self, validated_data):
        model = super(ListSerializer, self).create(validated_data)
        model.owner = validated_data.get('owner')

        return model

class VoteSerializer(serializers.Serializer):
    vote_token = serializers.CharField()
    winner = serializers.PrimaryKeyRelatedField(queryset=models.Item.objects.all())
    loser = serializers.PrimaryKeyRelatedField(queryset=models.Item.objects.all())

    def validate(self, attrs):
        if not votes.check_nonce(attrs['vote_token'], (attrs['winner'], attrs['loser'])):
            raise serializers.ValidationError("vote_token is invalid")
        return attrs

    def save(self):
        winner = self.validated_data['winner']
        winner.score += 1
        winner.save()

class ListViewSet(viewsets.ModelViewSet):
    queryset = models.List.objects.all()
    serializer_class = ListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isOwnerOrReadOnly(models.List))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @detail_route(methods=['GET'])
    def get_pair(self, request, pk=None):
        lst = get_object_or_404(models.List, pk=pk)
        pair = votes.get_pair(lst)
        nonce = votes.create_nonce(pair)
        pair_serializer = ItemSerializer(pair, many=True)

        return Response({'vote_token': nonce, 'pair': pair_serializer.data})

    @detail_route(methods=['POST'], permission_classes=[])
    def vote(self, request, pk=None):
        serializer = VoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(status=status.HTTP_200_OK)