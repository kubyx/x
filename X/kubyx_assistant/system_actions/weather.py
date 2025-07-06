import requests

def get_weather(city="Istanbul"):
    api_key = "SENIN_API_ANAHTARIN"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=tr&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get("main"):
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{city} için hava durumu: {desc}, sıcaklık: {temp}°C"
    return "Hava durumu alınamadı."
