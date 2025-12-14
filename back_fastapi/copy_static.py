"""
Скрипт для копирования статических файлов из Django проекта
"""
import shutil
import os
from pathlib import Path

# Определяем пути
current_dir = Path(__file__).parent
back_dir = current_dir.parent / "back"
staticfiles_source = back_dir / "staticfiles"
staticfiles_dest = current_dir / "staticfiles"

if staticfiles_source.exists():
    if staticfiles_dest.exists():
        print(f"Папка {staticfiles_dest} уже существует. Удаляем старую версию...")
        shutil.rmtree(staticfiles_dest)
    
    print(f"Копируем статические файлы из {staticfiles_source} в {staticfiles_dest}...")
    shutil.copytree(staticfiles_source, staticfiles_dest)
    print("Статические файлы успешно скопированы!")
else:
    print(f"Папка {staticfiles_source} не найдена. Убедитесь, что путь правильный.")

