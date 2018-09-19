from rest_framework import serializers
from .models import (Consumer, CreditRequest)

class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = (
            'first_name',
            'second_name',
            'phone_number',
        )

class CreditRequestSerializerCRUD(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = (
            'consumer',
            'status_ml',
            'status_ma',
            'seniority',
            'home',
            'time',
            'age',
            'marital',
            'records',
            'job',
            'expenses',
            'income',
            'assets',
            'debt',
            'amount',
            'price'
        )

class CreditRequestSerializerView(serializers.ModelSerializer):
    consumer = ConsumerSerializer(read_only=False)

    class Meta:
        model = CreditRequest
        fields = (
            'consumer',
            'created',
            'status_ml',
            'status_ma',
            'seniority',
            'home',
            'time',
            'age',
            'marital',
            'records',
            'job',
            'expenses',
            'income',
            'assets',
            'debt',
            'amount',
            'price'
        )