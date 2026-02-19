"""
Скрипт для загрузки датасета Old Tatar с Roboflow
"""
import os
from roboflow import Roboflow
from dotenv import load_dotenv, dotenv_values

def download_dataset(api_key=None, workspace="lab-ovmmc", project="old-tatar-new", version=2):
    """
    Загружает датасет Old Tatar с Roboflow
    
    Args:
        api_key: API ключ Roboflow (можно получить на https://roboflow.com)
        workspace: Имя рабочего пространства на Roboflow
        project: Имя проекта
        version: Версия датасета
    """
    print("Инициализация Roboflow...")
    
    # Если API ключ не указан, попробуем получить из переменной окружения
    if api_key is None:
        api_key = os.getenv("ROBOFLOW_API_KEY")
        if api_key is None:
            print("ВНИМАНИЕ: API ключ не найден!")
            print("Пожалуйста, установите переменную окружения ROBOFLOW_API_KEY")
            print("или передайте api_key в функцию download_dataset()")
            print("\nДля получения API ключа:")
            print("1. Зарегистрируйтесь на https://roboflow.com")
            print("2. Перейдите в Settings -> API")
            print("3. Скопируйте ваш API ключ")
            return None
    
    try:
        rf = Roboflow(api_key=api_key)
        project_obj = rf.workspace(workspace).project(project)
        dataset = project_obj.version(version).download("yolov8")
        
        print(f"\nДатасет успешно загружен в: {dataset.location}")
        print(f"Путь к данным: {os.path.join(dataset.location, 'data.yaml')}")
        
        return dataset
    except Exception as e:
        print(f"Ошибка при загрузке датасета: {e}")
        return None

if __name__ == "__main__":
    # loading variables from .env file
    load_dotenv()
    # Можно указать API ключ напрямую здесь или использовать переменную окружения
    # download_dataset(api_key="your_api_key_here")
    download_dataset()

