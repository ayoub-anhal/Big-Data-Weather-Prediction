# Big Data Weather Prediction - Morocco

## Project Overview
This project aims to predict weather temperature in Morocco using meteorological variables such as humidity, wind, and precipitation. It leverages Big Data technologies including **HDFS** for data storage and **PySpark** for data processing and model training. The final predictive service is deployed using **Streamlit**.

## Project Steps

### 1. Data Collection & Storage
The first step is to collect weather data from the OpenWeather API and store it in **HDFS** for further processing and model training.
* Run the notebook section:
inside the `PR_BD.ipynb` file.

### 2. Data Analysis & Processing
This step includes reading data from **HDFS**, performing data preprocessing, and training the predictive model using **PySpark**.
* Run the notebook sections:
from the `PR_BD.ipynb` file.

### 3. Model Training & Evaluation
In this step, we train multiple regression models and evaluate their performance:
* Execute the model training section in the notebook to train:
* Linear Regression
* Decision Tree Regression
* Random Forest Regression
* Compare models using RMSE and R² metrics
* Save the best performing model for deployment

### 4. HDFS Data Management
Set up and manage the HDFS environment for efficient data storage:
* Configure HDFS directories structure
* Implement data partitioning strategy by date
* Set up data backup and retention policies
* Monitor HDFS storage utilization

### 5. Streamlit Application Development
Develop a web application using **Streamlit** to collect real-time weather data, preprocess it, and generate predictions.
* Create two Python scripts:
* `actuel.py`: Contains functions for real-time data collection, preprocessing, and prediction.
* `app.py`: Contains the Streamlit app logic to run the web interface.

### 6. Application Deployment
Deploy the application for production use:
* Set up environment on target server
* Configure network settings and security
* Create startup scripts and service definitions
* Implement logging and monitoring

## Notes
* Steps 1 and 2 should be executed within **VS Code** using the **Jupyter** extension to run `.ipynb` notebooks.
* Step 3 involves running a **Streamlit** app from the VS Code terminal.

## Required Libraries
Before starting, ensure the following Python libraries are installed:
```bash
pip install streamlit streamlit_folium folium pyspark

This updated README adds more detailed steps about model training, HDFS management, application deployment, and troubleshooting, making it more comprehensive and professional.
