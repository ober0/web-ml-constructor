import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import pickle
import os
import pandas as pd
from constructor.models import UserModels, DataFields  # Corrected import
from sklearn.preprocessing import LabelEncoder

def predict_api(request, pk):
    model_id = pk
    model = UserModels.objects.get(id=model_id)
    model_path = os.path.join(settings.MODELS_ROOT_DIR, model.ModelPath)
    le_path = os.path.join(settings.LE_ROOT_DIR, model.LEPath)

    field_names = [df_field.name for df_field in DataFields.objects.filter(modelId=model_id)]



    data = {field: request.GET.get(field) for field in field_names}

    with open(le_path, 'rb') as f:
        label_encoders = pickle.load(f)

    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        num_cols = model.feature_names_in_
        df = pd.DataFrame([data])[num_cols]

        for col in df.columns:
            try:
                df[col][0] = float(df[col][0])
            except ValueError:
                le = label_encoders[col]
                df[col] = le.transform(df[col])


        prediction = model.predict(df)

    return JsonResponse({'predict': float(prediction[0])}, status=200)


def request_predict(request, pk):
    if request.method == "GET":
        fields_db = DataFields.objects.filter(modelId=pk).all()
        model = UserModels.objects.get(id=pk)
        model_name = model.name

        fields = {}
        find = None
        for field in fields_db:
            le_fields = None
            if field.predictValue == 'False':
                if field.datetype.lower() == 'object' and model.LEPath:
                    lePath = os.path.join(settings.LE_ROOT_DIR, model.LEPath)

                    if os.path.exists(lePath) and os.path.getsize(lePath) > 0:
                        try:
                            with open(lePath, 'rb') as f:
                                label_encoders = pickle.load(f)
                                le = label_encoders.get(field.name)
                                if le:
                                    le_fields = list(le.classes_)
                        except (EOFError, pickle.UnpicklingError):
                            return JsonResponse({"error": "Ошибка загрузки данных: файл поврежден или пуст"},
                                                status=400)

                fields[field.name] = {
                    'datetype': field.datetype,
                    'le_fields': le_fields
                }
            else:
                find = field.name

        return render(request, 'view/index.html', {'fields': fields, 'model_name': model_name, 'find': find, 'model_type': model.model_type})

    elif request.method == "POST":
        data = dict(request.POST)
        del data['csrfmiddlewaretoken']

        url = f'{settings.HOST_NAME}/view/api/predict/model/{pk}/?'
        for key, value in data.items():
            url += f'{key}={value[0]}&'

        response = requests.get(url)
        print(response.status_code)
        print(url)
        data = response.json()
        predict = data['predict']
        return render(request, 'view/result.html', {'predict': predict})

@staff_member_required
def remove_model(request, pk):
    model = UserModels.objects.get(id=pk)
    fields = DataFields.objects.filter(modelId=pk).all()
    for field in fields:
        field.delete()
    datasetPath = model.DatasetPath
    graphisPath = model.GraphisPath
    modelPath = model.ModelPath
    lePath = model.LEPath

    try:
        os.remove(os.path.join(settings.DATASET_ROOT_DIR, datasetPath))
        os.remove(os.path.join(settings.GRAPHICS_ROOT_DIR, graphisPath))
        os.remove(os.path.join(settings.MODELS_ROOT_DIR, modelPath))
        os.remove(os.path.join(settings.LE_ROOT_DIR, lePath))
    except Exception as e:
        return JsonResponse({'success':False, 'error': e})

    model.delete()

    return JsonResponse({'success': True})

#http://127.0.0.1:8000/view/api/predict/model/1?Age=56&Gender=0&Weight%20(kg)=88.3&Height%20(m)=1.71&Max_BPM=180&Resting_BPM=157&Session_Duration%20(hours)=1.69&Calories_Burned=1313.0&Workout_Type=0&Fat_Percentage=12.6&Water_Intake%20(liters)=3.5&Workout_Frequency%20(days/week)=4&Experience_Level=3&Avg_BPM=120
