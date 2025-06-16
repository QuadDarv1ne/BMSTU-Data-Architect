
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import matplotlib.pyplot as plt

# Загрузка данных
students = pd.read_csv('Students.csv')
grades = pd.read_csv('Grades.csv')
attendance = pd.read_csv('Attendance.csv')

# Признак: средний балл студента
grades_agg = grades.groupby('student_id')['grade'].mean().reset_index().rename(columns={'grade': 'avg_grade'})
# Признак: доля двоек и троек
grades['is_low'] = grades['grade'] <= 3.0
low_grades = grades.groupby('student_id')['is_low'].mean().reset_index().rename(columns={'is_low': 'low_grade_share'})
# Признак: средняя посещаемость (доля пропусков)
attendance['is_absent'] = attendance['status'].isin(['отсутствовал', 'уважительная_причина'])
attendance_agg = attendance.groupby('student_id')['is_absent'].mean().reset_index().rename(columns={'is_absent': 'absent_share'})
# Объединяем признаки
df = students.merge(grades_agg, on='student_id', how='left')              .merge(low_grades, on='student_id', how='left')              .merge(attendance_agg, on='student_id', how='left')
df['target'] = (df['status'] == 'отчислен').astype(int)
df['avg_grade'] = df['avg_grade'].fillna(df['avg_grade'].mean())
df['low_grade_share'] = df['low_grade_share'].fillna(0)
df['absent_share'] = df['absent_share'].fillna(0)
features = ['avg_grade', 'low_grade_share', 'absent_share']
X = df[features]
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
print(classification_report(y_test, y_pred))
print('ROC-AUC:', roc_auc_score(y_test, y_proba))
importances = model.feature_importances_
plt.barh(features, importances)
plt.xlabel('Важность признака')
plt.title('Feature Importances')
plt.show()
