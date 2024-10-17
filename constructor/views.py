import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Models
def main_page(request):
    return render(request, 'constructor/index.html')

def start(request):
    return render(request, 'constructor/constructor-run.html')

def checkName(request):
    if request.method == 'POST':
        name = json.loads(request.body)['name']
        names = Models.objects.values_list('name', flat=True)

        if name in names:
            return JsonResponse(
                {'success': False, 'error': 'Извините, это имя модели уже занято'})
        if len(name) < 3 and len(name) <= 20:
            return JsonResponse({'success': False, 'error': 'Имя модели должно иметь минимум 3 символа, но максимум 20'})
        if name[0].isdigit():
            return JsonResponse(
                {'success': False, 'error': 'Имя модели должно начинаться с буквы'})
        return JsonResponse({'success': True})

def checkModel(request):
    if request.method == 'POST':
        file = request.FILES['file']
        name = request.POST['name']
        data = request.POST['data']

        if file and data and name:

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})