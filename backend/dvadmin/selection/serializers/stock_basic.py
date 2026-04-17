from rest_framework import serializers
from dvadmin.selection.models import StockBasic

class StockBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockBasic
        fields = "__all__"
