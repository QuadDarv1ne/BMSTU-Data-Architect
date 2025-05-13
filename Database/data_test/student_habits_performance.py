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

# Просмотр первых строк
print(df.head())

# Проверка на пропуски
print(df.isnull().sum())

# Основные статистики
print(df.describe())

# Визуализация корреляции между сном и GPA
sns.scatterplot(data=df, x='Sleep Hours', y='GPA')
plt.title("Влияние сна на успеваемость")
plt.show()

# Сравнение среднего GPA у студентов с разной физической активностью
sns.boxplot(data=df, x='Physical Activity', y='GPA')
plt.title("Физическая активность и успеваемость")
plt.show()

# Корреляционная матрица
corr_matrix = df.corr(numeric_only=True)
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title("Корреляция между привычками и успеваемостью")
plt.show()
