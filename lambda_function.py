import json
import requests
import boto3
import os
from datetime import datetime
import pytz

s3 = boto3.client('s3')


def get_weather():
    api_key = os.environ['API_KEY']
    location = '43.0333,141.4167'  # 札幌市南郷通20丁目の緯度と経度
    url = f'https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&lang=ja'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(f"Response Text: {response.text}")
        return None

def generate_html(weather_data, timestamp):
    weather = weather_data['current']
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            h1 {{
                color: #333;
            }}
            p {{
                color: #555;
            }}
            @media (max-width: 600px) {{
                body {{
                    padding: 10px;
                }}
                h1 {{
                    font-size: 1.5em;
                }}
                p {{
                    font-size: 1em;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>南郷通20丁目の[{timestamp} 現在]の天気（30分ごとに更新） </h1>
        <p>Temperature: {weather['temp_c']}°C</p>
        <p>Condition: {weather['condition']['text']}</p>
        <p>Humidity: {weather['humidity']}%</p>
        <p>Wind: {weather['wind_kph']} kph</p>
    </body>
    </html>
    """
    return html_content


def lambda_handler(event, context):
    weather_data = get_weather()

    if weather_data is None:
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to retrieve weather data')
        }

    jst = pytz.timezone('Asia/Tokyo')
    timestamp = datetime.now(jst).strftime('%Y-%m-%d_%H-%M-%S')

    html_content = generate_html(weather_data, timestamp)
    file_name = f'weather_now.html'

    # S3バケットにHTMLファイルをアップロード
    s3.put_object(
        Bucket=os.environ['S3_BUCKET'],
        Key=file_name,
        Body=html_content,
        ContentType='text/html'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Weather HTML file uploaded successfully!')
    }
