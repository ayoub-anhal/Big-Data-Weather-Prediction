
import requests
from datetime import datetime, timedelta
import csv
import subprocess
import os
import pandas as pd


def Data_actuel():
    try:
        # Replace with your API key (if applicable)
        API_KEY = "4edc9281ea0d683c6caf71c7fdfdb7fa"

        # Define the list of cities and country code
        cities = ["Casablanca", "Tétouan", "Ouarzazate", "Ifrane", "Laayoune"]
        country_code = "MA"

        # Initialize an empty DataFrame to store weather data
        columns = ["City", "Timestamp", "Temperature (°C)", "Humidity (%)", "Winds (m/s)", "Clouds (%)", "rain_1h (mm)", "Description"]
        weather_data = pd.DataFrame(columns=columns)

        # Function to retrieve current weather data for a city
        def get_weather_data(city):
            try:
                # API endpoint for current weather data
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={API_KEY}"
                response = requests.get(url)
                data = response.json()

                # Extract relevant weather information
                temperature_kelvin = data["main"]["temp"]
                temperature_celsius = temperature_kelvin - 273.15
                humidity = data["main"]["humidity"]
                winds = data["wind"]["speed"]
                clouds = data["clouds"]["all"]
                rain = data["rain"]["1h"] if "rain" in data and "1h" in data["rain"] else 0
                description = data["weather"][0]["description"] if "weather" in data and len(data["weather"]) > 0 else ""

                # Get the current timestamp
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Append data to the DataFrame
                weather_data.loc[len(weather_data)] = [city, current_time, temperature_celsius, humidity, winds, clouds, rain, description]

            except Exception as e:
                print(f"Error fetching weather data for {city}: {e}")

        for city in cities:
            get_weather_data(city)

        if os.path.exists("weather_actuel.csv"):
            # Supprimer le fichier existant
            os.remove("weather_actuel.csv")

        # Enregistrer le DataFrame dans un fichier CSV
        weather_data.to_csv("weather_actuel.csv", index=False)

        # Define the command to transfer the CSV file to HDFS
        command = ["hdfs", "dfs", "-put", "-f", "weather_actuel.csv", "/user/hdfs/weather_actuel.csv"]

        subprocess.run(command, shell=True)

    except Exception as e:
        print(f"An error occurred: {e}")


from pyspark.sql.functions import col
from pyspark.sql import SparkSession

def Read_actuel():
    
    file_path="hdfs://localhost:9000/user/hdfs/weather_actuel.csv"
    # Create a SparkSession
    spark = SparkSession.builder \
        .appName("Read CSV") \
        .getOrCreate()

    # Read the CSV file into a DataFrame
    df = spark.read.format("csv") \
        .option("header", "true") \
        .load(file_path)
    
    # Convert Temperature (°C) to integer
    df = df.withColumn("Temperature (°C)", col("Temperature (°C)").cast("int"))
    
    # Normalize Humidity and Clouds columns
    df = df.withColumn("Humidity", col("Humidity (%)") / 100).drop("Humidity (%)")
    df = df.withColumn("Clouds", col("Clouds (%)") / 100).drop("Clouds (%)")
    
    # Convert winds (m/s) and rain_1h (mm) to appropriate types
    df = df.withColumn("winds (m/s)", col("winds (m/s)").cast("float"))
    df = df.withColumn("rain_1h (mm)", col("rain_1h (mm)").cast("float"))
    
    return df



from pyspark.sql import DataFrame

def filter_actuel(df, city_name):
    return df.filter(df.City == city_name)



from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegressionModel

def predict_actuel(data, city_name, model_path):
    # Filtrer les données pour la ville spécifiée
    df_city = filter_actuel(data, city_name)
    
    # Créer un assembleur de vecteur
    assembler = VectorAssembler(inputCols=["Clouds", "rain_1h (mm)", "Humidity", "winds (m/s)"], 
                                outputCol="features")
    
    # Transformer les données en utilisant l'assembleur
    df_city_features = assembler.transform(df_city)
    
    # Charger le modèle
    loaded_model = LinearRegressionModel.load(model_path)
    
    # Faire des prédictions
    predictions = loaded_model.transform(df_city_features)
    
    # Renommer la colonne de prédiction
    predictions = predictions.withColumnRenamed("prediction", "temperature_predict (°C)")
    
    return predictions




