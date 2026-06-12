import logging

# Настройка базового логгера
logging.basicConfig(
    level=logging.DEBUG, # Логируем всё: от DEBUG до CRITICAL
    format="%(asctime)s [%(levelname)s] %(name)s %(message)s", # Формат записи
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"), # Запись в файл
        logging.StreamHandler() # Вывод в терминал (консоль)
    ],
    force=True
)
def get_logger(name):
    return logging.getLogger(name)

def get_base_url():
    return os.getenv('BASE_URL')