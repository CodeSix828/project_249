import requests
from ..config.settings import settings


def weather_query(location):
    api_key = settings.GAODE_TIANQI_API_KEY
    if not api_key:
        return {
            "error": "天气查询工具未配置",
            "message": "缺少高德天气API密钥（GAODE_TIANQI_API_KEY），请在 .env 文件中配置后使用"
        }
    
    try:
        base_url = "https://restapi.amap.com/v3/weather/weatherInfo?parameters"
        params = {
            "key": api_key,
            "city": location
        }
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"无法获取到天气信息，HTTP状态码: {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "天气查询请求超时，请稍后重试"}
    except requests.exceptions.RequestException as e:
        return {"error": f"天气查询失败: {str(e)}"}
