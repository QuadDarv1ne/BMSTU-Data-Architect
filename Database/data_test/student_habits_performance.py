"""
TG: @quadd4rv1n7
Преподаватель: Дуплей Максим Игоревич
Дата: 13.05.2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных
df = pd.read_csv("student_habits_performance.csv")

# Проверка имён колонок 
print("Список колонок:", df.columns.tolist())  # Убедимся, какие названия на самом деле есть

# Визуализация корреляции между сном и оценками
sns.scatterplot(data=df, x='sleep_hours', y='exam_score')  # Исправлено на sleep_hours и exam_score
plt.title("Влияние сна на успеваемость")
plt.show()

# Сравнение среднего балла у студентов с разной физической активностью
sns.boxplot(data=df, x='exercise_frequency', y='exam_score')  # Исправлено на exercise_frequency
plt.title("Физическая активность и успеваемость")
plt.show()

# Корреляционная матрица (только числовые колонки)
corr_matrix = df.select_dtypes(include=['number']).corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Корреляция между привычками и успеваемостью")
plt.show()
