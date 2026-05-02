from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_wiew(["GET"])
def demo_api(request):
    return Response({
        "id": 1,
        "title": "demo",
        "message": "API working"
    })



