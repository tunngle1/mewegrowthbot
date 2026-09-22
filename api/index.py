import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
ADMIN_CHAT_FILE = '../admin_chat_id.json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_admin_chat_id() -> str:
    """Загрузка chat_id администратора из переменной окружения или файла"""
    # Сначала проверяем переменную окружения
    if ADMIN_CHAT_ID:
        return ADMIN_CHAT_ID
    
    # Если нет переменной, пробуем файл
    try:
        if os.path.exists(ADMIN_CHAT_FILE):
            with open(ADMIN_CHAT_FILE, 'r') as f:
                data = json.load(f)
                return data.get('chat_id')
    except Exception as e:
        logger.error(f"Ошибка при загрузке chat_id из файла: {e}")
    return None

def send_telegram_message(text: str, chat_id: str = None) -> bool:
    """Отправка сообщения через Telegram API"""
    target_chat_id = chat_id or load_admin_chat_id()
    
    if not target_chat_id:
        logger.error("Не установлен CHAT_ID для отправки сообщений")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"Сообщение успешно отправлено в чат {target_chat_id}")
            return True
        else:
            logger.error(f"Ошибка Telegram API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}")
        return False

@app.route('/test', methods=['GET'])
def test():
    """Тестовый endpoint"""
    return jsonify({"status": "test working"}), 200

@app.route('/', methods=['GET'])
def root():
    """Корневой endpoint"""
    return jsonify({"status": "MeWeGo Bot API", "endpoints": ["/test", "/lead", "/xray"]}), 200

@app.route('/lead', methods=['POST', 'OPTIONS'])
def handle_lead():
    """Обработка заявки с формы сайта"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Expected JSON data"}), 400
        
        data = request.json
        logger.info(f"Получена заявка: {data}")
        
        # Валидация обязательных полей
        if not data.get('name'):
            return jsonify({"status": "error", "message": "Поле 'name' обязательно"}), 400
        if not data.get('what'):
            return jsonify({"status": "error", "message": "Поле 'what' обязательно"}), 400
        if not data.get('contact'):
            return jsonify({"status": "error", "message": "Поле 'contact' обязательно"}), 400
        
        message = f"""
📝 <b>НОВАЯ ЗАЯВКА С САЙТА</b>

👤 <b>Имя:</b> {data.get('name', 'Не указано')}
🏢 <b>Компания:</b> {data.get('company', 'Не указано')}
📊 <b>Оборот:</b> {data.get('turnover', 'Не указано')}
👥 <b>Размер команды:</b> {data.get('team', 'Не указано')}
📈 <b>Выручка:</b> {data.get('revenue', 'Не указано')}
💬 <b>Контакт:</b> {data.get('contact', 'Не указано')} ({data.get('contact_type', 'Не указано')})
🌐 <b>Сайт:</b> {data.get('site', 'Не указано')}

📝 <b>Что происходит:</b>
{data.get('what', 'Не указано')}

🎯 <b>Ситуация:</b> {data.get('problem', 'Не выбрана')}

⏰ <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        success = send_telegram_message(message)
        
        if success:
            return jsonify({"status": "success", "message": "Заявка отправлена"}), 200
        else:
            return jsonify({"status": "error", "message": "Ошибка при отправке в Telegram - бот не добавлен в чат"}), 500
            
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
    except Exception as e:
        logger.error(f"Ошибка при обработке заявки: {e}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

@app.route('/xray', methods=['POST', 'OPTIONS'])
def handle_xray():
    """Обработка результатов Business X-Ray"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.json
        logger.info(f"Получен X-Ray результат: {data}")
        
        message = f"""
🔍 <b>РЕЗУЛЬТАТ BUSINESS X-RAY</b>

👤 <b>Имя:</b> {data.get('name', 'Не указано')}
🏢 <b>Компания:</b> {data.get('company', 'Не указано')}

📊 <b>Результаты опроса:</b>
{data.get('results', 'Нет результатов')}

⏰ <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        success = send_telegram_message(message)
        
        if success:
            return jsonify({"status": "success", "message": "Результаты отправлены"}), 200
        else:
            return jsonify({"status": "error", "message": "Ошибка при отправке - бот не добавлен в чат"}), 500
            
    except Exception as e:
        logger.error(f"Ошибка при обработке X-Ray: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500