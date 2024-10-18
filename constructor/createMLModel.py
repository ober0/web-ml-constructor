import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')  # Использование бэкенда Agg
import matplotlib.pyplot as plt
from django.conf import settings
import os


class LinearRegreesionModel:
    def __init__(self, datasetPath, find, columns, graphisPath):
        self.path = datasetPath
        self.find = find
        self.num_col = columns.keys()
        self.num_col_without_find = [i for i in self.num_col if i != self.find]
        self.nameroot = graphisPath
        self.df = self.read()

        self.le = self.labelEncode(columns)

        self.mse, self.model = self.learn()

    def read(self):
        print(self.path)
        df = pd.read_csv(self.path)
        print(df)
        df.drop_duplicates(inplace=True)

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col].fillna(df[col].mode()[0], inplace=True)
            elif df[col].dtype == 'float64':
                df[col].fillna(df[col].mean().round(3), inplace=True)
            elif df[col].dtype == 'int64':
                df[col].fillna(df[col].mean().round(0), inplace=True)

        return df

    def labelEncode(self, columns):
        le = LabelEncoder()
        for name, datatype in columns.items():
            if datatype == 'object':
                self.df[name] = le.fit_transform(self.df[name])
        return le

    def learn(self):
        X = self.df[self.num_col].drop(self.find, axis=1)
        y = self.df[self.find]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression(fit_intercept=True)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.7)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
        plt.xlabel(f'Истинные значения {self.find}')
        plt.ylabel(f'Предсказанные значения {self.find}')
        plt.title('Истинные vs Предсказанные значения')
        plt.savefig(os.path.join(settings.GRAPHICS_ROOT_DIR, self.nameroot))
        plt.close()

        mse = mean_squared_error(y_test, y_pred)
        return mse, model
