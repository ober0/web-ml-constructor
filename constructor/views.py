import json
import os
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import UserModels, DataFields
from django.db import IntegrityError

def main_page(request):
    return render(request, 'constructor/index.html')

def start(request):
    return render(request, 'constructor/constructor-run.html')

def checkName(request):
    if request.method == 'POST':
        name = json.loads(request.body)['name']
        names = UserModels.objects.values_list('name', flat=True)

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
        data = json.loads(request.POST['data'])
        print(type(data), data)
        messages = {}

        if file and data and name:
            message = {
                'text': 'Данные загружены на сервер',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#33ff33'
            }
            messages[f'message{len(messages)}'] = message

            if file.size > 1024 * 1024 * 64:
                message = {
                    'text': 'Файл превышает 64мб',
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#ef0000'
                }
                messages[f'message{len(messages)}'] = message
                return JsonResponse({'success': False, 'messages': messages})

            file_name = f'{datetime.now().strftime("%H-%M-%S")}{file.name}'
            path = os.path.join(settings.DATASET_ROOT_DIR, file_name)

            with open(path, 'wb+') as f:
                for chunk in file.chunks():
                    try:
                        f.write(chunk)
                        message = {
                            'text': 'Файл сохранен на сервере',
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'color': '#33ff33'
                        }
                        messages[f'message{len(messages)}'] = message
                    except Exception as e:
                        message = {
                            'text': e,
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'color': '#ef0000'
                        }
                        messages[f'message{len(messages)}'] = message

            try:
                userModel = UserModels(name=name, DatasetPath=file_name)
                userModel.save()
                message = {
                    'text': 'Файл сохранен в базе данных',
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#33ff33'
                }
                messages[f'message{len(messages)}'] = message
            except Exception as e:
                if os.path.isfile(path):
                    os.remove(path)
                message = {
                    'text': e,
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#ef0000'
                }
                messages[f'message{len(messages)}'] = message
                return JsonResponse({'success': False, 'messages': messages})

            try:
                for el in data:
                    print(el)
                    name = el["name"]
                    datatype = el["datatype"]
                    predict = True if el["predict"] == 'True' else False

                    try:
                        dataField = DataFields(name=name, datetype=datatype, predictValue=predict, modelId=userModel.id)
                        dataField.save()
                    except IntegrityError:
                        message = {
                            'text': 'Названия столбцов не должны повторяться',
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'color': '#ef0000',
                            'modelId': userModel.id
                        }
                        messages[f'message{len(messages)}'] = message
                        print(messages)
                        return JsonResponse(
                            {'success': False, 'messages': messages})
                message = {
                    'text': 'Данные стобцов добавлены в базу данных',
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#33ff33',
                    'modelId': userModel.id
                }
                messages[f'message{len(messages)}'] = message
            except Exception as e:
                message = {
                    'text': e,
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#ef0000'
                }
                messages[f'message{len(messages)}'] = message
                if os.path.isfile(path):
                    os.remove(path)
                if userModel:
                    userModel.delete()
                return JsonResponse({'success': False, 'messages': messages})


            return JsonResponse({'success': True, 'messages': messages, 'modelId': userModel.id})


        else:
            message = {
                'text': 'Данные не загружены на сервер',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#ef0000'
            }
            messages[f'message{len(messages)}'] = message
            return JsonResponse({'success': False, 'messages': messages})


def createModel(request):
    if request.method == 'POST':
        modelId = request.POST['modelId']
        print(modelId)
        return JsonResponse({'success': True})
