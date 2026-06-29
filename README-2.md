# Health Data Analyzer – Diabetes EDA

A Python-based exploratory data analysis project on the Pima Indians Diabetes Dataset (UCI ML Repository).

## Overview

This project analyzes health records of 768 patients to identify patterns and risk factors associated with diabetes using Python data analysis libraries.

## Dataset

- **Source:** [Pima Indians Diabetes Database – Kaggle](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
- **Records:** 768 patients
- **Features:** Glucose, BMI, Age, Blood Pressure, Insulin, etc.
- **Target:** Outcome (1 = Diabetic, 0 = Non-Diabetic)

## Features

- Data cleaning (handling missing/zero values using median imputation)
- Exploratory Data Analysis (EDA) with statistics
- Visualizations: Pie chart, Scatter plot, Heatmap, Histogram
- Key insights on diabetes risk factors

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Download diabetes.csv from Kaggle link above and place in same folder

# Run the script
python diabetes_analysis.py
```

## Key Findings

- Diabetic patients have significantly higher average glucose levels (~141) vs non-diabetic (~110)
- Higher BMI is observed in diabetic patients
- Glucose level has the highest correlation with diabetes outcome

## Output Charts

- `outcome_distribution.png` – Pie chart of diabetic vs non-diabetic patients
- `age_vs_glucose.png` – Scatter plot of Age vs Glucose by outcome
- `correlation_heatmap.png` – Feature correlation heatmap
- `bmi_distribution.png` – BMI distribution comparison
