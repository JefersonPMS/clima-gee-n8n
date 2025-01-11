import base64
from io import BytesIO
import ee
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from google.oauth2 import service_account
import os

# Use a variável de ambiente para obter o caminho do arquivo de credenciais
service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
credentials = service_account.Credentials.from_service_account_file(
    service_account_path,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
ee.Initialize(credentials)

app = FastAPI()

class Geometry(BaseModel):
    type: str
    coordinates: list

def create_buffer(lat, lon, buffer_distance_meters=500):
    """Cria um buffer em torno de uma latitude e longitude fornecidas."""
    point = ee.Geometry.Point([lon, lat])
    buffer = point.buffer(buffer_distance_meters)
    return buffer

@app.post("/climate_buffer")
async def get_climate_and_altitude(lat: float, lon: float):
    # Cria um buffer de 500m em torno das coordenadas de entrada
    buffer_geometry = create_buffer(lat, lon)

    # Calcula temperatura e precipitação dentro do buffer
    start_year = 1993
    end_year = 2022
    anosParaDiv = end_year - start_year
    months = ee.List.sequence(1, 12)

    def compute_monthly_stats(m):
        m = ee.Number(m)
        month_filter = ee.Filter.calendarRange(m, m, 'month')
        date_filter = ee.Filter.calendarRange(start_year, end_year, 'year')
        filtered_collection = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE') \
            .filter(month_filter) \
            .filter(date_filter)
        mean_image = filtered_collection.mean()
        sum_image = filtered_collection.sum()
        temp_max = mean_image.select('tmmx').multiply(0.1)
        temp_min = mean_image.select('tmmn').multiply(0.1)
        precip = sum_image.select('pr').divide(anosParaDiv)
        stats = temp_max.addBands(temp_min).addBands(precip).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=buffer_geometry,
            scale=1000,
            bestEffort=True
        )
        return ee.Dictionary({
            'month': m,
            'tempMax': stats.get('tmmx'),
            'tempMin': stats.get('tmmn'),
            'prec': stats.get('pr')
        })

    # Calcula estatísticas mensais para temperatura e precipitação
    monthly_stats = months.map(compute_monthly_stats)
    stats_list = monthly_stats.getInfo()  # Recupera os dados como uma lista em Python

    # Prepara DataFrame para gráficos (se necessário)
    df = pd.DataFrame(stats_list)
    df['Month'] = df['month'].map({
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    })
    df['temp'] = (df['tempMax'] + df['tempMin']) / 2

    # Gera gráficos de temperatura e precipitação
    temperature_graph = generate_temperature_graph(df)
    precipitation_graph = generate_precipitation_graph(df)

    # Calcula altitude usando o DEM (SRTM)
    dem = ee.Image('USGS/SRTMGL1_003').clip(buffer_geometry)
    dem_stats = dem.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=buffer_geometry,
        scale=30,  # Usa uma resolução mais alta para dados de DEM  
        bestEffort=True
    ).getInfo()
    altitude_mean = dem_stats.get('elevation', 'No data')  # Obtém o valor médio de elevação  

    return {
        "climate_data": stats_list,
        "temperature_graph": temperature_graph,
        "precipitation_graph": precipitation_graph,
        "altitude_mean": altitude_mean
    }

def generate_temperature_graph(df):
    """Gera um gráfico de temperatura usando Matplotlib e codifica em base64."""
    plt.figure(figsize=(10, 5))
    plt.fill_between(df['Month'], df['tempMax'], df['temp'], color='#8a0d0d', alpha=0.3)
    plt.fill_between(df['Month'], df['temp'], df['tempMin'], color='#b9b3e7', alpha=0.2)
    plt.plot(df['Month'], df['tempMax'], label='Máxima', color='#8a0d0d')    
    plt.plot(df['Month'], df['temp'], label='Média', color='black', marker='o', linewidth=1, markersize=3)
    
    for i, txt in enumerate(df['temp']):
        plt.annotate(f'{round(txt, 2)}', (df['Month'][i], df['temp'][i]), textcoords="offset points", xytext=(0, 10), ha='center', color='black', fontsize=8)

    plt.xlabel(' ')
    plt.ylabel('Temperatura (°C)')
    plt.legend()
    plt.grid(True, color='lightgrey', linestyle='-', linewidth=0.3)
    ax = plt.gca()
    ax.tick_params(axis='both', which='both', length=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_precipitation_graph(df):
    """Gera um gráfico de precipitação usando Matplotlib e codifica em base64."""
    plt.figure(figsize=(10, 5))
    plt.bar(df['Month'], df['prec'], label='Média', color='#1f77b4', zorder=2)
    for i, txt in enumerate(df['prec']):
        plt.annotate(f'{round(txt, 2)}', (df['Month'][i], df['prec'][i]), textcoords="offset points", xytext=(0, 5), ha='center', color='black', fontsize=8)

    plt.xlabel('')
    plt.ylabel('Precipitação (mm)')
    plt.grid(True, color='lightgrey', linestyle='-', linewidth=0.3)
    ax = plt.gca()
    ax.tick_params(axis='both', which='both', length=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return base64.b64encode(buf.getvalue()).decode('utf-8')
