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
    model_id = pk
    model_db = UserModels.objects.get(id=model_id)

    path = os.path.join(settings.MODELS_ROOT_DIR, model_db.ModelPath)

    with open(path, 'rb') as f:
        model = pickle.load(f)
        num_cols = model.feature_names_in_

    return JsonResponse({})




#http://127.0.0.1:8000/constructor/api/predict/model/1?Age=56&Gender=0&Weight%20(kg)=88.3&Height%20(m)=1.71&Max_BPM=180&Resting_BPM=157&Session_Duration%20(hours)=1.69&Calories_Burned=1313.0&Workout_Type=0&Fat_Percentage=12.6&Water_Intake%20(liters)=3.5&Workout_Frequency%20(days/week)=4&Experience_Level=3&Avg_BPM=120