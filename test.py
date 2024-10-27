import subprocess
import os
import ctypes

# Проверяем, запущен ли скрипт с правами администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Запускаем процесс с правами администратора
def run_as_admin(script_path):
    # Команда для запуска PowerShell в режиме администратора
    subprocess.run(['powershell', '-Command', f'Start-Process python "{script_path}" -Verb runAs'])

# Основная функция
def main():
    if not is_admin():
        # Если не администратор, перезапускаем с правами администратора
        run_as_admin(os.path.abspath(__file__))
        return

    # Ваш код здесь
    print("Запущено с правами администратора")

if __name__ == "__main__":
    main()
    i = 0
    while True:
        print(f"test {i}")
        i += 1
