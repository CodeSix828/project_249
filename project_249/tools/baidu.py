import requests
import base64
import json
from pathlib import Path
from ..config.settings import settings


def get_access_token(api_key: str, secret_key: str) -> dict:
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}'
    try:
        response = requests.get(host, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                return {"success": True, "token": data['access_token']}
            else:
                return {"success": False, "error": f"获取Token失败: {data.get('error_description', '未知错误')}"}
        else:
            return {"success": False, "error": f"Token请求失败，HTTP状态码: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Token请求异常: {str(e)}"}


def recognize_image(image_path: str, access_token: str) -> dict:
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
    
    try:
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        return {"error": f"图片文件不存在: {image_path}"}
    except Exception as e:
        return {"error": f"读取图片失败: {str(e)}"}
    
    params = {"image": img_data, "top_num": 5}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        final_url = f"{request_url}?access_token={access_token}"
        response = requests.post(final_url, data=params, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"图像识别API调用失败，HTTP状态码: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"图像识别请求异常: {str(e)}"}


def image_recognition(image_path: str) -> dict:
    api_key = settings.BAIDU_API_KE
    secret_key = settings.BAIDU_SECRET_KEY
    
    if not api_key or not secret_key:
        return {
            "error": "图像识别工具未配置",
            "message": "缺少百度API密钥（BAIDU_API_KE 或 BAIDU_SECRET_KEY），请在 .env 文件中配置后使用"
        }
    
    token_result = get_access_token(api_key, secret_key)
    if not token_result["success"]:
        return {"error": token_result["error"]}
    
    result = recognize_image(image_path, token_result["token"])
    
    if "error" in result:
        return result
    
    if 'result' in result:
        formatted_result = {
            "success": True,
            "results": [
                {
                    "keyword": item['keyword'],
                    "score": round(item['score'], 4)
                }
                for item in result['result']
            ]
        }
        return formatted_result
    else:
        return {"error": "未识别到内容", "raw_response": result}


def main():
    image_path = "F:/ml/cats_vs_dogs/PetImages/Cat/100.jpg"
    result = image_recognition(image_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
