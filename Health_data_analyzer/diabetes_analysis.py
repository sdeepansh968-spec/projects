# Health Data Analysis - Diabetes Dataset
# Dataset: Pima Indians Diabetes Database (UCI ML Repository)
# Source: https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ------- Load Dataset -------

df = pd.read_csv('diabetes.csv')

print("Dataset loaded!")
print("Total records:", df.shape[0])
print("Total features:", df.shape[1])
print()
print(df.head())

# ------- Basic Info -------

print("\n--- Dataset Info ---")
print(df.info())

print("\n--- Basic Statistics ---")
print(df.describe().round(2))

# ------- Data Cleaning -------

# 0 values in these columns don't make medical sense
# e.g. glucose = 0 or BMI = 0 is not possible, so treating them as missing
missing_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

print("\nZero values (treated as missing):")
for col in missing_cols:
    zeros = (df[col] == 0).sum()
    print(f"  {col}: {zeros}")

# replacing 0 with NaN so we can fill properly
df[missing_cols] = df[missing_cols].replace(0, np.nan)

# median is better than mean for medical data since it handles outliers well
for col in missing_cols:
    df[col] = df[col].fillna(df[col].median())

print("\nNull values after cleaning:")
print(df.isnull().sum())

# ------- Outcome Distribution -------

print("\nDiabetes Outcome Count:")
print(df['Outcome'].value_counts())
print(f"\nDiabetic patients: {int(df['Outcome'].sum())} out of {len(df)}")

# ------- Visualization -------

# 1. Outcome pie chart
plt.figure(figsize=(6, 5))
df['Outcome'].value_counts().plot(
    kind='pie',
    labels=['No Diabetes', 'Diabetes'],
    autopct='%1.1f%%',
    colors=['#66b3ff', '#ff9999'],
    startangle=90
)
plt.title('Diabetes Distribution in Dataset')
plt.ylabel('')
plt.tight_layout()
plt.savefig('outcome_distribution.png', dpi=100)
plt.show()
print("Chart saved: outcome_distribution.png")

# 2. Age vs Glucose scatter
plt.figure(figsize=(7, 5))
for outcome, group in df.groupby('Outcome'):
    label = 'Diabetic' if outcome == 1 else 'Non-Diabetic'
    color = 'red' if outcome == 1 else 'steelblue'
    plt.scatter(group['Age'], group['Glucose'], label=label, alpha=0.5, color=color, s=30)

plt.xlabel('Age')
plt.ylabel('Glucose Level')
plt.title('Age vs Glucose Level')
plt.legend()
plt.tight_layout()
plt.savefig('age_vs_glucose.png', dpi=100)
plt.show()
print("Chart saved: age_vs_glucose.png")

# 3. Correlation Heatmap
plt.figure(figsize=(9, 7))
sns.heatmap(df.corr(numeric_only=True), annot=True, fmt='.2f', cmap='coolwarm', linewidths=0.5)
plt.title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=100)
plt.show()
print("Chart saved: correlation_heatmap.png")

# 4. BMI Distribution
plt.figure(figsize=(7, 5))
df[df['Outcome'] == 0]['BMI'].plot(kind='hist', bins=20, alpha=0.6, label='No Diabetes', color='steelblue')
df[df['Outcome'] == 1]['BMI'].plot(kind='hist', bins=20, alpha=0.6, label='Diabetes', color='red')
plt.xlabel('BMI')
plt.ylabel('Number of Patients')
plt.title('BMI Distribution: Diabetic vs Non-Diabetic')
plt.legend()
plt.tight_layout()
plt.savefig('bmi_distribution.png', dpi=100)
plt.show()
print("Chart saved: bmi_distribution.png")

# ------- Key Insights -------

print("\n====== KEY INSIGHTS ======")

diabetic = df[df['Outcome'] == 1]
non_diabetic = df[df['Outcome'] == 0]

print(f"\nAverage Glucose  -> Diabetic: {diabetic['Glucose'].mean():.1f}  |  Non-Diabetic: {non_diabetic['Glucose'].mean():.1f}")
print(f"Average BMI      -> Diabetic: {diabetic['BMI'].mean():.1f}  |  Non-Diabetic: {non_diabetic['BMI'].mean():.1f}")
print(f"Average Age      -> Diabetic: {diabetic['Age'].mean():.1f}  |  Non-Diabetic: {non_diabetic['Age'].mean():.1f}")

# see which features are most linked to diabetes
corr = df.corr(numeric_only=True)['Outcome'].drop('Outcome').sort_values(ascending=False)
print("\nTop features correlated with Diabetes:")
print(corr.head(3))

print("\n--- Analysis Complete ---")
