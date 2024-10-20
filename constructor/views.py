import json
import os
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import UserModels, DataFields
from django.db import IntegrityError
import pandas as pd
from .createMLModel import LinearRegreesionModel
import pickle


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
                            'text': str(e),
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'color': '#ef0000'
                        }
                        messages[f'message{len(messages)}'] = message
                        return JsonResponse({'success': False, 'messages': messages})





            df = pd.read_csv(path)
            columns = [i for i in df.columns]
            columns_with_types = {col: str(df[col].dtype) for col in df.columns}
            formatted_columns = {col: dtype for col, dtype in columns_with_types.items()}


            data = [{'name': 'Age', 'datatype': 'int64', 'predict': 'False'}, {'name': 'Gender', 'datatype': 'object', 'predict': 'False'}, {'name': 'Weight (kg)', 'datatype': 'float64', 'predict': 'False'}, {'name': 'Height (m)', 'datatype': 'float64', 'predict': 'False'}, {'name': 'Max_BPM', 'datatype': 'int64', 'predict':
'False'}, {'name': 'Avg_BPM', 'datatype': 'int64', 'predict': 'False'}, {'name': 'Resting_BPM', 'datatype': 'int64', 'predict': 'False'}, {'name': 'Session_Duration (hours)', 'datatype': 'float64', 'predict': 'False'}, {'name': 'Calories_Burned', 'datatype': 'float64', 'predict': 'False'}, {'name': 'Workout_Type', 'datatype': 'object', 'predict': 'False'}, {'name': 'Fat_Percentage', 'datatype': 'float64', 'predict': 'False'}, {'name': 'Water_Intake (liters)', 'datatype': 'float64', 'predict': 'False'}, {'name': 'Workout_Frequency (days/week)', 'datatype': 'int64', 'predict': 'False'}, {'name': 'Experience_Level', 'datatype': 'int64', 'predict': 'False'}, {'name': 'BMI', 'datatype': 'float64', 'predict': 'True'}]


            if len(data) == len(columns):
                for i in data:

                    if i['name'] not in columns:
                        message = {
                            'text': f'Поле {i["name"]} нет в датафрейме',
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'color': '#ef0000'
                        }
                        messages[f'message{len(messages)}'] = message
                        if os.path.isfile(path):
                            os.remove(path)
                        return JsonResponse({'success': False, 'messages': messages})

                    if i['datatype'] != formatted_columns.get(i['name'], None):
                        message = {
                            'text': f'Поле {i["name"]} имеет неправильный тип данных (ожидался: {formatted_columns.get(i["name"])}, получен: {i["datatype"]})',
                            'time': datetime.now().strftime('%H:%M:%S'),
                            'color': '#ef0000'
                        }
                        messages[f'message{len(messages)}'] = message
                        if os.path.isfile(path):
                            os.remove(path)
                        return JsonResponse({'success': False, 'messages': messages})
                message = {
                    'text': f'Все поля успешно проверены и совпали с полями в датасете',
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#33ff33'
                }
                messages[f'message{len(messages)}'] = message
            else:
                message = {
                    'text': f'Количество столбцов не одинаковое',
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#ef0000'
                }
                messages[f'message{len(messages)}'] = message
                if os.path.isfile(path):
                    os.remove(path)
                return JsonResponse({'success': False, 'messages': messages})







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
                    'text': str(e),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'color': '#ef0000'
                }
                messages[f'message{len(messages)}'] = message
                return JsonResponse({'success': False, 'messages': messages})

            try:
                for el in data:
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
                    'text': str(e),
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
        messages = {}
        modelId = request.POST['modelId']
        print(1)
        try:
            userModelCfg = UserModels.objects.get(id=modelId)
            datasetPath = os.path.join(settings.DATASET_ROOT_DIR, userModelCfg.DatasetPath)

            filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}-{userModelCfg.name}'

            graphisPath = os.path.join(settings.GRAPHICS_ROOT_DIR, filename)
            userModelCfg.GraphisPath = filename + '.png'

            userModelCfg.ModelPath = filename + '.pkl'
            modelPath = filename + '.pkl'

            columns = {}
            userModelColumns = DataFields.objects.filter(modelId=modelId).all()

            find = ''

            for el in userModelColumns:
                columns[el.name] = el.datetype
                if el.predictValue == 'True':
                    find = el.name
                    print('find: ', el.name)
            message = {
                'text': 'Данные для модели успешно обработаны',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#33ff33'
            }
            messages[f'message{len(messages)}'] = message
        except Exception as e:
            message = {
                'text': str(e),
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#ef0000'
            }
            messages[f'message{len(messages)}'] = message
            return JsonResponse({'success': False, 'messages': messages})
        print(2)
        if find == '':
            message = {
                'text': 'Нет значения для поиска',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#ef0000'
            }
            messages[f'message{len(messages)}'] = message
            print('error3')
            return JsonResponse({'success': False, 'messages': messages})
        print(3)
        try:
            regressionModel = LinearRegreesionModel(datasetPath, find, columns, graphisPath)
            mse = regressionModel.mse
            model = regressionModel.model
            userModelCfg.mse = mse

            message = {
                'text': 'Модель успешно создана',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#33ff33'
            }
            messages[f'message{len(messages)}'] = message
        except Exception as e:
            message = {
                'text': f'Ошибка создания модели: {str(e)}',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#ef0000'
            }
            messages[f'message{len(messages)}'] = message
            return JsonResponse({'success': False, 'messages': messages})
        print(4)
        try:
            print(os.path.join(settings.MODELS_ROOT_DIR, modelPath))
            with open(os.path.join(settings.MODELS_ROOT_DIR, modelPath), 'wb') as f:
                pickle.dump(model, f)
            message = {
                'text': f'Модель успешно сохранена',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#33ff33'
            }
            messages[f'message{len(messages)}'] = message
        except Exception as e:
            message = {
                'text': f'Ошибка сохранения модели: {str(e)}',
                'time': datetime.now().strftime('%H:%M:%S'),
                'color': '#ef0000'
            }
            messages[f'message{len(messages)}'] = message
            print(f"Error saving model: {e}")
            return JsonResponse({'success': False, 'messages': messages})
        userModelCfg.save()
        message = {
            'text': f'mse: {mse}',
            'time': datetime.now().strftime('%H:%M:%S'),
            'color': '#33ff33'
        }
        messages[f'message{len(messages)}'] = message
        return JsonResponse({'success': True, 'messages': messages, 'graphicsPath': filename})