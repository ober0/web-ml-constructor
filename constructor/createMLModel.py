import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')  # Использование бэкенда Agg
import matplotlib.pyplot as plt
from django.conf import settings
import os
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor


class RegressionModel:
    def __init__(self, datasetPath, find, columns, graphisPath):
        self.path = datasetPath
        self.find = find
        self.num_col = columns.keys()
        self.num_col_without_find = [i for i in self.num_col if i != self.find]
        self.nameroot = graphisPath
        self.df = self.read()
        self.label_encoders = self.labelEncode(columns)

    def read(self):
        df = pd.read_csv(self.path)
        df.drop_duplicates(inplace=True)

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col].fillna(df[col].mode()[0], inplace=True)
            elif df[col].dtype in ['float64', 'int64']:
                df[col].fillna(df[col].mean(), inplace=True)

        return df

    def labelEncode(self, columns):
        label_encoders = {}
        names = [name for name, datatype in columns.items() if datatype == 'object']

        for name in names:
            le = LabelEncoder()
            self.df[name] = le.fit_transform(self.df[name].fillna("unknown"))
            label_encoders[name] = le

        return label_encoders

    def learn(self):
        X = self.df[self.num_col].drop(self.find, axis=1)
        print(f"Целевая переменная: {self.find}")
        y = self.df[self.find]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Обучение модели
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.7)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
        plt.xlabel(f'Истинные значения {self.find}')
        plt.ylabel(f'Предсказанные значения {self.find}')
        plt.title('Истинные vs Предсказанные значения')

        # Убедитесь, что директория для графиков существует
        if not os.path.exists(settings.GRAPHICS_ROOT_DIR):
            os.makedirs(settings.GRAPHICS_ROOT_DIR)

        plt.savefig(os.path.join(settings.GRAPHICS_ROOT_DIR, self.nameroot))
        plt.close()

        mse = mean_squared_error(y_test, y_pred)
        return mse


class LinearRegressionModel(RegressionModel):
    def __init__(self, datasetPath, find, columns, graphisPath):
        super().__init__(datasetPath, find, columns, graphisPath)
        self.model = LinearRegression(fit_intercept=True)
        self.mse = self.learn()


class RandomForestModel(RegressionModel):
    def __init__(self, datasetPath, find, columns, graphisPath):
        super().__init__(datasetPath, find, columns, graphisPath)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.mse = self.learn()

class GradientBoosterModel(RegressionModel):
    def __init__(self, datasetPath, find, columns, graphisPath):
        super().__init__(datasetPath, find, columns, graphisPath)
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.mse = self.learn()

class SvrModel(RegressionModel):
    def __init__(self, datasetPath, find, columns, graphisPath):
        super().__init__(datasetPath, find, columns, graphisPath)
        self.model = SVR(kernel='rbf', C=100, epsilon=0.1)
        self.mse = self.learn()

class DecisionTreeModel(RegressionModel):
    def __init__(self, datasetPath, find, columns, graphisPath):
        super().__init__(datasetPath, find, columns, graphisPath)
        self.model = DecisionTreeRegressor(random_state=42)
        self.mse = self.learn()

