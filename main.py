import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot çalışıyor"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive sunucusu başlatıldı.")

BOT_START_TIME = datetime.now()

# ================== ÇOKLU DİL DESTEĞİ ==================
USER_LANG = {}

TRANSLATIONS = {
    'tr': {
        'welcome': "Hoş geldin, {name}!",
        'your_id': "Kullanıcı ID'n",
        'username': "Kullanıcı Adın",
        'your_status': "Durumun",
        'files_uploaded': "Yüklenen Dosyalar",
        'upload_file': "Dosya Yükle",
        'check_files': "Dosyaları Kontrol Et",
        'bot_speed': "Bot Hızı",
        'statistics': "İstatistikler",
        'updates_channel': "Güncelleme Kanalı",
        'contact_owner': "Sahibe Ulaş",
        'uptime': "Çalışma Süresi",
        'admin_panel': "Admin Paneli",
        'broadcast': "Duyuru",
        'subscriptions': "Abonelikler",
        'lock_bot': "Botu Kilitle",
        'unlock_bot': "Botun Kilidini Aç",
        'run_all': "Tüm Kodları Çalıştır",
        'ai': "MPX AI",
        'bot_locked': "Bot admin tarafından kilitlendi. Daha sonra tekrar deneyin.",
        'file_limit_reached': "Dosya limitine ulaşıldı ({current}/{limit}). Önce dosya silin.",
        'send_file': "Python (.py) veya ZIP (.zip) dosyanı gönder.",
        'unsupported_type': "Desteklenmeyen tür! Sadece .py ve .zip izin verilir.",
        'file_too_large': "Dosya çok büyük (Maks: 20 MB).",
        'no_files': "Dosyaların:\n\n(Henüz dosya yüklenmedi)",
        'your_files': "Dosyaların:\nYönetmek için tıkla.",
        'admin_required': "Admin yetkisi gerekli.",
        'owner_required': "Sahip yetkisi gerekli.",
        'permission_denied': "Bu dosyayı yönetme iznin yok.",
        'file_not_found': "Dosya bulunamadı.",
        'running': "Çalışıyor",
        'stopped': "Durdu",
        'start': "Başlat",
        'stop': "Durdur",
        'restart': "Yeniden Başlat",
        'delete': "Sil",
        'logs': "Loglar",
        'view_logs': "Logları Gör",
        'back_to_files': "Dosyalara Dön",
        'back_to_main': "Ana Menüye Dön",
        'starting': "Başlatılıyor",
        'stopping': "Durduruluyor",
        'deleting': "Siliniyor",
        'restarting': "Yeniden başlatılıyor",
        'broadcast_prompt': "Tüm aktif kullanıcılara gönderilecek mesajı yaz.\nİptal için /cancel",
        'broadcast_confirm': "Duyuruyu Onayla",
        'broadcast_sent': "Duyuru gönderildi!",
        'broadcast_cancelled': "Duyuru iptal edildi.",
        'bot_locked_msg': "Bot kilitlendi.",
        'bot_unlocked_msg': "Botun kilidi açıldı.",
        'pending_approval': "⏳ Dosyan admin onayı bekliyor...\nOnaylandığında otomatik başlatılacak.",
        'approved': "✅ Admin tarafından onaylandı! Bot başlatılıyor...",
        'rejected': "❌ Admin tarafından reddedildi! Dosya silindi.",
        'approve': "✅ Onayla",
        'reject': "❌ Reddet",
        'new_file_approval': "🔔 YENİ DOSYA ONAYI",
        'file_approved_admin': "✅ Dosya onaylandı ve başlatıldı.",
        'file_rejected_admin': "❌ Dosya reddedildi ve silindi.",
        'already_processed': "Bu dosya zaten işlendi.",
        'approval_expired': "Bu onay isteği süresi doldu.",
        'no_pending': "Bekleyen onay yok.",
        'admin_pending_list': "📋 Bekleyen Onaylar:",
        'waiting_approval_short': "Onay Bekliyor",
    },
    'en': {
        'welcome': "Welcome, {name}!",
        'your_id': "Your User ID",
        'username': "Username",
        'your_status': "Your Status",
        'files_uploaded': "Files Uploaded",
        'upload_file': "Upload File",
        'check_files': "Check Files",
        'bot_speed': "Bot Speed",
        'statistics': "Statistics",
        'updates_channel': "Updates Channel",
        'contact_owner': "Contact Owner",
        'uptime': "Uptime",
        'admin_panel': "Admin Panel",
        'broadcast': "Broadcast",
        'subscriptions': "Subscriptions",
        'lock_bot': "Lock Bot",
        'unlock_bot': "Unlock Bot",
        'run_all': "Run All Code",
        'ai': "MPX AI",
        'bot_locked': "Bot locked by admin. Try later.",
        'file_limit_reached': "File limit reached ({current}/{limit}). Delete files first.",
        'send_file': "Send your Python (.py) or ZIP (.zip) file.",
        'unsupported_type': "Unsupported type! Only .py and .zip allowed.",
        'file_too_large': "File too large (Max: 20 MB).",
        'no_files': "Your files:\n\n(No files uploaded yet)",
        'your_files': "Your files:\nClick to manage.",
        'admin_required': "Admin permissions required.",
        'owner_required': "Owner permissions required.",
        'permission_denied': "You can only manage your own files.",
        'file_not_found': "File not found.",
        'running': "Running",
        'stopped': "Stopped",
        'start': "Start",
        'stop': "Stop",
        'restart': "Restart",
        'delete': "Delete",
        'logs': "Logs",
        'view_logs': "View Logs",
        'back_to_files': "Back to Files",
        'back_to_main': "Back to Main",
        'starting': "Starting",
        'stopping': "Stopping",
        'deleting': "Deleting",
        'restarting': "Restarting",
        'broadcast_prompt': "Send message to broadcast to all active users.\n/cancel to abort.",
        'broadcast_confirm': "Confirm & Send",
        'broadcast_sent': "Broadcast sent!",
        'broadcast_cancelled': "Broadcast cancelled.",
        'bot_locked_msg': "Bot locked.",
        'bot_unlocked_msg': "Bot unlocked.",
        'pending_approval': "⏳ Your file is awaiting admin approval...\nWill auto-start once approved.",
        'approved': "✅ Approved by admin! Starting bot...",
        'rejected': "❌ Rejected by admin! File deleted.",
        'approve': "✅ Approve",
        'reject': "❌ Reject",
        'new_file_approval': "🔔 NEW FILE APPROVAL",
        'file_approved_admin': "✅ File approved and started.",
        'file_rejected_admin': "❌ File rejected and deleted.",
        'already_processed': "This file was already processed.",
        'approval_expired': "This approval request expired.",
        'no_pending': "No pending approvals.",
        'admin_pending_list': "📋 Pending Approvals:",
        'waiting_approval_short': "Awaiting Approval",
    },
    'ru': {
        'welcome': "Добро пожаловать, {name}!",
        'your_id': "Ваш ID",
        'username': "Имя пользователя",
        'your_status': "Ваш статус",
        'files_uploaded': "Загружено файлов",
        'upload_file': "Загрузить файл",
        'check_files': "Проверить файлы",
        'bot_speed': "Скорость бота",
        'statistics': "Статистика",
        'updates_channel': "Канал обновлений",
        'contact_owner': "Связаться с владельцем",
        'uptime': "Время работы",
        'admin_panel': "Админ-панель",
        'broadcast': "Рассылка",
        'subscriptions': "Подписки",
        'lock_bot': "Заблокировать",
        'unlock_bot': "Разблокировать",
        'run_all': "Запустить всё",
        'ai': "MPX AI",
        'bot_locked': "Бот заблокирован админом.",
        'file_limit_reached': "Достигнут лимит ({current}/{limit}).",
        'send_file': "Отправьте файл .py или .zip.",
        'unsupported_type': "Неподдерживаемый тип!",
        'file_too_large': "Файл слишком большой (макс. 20 МБ).",
        'no_files': "Ваши файлы:\n\n(пусто)",
        'your_files': "Ваши файлы:",
        'admin_required': "Требуются права админа.",
        'owner_required': "Требуются права владельца.",
        'permission_denied': "Нет прав.",
        'file_not_found': "Файл не найден.",
        'running': "Работает",
        'stopped': "Остановлен",
        'start': "Запустить",
        'stop': "Остановить",
        'restart': "Перезапустить",
        'delete': "Удалить",
        'logs': "Логи",
        'view_logs': "Просмотр логов",
        'back_to_files': "К файлам",
        'back_to_main': "В главное меню",
        'starting': "Запуск",
        'stopping': "Остановка",
        'deleting': "Удаление",
        'restarting': "Перезапуск",
        'broadcast_prompt': "Отправьте сообщение для рассылки.",
        'broadcast_confirm': "Подтвердить",
        'broadcast_sent': "Рассылка отправлена!",
        'broadcast_cancelled': "Рассылка отменена.",
        'bot_locked_msg': "Бот заблокирован.",
        'bot_unlocked_msg': "Бот разблокирован.",
        'pending_approval': "⏳ Ожидает одобрения админа...",
        'approved': "✅ Одобрено!",
        'rejected': "❌ Отклонено!",
        'approve': "✅ Одобрить",
        'reject': "❌ Отклонить",
        'new_file_approval': "🔔 НОВЫЙ ФАЙЛ",
        'file_approved_admin': "✅ Одобрено и запущено.",
        'file_rejected_admin': "❌ Отклонено и удалено.",
        'already_processed': "Уже обработано.",
        'approval_expired': "Запрос истёк.",
        'no_pending': "Нет ожидающих.",
        'admin_pending_list': "📋 Ожидающие:",
        'waiting_approval_short': "Ожидает",
    },
    'ar': {
        'welcome': "أهلاً، {name}!",
        'your_id': "معرفك",
        'username': "اسم المستخدم",
        'your_status': "حالتك",
        'files_uploaded': "الملفات المرفوعة",
        'upload_file': "رفع ملف",
        'check_files': "فحص الملفات",
        'bot_speed': "سرعة البوت",
        'statistics': "الإحصائيات",
        'updates_channel': "قناة التحديثات",
        'contact_owner': "اتصل بالمالك",
        'uptime': "مدة التشغيل",
        'admin_panel': "لوحة الإدارة",
        'broadcast': "إذاعة",
        'subscriptions': "الاشتراكات",
        'lock_bot': "قفل البوت",
        'unlock_bot': "فتح البوت",
        'run_all': "تشغيل الكل",
        'ai': "MPX AI",
        'bot_locked': "البوت مقفل بواسطة الإدارة.",
        'file_limit_reached': "تم الوصول للحد ({current}/{limit}).",
        'send_file': "أرسل ملف .py أو .zip.",
        'unsupported_type': "نوع غير مدعوم!",
        'file_too_large': "الملف كبير جدًا (20 ميجا).",
        'no_files': "ملفاتك:\n\n(لا يوجد)",
        'your_files': "ملفاتك:",
        'admin_required': "صلاحيات الإدارة مطلوبة.",
        'owner_required': "صلاحيات المالك مطلوبة.",
        'permission_denied': "لا تملك صلاحية.",
        'file_not_found': "الملف غير موجود.",
        'running': "قيد التشغيل",
        'stopped': "متوقف",
        'start': "تشغيل",
        'stop': "إيقاف",
        'restart': "إعادة",
        'delete': "حذف",
        'logs': "السجلات",
        'view_logs': "عرض السجلات",
        'back_to_files': "رجوع للملفات",
        'back_to_main': "القائمة الرئيسية",
        'starting': "جاري التشغيل",
        'stopping': "جاري الإيقاف",
        'deleting': "جاري الحذف",
        'restarting': "جاري الإعادة",
        'broadcast_prompt': "أرسل الرسالة للإذاعة.",
        'broadcast_confirm': "تأكيد",
        'broadcast_sent': "تم إرسال الإذاعة!",
        'broadcast_cancelled': "تم الإلغاء.",
        'bot_locked_msg': "تم قفل البوت.",
        'bot_unlocked_msg': "تم فتح البوت.",
        'pending_approval': "⏳ بانتظار موافقة الإدارة...",
        'approved': "✅ تمت الموافقة!",
        'rejected': "❌ مرفوض!",
        'approve': "✅ موافقة",
        'reject': "❌ رفض",
        'new_file_approval': "🔔 ملف جديد",
        'file_approved_admin': "✅ تمت الموافقة والتشغيل.",
        'file_rejected_admin': "❌ مرفوض ومحذوف.",
        'already_processed': "تمت المعالجة.",
        'approval_expired': "انتهت الصلاحية.",
        'no_pending': "لا يوجد معلق.",
        'admin_pending_list': "📋 المعلقة:",
        'waiting_approval_short': "بالانتظار",
    },
    'hi': {
        'welcome': "स्वागत है, {name}!",
        'your_id': "आपकी ID",
        'username': "उपयोगकर्ता नाम",
        'your_status': "आपकी स्थिति",
        'files_uploaded': "अपलोड की गई फ़ाइलें",
        'upload_file': "फ़ाइल अपलोड करें",
        'check_files': "फ़ाइलें जाँचें",
        'bot_speed': "बॉट गति",
        'statistics': "आंकड़े",
        'updates_channel': "अपडेट चैनल",
        'contact_owner': "मालिक से संपर्क",
        'uptime': "अपटाइम",
        'admin_panel': "एडमिन पैनल",
        'broadcast': "ब्रॉडकास्ट",
        'subscriptions': "सदस्यताएँ",
        'lock_bot': "बॉट लॉक",
        'unlock_bot': "अनलॉक",
        'run_all': "सभी चलाएँ",
        'ai': "MPX AI",
        'bot_locked': "बॉट एडमिन द्वारा लॉक।",
        'file_limit_reached': "सीमा पूरी ({current}/{limit})।",
        'send_file': "अपनी .py या .zip फ़ाइल भेजें।",
        'unsupported_type': "असमर्थित प्रकार!",
        'file_too_large': "फ़ाइल बहुत बड़ी (20 MB)।",
        'no_files': "आपकी फ़ाइलें:\n\n(कोई नहीं)",
        'your_files': "आपकी फ़ाइलें:",
        'admin_required': "एडमिन अनुमति चाहिए।",
        'owner_required': "मालिक अनुमति चाहिए।",
        'permission_denied': "अनुमति नहीं।",
        'file_not_found': "फ़ाइल नहीं मिली।",
        'running': "चल रहा",
        'stopped': "रुका",
        'start': "चालू",
        'stop': "रोकें",
        'restart': "पुनः आरंभ",
        'delete': "हटाएँ",
        'logs': "लॉग",
        'view_logs': "लॉग देखें",
        'back_to_files': "फ़ाइलों पर वापस",
        'back_to_main': "मुख्य मेनू",
        'starting': "चालू हो रहा",
        'stopping': "रुक रहा",
        'deleting': "हटा रहे",
        'restarting': "पुनः आरंभ",
        'broadcast_prompt': "ब्रॉडकास्ट संदेश भेजें।",
        'broadcast_confirm': "पुष्टि करें",
        'broadcast_sent': "ब्रॉडकास्ट भेजा!",
        'broadcast_cancelled': "रद्द किया।",
        'bot_locked_msg': "बॉट लॉक हुआ।",
        'bot_unlocked_msg': "बॉट अनलॉक हुआ।",
        'pending_approval': "⏳ एडमिन अनुमोदन की प्रतीक्षा...",
        'approved': "✅ अनुमोदित!",
        'rejected': "❌ अस्वीकृत!",
        'approve': "✅ अनुमोदन",
        'reject': "❌ अस्वीकार",
        'new_file_approval': "🔔 नई फ़ाइल",
        'file_approved_admin': "✅ अनुमोदित और चालू।",
        'file_rejected_admin': "❌ अस्वीकृत और हटाया।",
        'already_processed': "पहले ही संसाधित।",
        'approval_expired': "समय समाप्त।",
        'no_pending': "कोई लंबित नहीं।",
        'admin_pending_list': "📋 लंबित:",
        'waiting_approval_short': "प्रतीक्षारत",
    }
}

def t(user_id, key, **kwargs):
    lang = USER_LANG.get(user_id, 'tr')
    text = TRANSLATIONS.get(lang, TRANSLATIONS['tr']).get(key, TRANSLATIONS['tr'].get(key, key))
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        return text

# ================== AYARLAR ==================
TOKEN = os.environ.get('BOT_TOKEN', '8713603435:AAHSgug0Xwx4NOj47HX8UF6MzPxaFU3Mrnw')
OWNER_ID = int(os.environ.get('OWNER_ID', '8818660111'))
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8818660111'))
YOUR_USERNAME = os.environ.get('YOUR_USERNAME', '@ibenler')
UPDATE_CHANNEL = 'https://t.me/freebotHostingServer'
FORCED_CHANNEL = 'https://t.me/freebotHostingServer'
FORCED_CHANNEL_USERNAME = 'freebotHostingServer'
SUPPORT_USERNAME = '@ibenler'

A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

FREE_USER_LIMIT = 6
SUBSCRIBED_USER_LIMIT = 23
ADMIN_LIMIT =99
OWNER_LIMIT = float('inf')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False

# Onay bekleyen dosyalar
pending_approvals = {}  # {approval_id: {info}}
approval_counter = [0]
approvals_lock = threading.Lock()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================== VERİTABANI ==================
def init_db():
    logger.info(f"Veritabanı başlatılıyor: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_langs
                     (user_id INTEGER PRIMARY KEY, lang TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pending_approvals
                     (approval_id INTEGER PRIMARY KEY, user_id INTEGER,
                      file_name TEXT, file_type TEXT, message_id INTEGER, created_at TEXT)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("Veritabanı başarıyla başlatıldı.")
    except Exception as e:
        logger.error(f"Veritabanı başlatma hatası: {e}", exc_info=True)

def load_data():
    logger.info("Veritabanından veriler yükleniyor...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"Geçersiz tarih: {user_id}: {expiry}")

        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id, lang FROM user_langs')
        for uid, lang in c.fetchall():
            USER_LANG[uid] = lang

        conn.close()
        logger.info(f"Veriler yüklendi: {len(active_users)} kullanıcı, {len(user_subscriptions)} abonelik, {len(admin_ids)} admin.")
    except Exception as e:
        logger.error(f"Veri yükleme hatası: {e}", exc_info=True)

init_db()
load_data()

# ================== YARDIMCI FONKSİYONLAR ==================
def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                logger.warning(f"{script_key} zombi. Temizleniyor.")
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try: script_info['log_file'].close()
                    except Exception as log_e: logger.error(f"Log kapatma hatası: {log_e}")
                if script_key in bot_scripts: del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try: script_info['log_file'].close()
                except Exception: pass
            if script_key in bot_scripts: del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"Durum kontrol hatası {script_key}: {e}", exc_info=True)
            return False
    return False

def kill_process_tree(process_info):
    pid = None
    script_key = process_info.get('script_key', 'N/A')
    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try: process_info['log_file'].close()
            except Exception as log_e: logger.error(f"Log kapatma: {log_e}")

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            if pid:
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try: child.terminate()
                        except psutil.NoSuchProcess: pass
                        except Exception:
                            try: child.kill()
                            except Exception: pass
                    gone, alive = psutil.wait_procs(children, timeout=1)
                    for p in alive:
                        try: p.kill()
                        except Exception: pass
                    try:
                        parent.terminate()
                        try: parent.wait(timeout=1)
                        except psutil.TimeoutExpired: parent.kill()
                    except psutil.NoSuchProcess: pass
                    except Exception:
                        try: parent.kill()
                        except Exception: pass
                except psutil.NoSuchProcess: pass
    except Exception as e:
        logger.error(f"Process ağacı öldürme hatası {pid}: {e}", exc_info=True)

# ================== BOT TOKEN ÇIKARMA VE İMZALAMA ==================
def extract_bot_tokens(file_path):
    """Verilen .py dosyasından telegram bot token'larını çıkarır."""
    tokens = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        pattern = r'\b(\d{8,12}:[A-Za-z0-9_-]{35})\b'
        matches = re.findall(pattern, content)
        tokens = list(set(matches))
        if tokens:
            logger.info(f"{file_path} içinde {len(tokens)} token bulundu.")
    except Exception as e:
        logger.error(f"Token çıkarma hatası {file_path}: {e}")
    return tokens

def enforce_bot_signature(token):
    """Botun adını ve bio'sunu güncelle: zorunlu kanal + destek."""
    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json()
        if not resp.get('ok'):
            logger.warning(f"Token geçersiz: {token[:15]}...")
            return False

        bot_username = resp['result'].get('username', 'Bot')
        new_name = f"{bot_username} | FREEBOTHOSTİNGSERVER"

        # İsmi güncelle
        try:
            requests.post(f"https://api.telegram.org/bot{token}/setMyName",
                          data={'name': new_name[:64]}, timeout=10)
        except Exception as e:
            logger.error(f"setMyName hatası: {e}")

        # Bio
        description = (
            f"🚀 Bu bot FREEBOTHOSTİNGSERVER tarafından barındırılıyor.\n"
            f"📢 Kanal: {FORCED_CHANNEL}\n"
            f"💬 Destek: {SUPPORT_USERNAME}"
        )
        try:
            requests.post(f"https://api.telegram.org/bot{token}/setMyDescription",
                          data={'description': description[:512]}, timeout=10)
            requests.post(f"https://api.telegram.org/bot{token}/setMyShortDescription",
                          data={'short_description': f"freebotHostingServer Hosting | {SUPPORT_USERNAME}"[:120]}, timeout=10)
        except Exception as e:
            logger.error(f"setMyDescription hatası: {e}")

        # Bot komutlarını güncelle (opsiyonel)
        try:
            commands = json.dumps([
                {"command": "start", "description": "Başlat"},
                {"command": "help", "description": "Yardım"},
            ])
            requests.post(f"https://api.telegram.org/bot{token}/setMyCommands",
                          data={'commands': commands}, timeout=10)
        except Exception: pass

        logger.info(f"Bot imzası güncellendi: {bot_username}")
        return True
    except Exception as e:
        logger.error(f"enforce_bot_signature hatası: {e}", exc_info=True)
        return False

# ================== SCRIPT ÇALIŞTIRMA ==================
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI',
    'telegram': 'python-telegram-bot',
    'python_telegram_bot': 'python-telegram-bot',
    'aiogram': 'aiogram',
    'pyrogram': 'pyrogram',
    'telethon': 'telethon',
    'telethon.sync': 'telethon',
    'telepot': 'telepot',
    'tgcrypto': 'tgcrypto',
    'bs4': 'beautifulsoup4',
    'requests': 'requests',
    'pillow': 'Pillow',
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'dotenv': 'python-dotenv',
    'dateutil': 'python-dateutil',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'flask': 'Flask',
    'django': 'Django',
    'sqlalchemy': 'SQLAlchemy',
    'aiohttp': 'aiohttp',
    'httpx': 'httpx',
    'motor': 'motor',
    'pymongo': 'pymongo',
    'redis': 'redis',
    'psutil': 'psutil',
    'asyncio': None, 'json': None, 'datetime': None, 'os': None,
    'sys': None, 're': None, 'time': None, 'math': None, 'random': None,
    'logging': None, 'threading': None, 'subprocess': None, 'zipfile': None,
    'tempfile': None, 'shutil': None, 'sqlite3': None, 'atexit': None,
    'pathlib': None, 'typing': None, 'collections': None, 'functools': None,
    'itertools': None, 'traceback': None, 'signal': None, 'base64': None,
    'hashlib': None, 'uuid': None, 'csv': None, 'io': None, 'html': None,
    'urllib': None, 'socket': None, 'ssl': None, 'http': None, 'email': None,
}

def attempt_install_pip(module_name, message):
    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if package_name is None:
        return False
    try:
        bot.reply_to(message, f"📦 Modül `{module_name}` eksik. `{package_name}` yükleniyor...", parse_mode='Markdown')
        command = [sys.executable, '-m', 'pip', 'install', package_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False,
                                encoding='utf-8', errors='ignore', timeout=180)
        if result.returncode == 0:
            bot.reply_to(message, f"✅ Paket `{package_name}` yüklendi.", parse_mode='Markdown')
            return True
        else:
            error_msg = f"❌ `{package_name}` yüklenemedi.\n```\n{(result.stderr or result.stdout)[:500]}\n```"
            bot.reply_to(message, error_msg, parse_mode='Markdown')
            return False
    except subprocess.TimeoutExpired:
        bot.reply_to(message, f"⏱ `{package_name}` yüklemesi zaman aşımına uğradı.")
        return False
    except Exception as e:
        bot.reply_to(message, f"❌ Yükleme hatası `{package_name}`: {str(e)}")
        return False

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        try:
            bot.send_message(message_obj_for_reply.chat.id,
                           f"❌ '{file_name}' {max_attempts} denemede çalıştırılamadı. Logları kontrol et.")
        except Exception: pass
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Python script çalıştırma denemesi {attempt}: {script_path}")

    try:
        if not os.path.exists(script_path):
            try:
                bot.send_message(message_obj_for_reply.chat.id, f"❌ Hata: '{file_name}' bulunamadı!")
            except Exception: pass
            if script_owner_id in user_files:
                user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
            remove_user_file_db(script_owner_id, file_name)
            return

        if attempt == 1:
            check_command = [sys.executable, script_path]
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              text=True, encoding='utf-8', errors='ignore')
                stdout, stderr = check_proc.communicate(timeout=8)
                return_code = check_proc.returncode
                if return_code != 0 and stderr:
                    match_py = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if match_py:
                        module_name = match_py.group(1).strip().strip("'\"")
                        if module_name.startswith('.'):
                            error_summary = stderr[:500]
                            try:
                                bot.send_message(message_obj_for_reply.chat.id,
                                               f"❌ '{file_name}' içe aktarma hatası:\n```\n{error_summary}\n```",
                                               parse_mode='Markdown')
                            except Exception: pass
                            return
                        if attempt_install_pip(module_name, message_obj_for_reply):
                            try:
                                bot.send_message(message_obj_for_reply.chat.id,
                                               f"✅ Yükleme başarılı. '{file_name}' tekrar deneniyor...")
                            except Exception: pass
                            time.sleep(2)
                            threading.Thread(target=run_script,
                                             args=(script_path, script_owner_id, user_folder, file_name,
                                                   message_obj_for_reply, attempt + 1)).start()
                            return
                        else:
                            return
                    else:
                        error_summary = stderr[:500]
                        try:
                            bot.send_message(message_obj_for_reply.chat.id,
                                           f"❌ '{file_name}' ön kontrol hatası:\n```\n{error_summary}\n```",
                                           parse_mode='Markdown')
                        except Exception: pass
                        return
            except subprocess.TimeoutExpired:
                if check_proc and check_proc.poll() is None: check_proc.kill(); check_proc.communicate()
            except FileNotFoundError:
                try:
                    bot.send_message(message_obj_for_reply.chat.id,
                                   f"❌ Hata: Python yorumlayıcısı '{sys.executable}' bulunamadı.")
                except Exception: pass
                return
            except Exception as e:
                try:
                    bot.send_message(message_obj_for_reply.chat.id,
                                   f"❌ Ön kontrol hatası '{file_name}': {e}")
                except Exception: pass
                return
            finally:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill(); check_proc.communicate()

        # Uzun süreli çalıştırma
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None; process = None
        try:
            log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        except Exception as e:
            try:
                bot.send_message(message_obj_for_reply.chat.id, f"❌ Log dosyası açılamadı: {e}")
            except Exception: pass
            return
        try:
            startupinfo = None; creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # Ortam değişkenlerine zorunlu bilgileri ekle
            env_vars = os.environ.copy()
            env_vars['freebothostingserver_CHANNEL'] = FORCED_CHANNEL
            env_vars['freebothostingserver_SUPPORT'] = SUPPORT_USERNAME
            env_vars['freebothostingserver_HOST'] = 'freebothostingserver Hosting'

            process = subprocess.Popen(
                [sys.executable, script_path], cwd=user_folder,
                stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore', env=env_vars
            )
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id,
                'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder,
                'type': 'py', 'script_key': script_key
            }
            try:
                bot.send_message(message_obj_for_reply.chat.id,
                               f"✅ Python script '{file_name}' başlatıldı! (PID: {process.pid})")
            except Exception: pass

            # Token çıkarma + bot imzası zorlama
            try:
                tokens = extract_bot_tokens(script_path)
                for tk in tokens:
                    threading.Thread(target=enforce_bot_signature, args=(tk,), daemon=True).start()
            except Exception as e:
                logger.error(f"Token imzalama hatası: {e}")

        except FileNotFoundError:
            if log_file and not log_file.closed: log_file.close()
            try:
                bot.send_message(message_obj_for_reply.chat.id, f"❌ Hata: Python bulunamadı.")
            except Exception: pass
            if script_key in bot_scripts: del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed: log_file.close()
            try:
                bot.send_message(message_obj_for_reply.chat.id, f"❌ '{file_name}' başlatılamadı: {str(e)}")
            except Exception: pass
            if process and process.poll() is None:
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts: del bot_scripts[script_key]
    except Exception as e:
        try:
            bot.send_message(message_obj_for_reply.chat.id, f"❌ Beklenmedik hata '{file_name}': {str(e)}")
        except Exception: pass
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]

# ================== VERİTABANI İŞLEMLERİ ==================
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
        except Exception as e: logger.error(f"Dosya kaydetme hatası: {e}")
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
        except Exception as e: logger.error(f"Dosya silme hatası: {e}")
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
        except Exception as e: logger.error(f"Aktif kullanıcı hatası: {e}")
        finally: conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)',
                      (user_id, expiry.isoformat()))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
        except Exception as e: logger.error(f"Abonelik hatası: {e}")
        finally: conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions: del user_subscriptions[user_id]
        except Exception as e: logger.error(f"Abonelik silme hatası: {e}")
        finally: conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id)
        except Exception as e: logger.error(f"Admin ekleme hatası: {e}")
        finally: conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID: return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
            conn.commit()
            removed = c.rowcount > 0
            if removed: admin_ids.discard(admin_id)
            return removed
        except Exception as e:
            logger.error(f"Admin silme hatası: {e}")
            return False
        finally: conn.close()

def save_user_lang(user_id, lang):
    USER_LANG[user_id] = lang
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_langs (user_id, lang) VALUES (?, ?)', (user_id, lang))
            conn.commit()
        except Exception as e: logger.error(f"Dil kaydetme hatası: {e}")
        finally: conn.close()

# ================== MENÜLER ==================
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(t(user_id, 'updates_channel'), url=UPDATE_CHANNEL),
        types.InlineKeyboardButton(t(user_id, 'upload_file'), callback_data='upload'),
        types.InlineKeyboardButton(t(user_id, 'check_files'), callback_data='check_files'),
        types.InlineKeyboardButton(t(user_id, 'bot_speed'), callback_data='speed'),
        types.InlineKeyboardButton(t(user_id, 'statistics'), callback_data='stats'),
        types.InlineKeyboardButton(t(user_id, 'contact_owner'), url=f'https://t.me/{SUPPORT_USERNAME.replace("@", "")}'),
        types.InlineKeyboardButton(t(user_id, 'ai'), callback_data='mpx_ai'),
        types.InlineKeyboardButton(t(user_id, 'uptime'), callback_data='uptime'),
        types.InlineKeyboardButton("🌐 Dil / Language", callback_data='change_lang'),
    ]

    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton(t(user_id, 'subscriptions'), callback_data='subscription'),
            types.InlineKeyboardButton(t(user_id, 'broadcast'), callback_data='broadcast'),
            types.InlineKeyboardButton(t(user_id, 'lock_bot') if not bot_locked else t(user_id, 'unlock_bot'),
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton(t(user_id, 'admin_panel'), callback_data='admin_panel'),
            types.InlineKeyboardButton("🟢 " + t(user_id, 'run_all'), callback_data='run_all_scripts'),
            types.InlineKeyboardButton("📋 Bekleyen Onaylar", callback_data='pending_list'),
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(buttons[4], admin_buttons[1])
        markup.add(admin_buttons[2], admin_buttons[4])
        markup.add(admin_buttons[3], admin_buttons[5])
        markup.add(buttons[5], buttons[6])
        markup.add(buttons[7], buttons[8])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3])
        markup.add(buttons[4])
        markup.add(buttons[5], buttons[6])
        markup.add(buttons[7], buttons[8])

    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if user_id in admin_ids:
        rows = [
            [t(user_id, 'updates_channel'), t(user_id, 'check_files')],
            [t(user_id, 'upload_file'), t(user_id, 'statistics')],
            [t(user_id, 'bot_speed'), t(user_id, 'subscriptions')],
            [t(user_id, 'broadcast'), t(user_id, 'admin_panel')],
            [t(user_id, 'contact_owner'), t(user_id, 'uptime')],
        ]
    else:
        rows = [
            [t(user_id, 'updates_channel'), t(user_id, 'uptime')],
            [t(user_id, 'upload_file'), t(user_id, 'check_files')],
            [t(user_id, 'bot_speed'), t(user_id, 'statistics')],
            [t(user_id, 'contact_owner'), t(user_id, 'ai')],
        ]
    for row in rows:
        markup.add(*[types.KeyboardButton(text) for text in row])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True, requester_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    rid = requester_id or script_owner_id
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 " + t(rid, 'stop'), callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 " + t(rid, 'restart'), callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ " + t(rid, 'delete'), callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 " + t(rid, 'logs'), callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 " + t(rid, 'start'), callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ " + t(rid, 'delete'), callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 " + t(rid, 'view_logs'), callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(types.InlineKeyboardButton("🔙 " + t(rid, 'back_to_files'), callback_data='check_files'))
    return markup

def create_admin_panel(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Admin Ekle', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Admin Sil', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 Admin Listesi', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton('📋 Bekleyen Onaylar', callback_data='pending_list'))
    markup.row(types.InlineKeyboardButton('🔙 ' + t(user_id, 'back_to_main'), callback_data='back_to_main'))
    return markup

def create_subscription_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Abonelik Ekle', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Abonelik Sil', callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton('🔍 Abonelik Sorgula', callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton('🔙 ' + t(user_id, 'back_to_main'), callback_data='back_to_main'))
    return markup

def create_lang_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data='setlang_tr'),
        types.InlineKeyboardButton("🇬🇧 English", callback_data='setlang_en')
    )
    markup.row(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data='setlang_ru'),
        types.InlineKeyboardButton("🇸🇦 العربية", callback_data='setlang_ar')
    )
    markup.row(types.InlineKeyboardButton("🇮🇳 हिन्दी", callback_data='setlang_hi'))
    markup.row(types.InlineKeyboardButton("🔙 Geri", callback_data='back_to_main'))
    return markup

# ================== ADMIN ONAY SİSTEMİ ==================
def request_approval(user_id, file_path, file_name, file_type, message):
    """Python ve ZIP dosyaları için admin onayı ister."""
    with approvals_lock:
        approval_counter[0] += 1
        approval_id = approval_counter[0]
        pending_approvals[approval_id] = {
            'user_id': user_id,
            'file_path': file_path,
            'file_name': file_name,
            'file_type': file_type,
            'user_folder': os.path.dirname(file_path),
            'chat_id': message.chat.id,
            'created_at': datetime.now(),
            'message_id': message.message_id,
        }

    user_name = message.from_user.first_name
    user_username = message.from_user.username or "Yok"

    bot.reply_to(message, t(user_id, 'pending_approval'), parse_mode='Markdown')

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(t(OWNER_ID, 'approve') + f" #{approval_id}", callback_data=f'approve_{approval_id}'),
        types.InlineKeyboardButton(t(OWNER_ID, 'reject') + f" #{approval_id}", callback_data=f'reject_{approval_id}')
    )

    approval_text = (
        f"🔔 <b>{t(OWNER_ID, 'new_file_approval')}</b>\n\n"
        f"👤 Kullanıcı: <b>{user_name}</b>\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📛 Kullanıcı Adı: @{user_username}\n"
        f"📄 Dosya: <code>{file_name}</code>\n"
        f"📦 Tür: <b>{file_type.upper()}</b>\n"
        f"🔢 Onay ID: <b>#{approval_id}</b>\n\n"
        f"Onaylıyor musun?"
    )

    for admin_id in list(admin_ids):
        try:
            try:
                with open(file_path, 'rb') as f:
                    bot.send_document(admin_id, f, caption=approval_text,
                                      reply_markup=markup, parse_mode='HTML')
            except Exception:
                bot.send_message(admin_id, approval_text, reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Admin {admin_id} onay mesajı gönderilemedi: {e}")

def handle_approve(call):
    try:
        approval_id = int(call.data.split('_')[1])
    except (ValueError, IndexError):
        bot.answer_callback_query(call.id, "Geçersiz onay ID.", show_alert=True); return

    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'admin_required'), show_alert=True); return

    with approvals_lock:
        info = pending_approvals.get(approval_id)
        if not info:
            bot.answer_callback_query(call.id, t(call.from_user.id, 'already_processed'), show_alert=True)
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except Exception: pass
            return
        del pending_approvals[approval_id]

    bot.answer_callback_query(call.id, t(call.from_user.id, 'file_approved_admin'))
    user_id = info['user_id']
    file_path = info['file_path']
    file_name = info['file_name']
    file_type = info['file_type']
    user_folder = info['user_folder']
    user_chat_id = info['chat_id']

    # Buton temizle
    try:
        bot.edit_message_caption(
            caption=f"✅ <b>ONAYLANDI</b> - Dosya: <code>{file_name}</code>\nKullanıcı: <code>{user_id}</code>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML'
        )
    except Exception:
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except Exception: pass

    # Kullanıcıya bildir
    try:
        bot.send_message(user_chat_id, t(user_id, 'approved'))
    except Exception: pass

    # Script'i çalıştır
    class FakeMessage:
        def __init__(self, chat_id):
            self.chat = type('obj', (object,), {'id': chat_id})()
    fake = FakeMessage(user_chat_id)
    threading.Thread(target=run_script,
                     args=(file_path, user_id, user_folder, file_name, fake),
                     daemon=True).start()

def handle_reject(call):
    try:
        approval_id = int(call.data.split('_')[1])
    except (ValueError, IndexError):
        bot.answer_callback_query(call.id, "Geçersiz onay ID.", show_alert=True); return

    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'admin_required'), show_alert=True); return

    with approvals_lock:
        info = pending_approvals.get(approval_id)
        if not info:
            bot.answer_callback_query(call.id, t(call.from_user.id, 'already_processed'), show_alert=True)
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except Exception: pass
            return
        del pending_approvals[approval_id]

    bot.answer_callback_query(call.id, t(call.from_user.id, 'file_rejected_admin'))
    user_id = info['user_id']
    file_path = info['file_path']
    file_name = info['file_name']
    user_chat_id = info['chat_id']

    # Dosyayı diskten sil
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        # Klasörü de temizle (içi boşsa)
        parent_dir = os.path.dirname(file_path)
        if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
            shutil.rmtree(parent_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Red sonrası dosya silme hatası: {e}")
    remove_user_file_db(user_id, file_name)

    try:
        bot.edit_message_caption(
            caption=f"❌ <b>REDDEDİLDİ</b> - Dosya: <code>{file_name}</code>\nKullanıcı: <code>{user_id}</code>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML'
        )
    except Exception:
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except Exception: pass

    try:
        bot.send_message(user_chat_id, t(user_id, 'rejected'))
    except Exception: pass

# ================== ZIP İŞLEME ==================
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)

        # Güvenli çıkarma
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                if not member_path.startswith(os.path.abspath(temp_dir) + os.sep) and member_path != os.path.abspath(temp_dir):
                    raise zipfile.BadZipFile(f"Güvenli olmayan zip yolu: {member.filename}")
            zip_ref.extractall(temp_dir)

        extracted_items = os.listdir(temp_dir)
        py_files = [f for f in extracted_items if f.endswith('.py')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None

        if not py_files and not req_file:
            bot.reply_to(message, "❌ Arşivde `.py` dosyası bulunamadı!"); return

        # requirements.txt varsa yükle
        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            bot.reply_to(message, f"📦 `{req_file}` yükleniyor...")
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_path],
                                       capture_output=True, text=True, check=True,
                                       encoding='utf-8', errors='ignore', timeout=300)
                bot.reply_to(message, f"✅ `{req_file}` yüklendi.")
            except subprocess.TimeoutExpired:
                bot.reply_to(message, f"⏱ `{req_file}` yüklemesi zaman aşımına uğradı, devam ediliyor...")
            except Exception as e:
                bot.reply_to(message, f"⚠️ `{req_file}` kısmen yüklenemedi: {str(e)[:200]}")

        # Ana script'i seç
        main_script_name = None
        preferred_py = ['main.py', 'bot.py', 'app.py']
        for p in preferred_py:
            if p in py_files:
                main_script_name = p; break
        if not main_script_name and py_files:
            main_script_name = py_files[0]

        if not main_script_name:
            bot.reply_to(message, "❌ Ana script belirlenemedi!"); return

        # Temp'ten user_folder'a taşı
        for item_name in os.listdir(temp_dir):
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path)

        save_user_file(user_id, main_script_name, 'py')
        main_script_path = os.path.join(user_folder, main_script_name)

        bot.reply_to(message, f"📦 Arşiv çıkarıldı. Ana script: `{main_script_name}`\nAdmin onayına gönderiliyor...",
                     parse_mode='Markdown')

        # Admin onayı
        request_approval(user_id, main_script_path, main_script_name, 'py', message)

    except zipfile.BadZipFile as e:
        bot.reply_to(message, f"❌ Hata: Geçersiz/bozuk ZIP. {e}")
    except Exception as e:
        logger.error(f"Zip işleme hatası {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Zip hatası: {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir)
            except Exception: pass

# ================== MESAJ İŞLEYİCİLERİ ==================
def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username

    logger.info(f"Karşılama: user_id={user_id}, username=@{user_username}")

    if bot_locked and user_id not in admin_ids:
        bot.send_message(chat_id, t(user_id, 'bot_locked'))
        return

    user_bio = "Bio alınamadı"; photo_file_id = None
    try: user_bio = bot.get_chat(user_id).bio or "Bio yok"
    except Exception: pass
    try:
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos:
            photo_file_id = user_profile_photos.photos[0][-1].file_id
    except Exception: pass

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            owner_notification = (f"🆕 Yeni kullanıcı!\nAd: {user_name}\nKullanıcı: @{user_username or 'N/A'}\n"
                                  f"ID: `{user_id}`\nBio: {user_bio}")
            bot.send_message(OWNER_ID, owner_notification, parse_mode='Markdown')
            if photo_file_id: bot.send_photo(OWNER_ID, photo_file_id, caption=f"Yeni kullanıcı fotoğrafı {user_id}")
        except Exception as e: logger.error(f"Owner bildirim hatası: {e}")

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
    expiry_info = ""
    if user_id == OWNER_ID: user_status = "Sahip"
    elif user_id in admin_ids: user_status = "Admin"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "Premium"; days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\nAbonelik bitiş: {days_left} gün"
        else: user_status = "Ücretsiz (Süresi dolmuş)"; remove_subscription_db(user_id)
    else: user_status = "Ücretsiz"

    welcome_msg_text = (
        f"{t(user_id, 'welcome', name=user_name)}\n\n"
        f"{t(user_id, 'your_id')}: `{user_id}`\n"
        f"{t(user_id, 'username')}: `@{user_username or 'Yok'}`\n"
        f"{t(user_id, 'your_status')}: {user_status}{expiry_info}\n"
        f"{t(user_id, 'files_uploaded')}: {current_files} / {limit_str}\n\n"
        f"📢 Zorunlu kanal: {FORCED_CHANNEL}\n"
        f"💬 Destek: {SUPPORT_USERNAME}\n\n"
        f"📌 Sadece `.py` ve `.zip` dosyaları kabul edilir.\n"
        f"⚠️ Tüm `.py` dosyaları **admin onayı** sonrası çalışır.\n\n"
        f"Butonları kullan veya komut yaz."
    )
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    try:
        if photo_file_id: bot.send_photo(chat_id, photo_file_id)
        bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Karşılama gönderme hatası {user_id}: {e}", exc_info=True)
        try:
            bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
        except Exception as fallback_e:
            logger.error(f"Yedek gönderim hatası {user_id}: {fallback_e}")

def _logic_updates_channel(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📢 ' + t(user_id, 'updates_channel'), url=UPDATE_CHANNEL))
    bot.reply_to(message, f"Zorunlu kanalımıza katıl:\n{UPDATE_CHANNEL}\n\nDestek: {SUPPORT_USERNAME}",
                 reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'bot_locked')); return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
        bot.reply_to(message, t(user_id, 'file_limit_reached', current=current_files, limit=limit_str)); return
    bot.reply_to(message, t(user_id, 'send_file'))

def _logic_check_files(message):
    user_id = message.from_user.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message, t(user_id, 'no_files')); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        # Onay bekliyor mu kontrol
        pending = any(info['user_id'] == user_id and info['file_name'] == file_name
                      for info in pending_approvals.values())
        if pending:
            status_icon = t(user_id, 'waiting_approval_short')
        else:
            status_icon = t(user_id, 'running') if is_running else t(user_id, 'stopped')
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, t(user_id, 'your_files'), reply_markup=markup, parse_mode='Markdown')

def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    start_time_ping = time.time()
    wait_msg = bot.reply_to(message, "⚡ Hız test ediliyor...")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "Kilitli değil" if not bot_locked else "Kilitli"
        if user_id == OWNER_ID: user_level = "Sahip"
        elif user_id in admin_ids: user_level = "Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "Premium"
        else: user_level = "Ücretsiz"
        speed_msg = (f"⚡ Bot Hızı ve Durumu:\n\n"
                     f"📡 API Yanıt: {response_time} ms\n"
                     f"🔐 Bot Durumu: {status}\n"
                     f"👤 Seviyen: {user_level}")
        bot.edit_message_text(speed_msg, chat_id, wait_msg.message_id)
    except Exception as e:
        logger.error(f"Hız testi hatası: {e}", exc_info=True)
        bot.edit_message_text("Hız testi hatası.", chat_id, wait_msg.message_id)

def _logic_contact_owner(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📞 ' + t(user_id, 'contact_owner'),
                                          url=f'https://t.me/{SUPPORT_USERNAME.replace("@", "")}'))
    bot.reply_to(message, f"Destek: {SUPPORT_USERNAME}\nKanal: {FORCED_CHANNEL}", reply_markup=markup)

def _logic_uptime(message):
    uptime_str = get_uptime()
    bot.reply_to(message, f"⏱ Bot Çalışma Süresi: `{uptime_str}`", parse_mode='Markdown')

def _logic_subscriptions_panel(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'admin_required')); return
    bot.reply_to(message, "💳 Abonelik Yönetimi\nİşlem seç:", reply_markup=create_subscription_menu(user_id))

def _logic_statistics(message):
    user_id = message.from_user.id
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())
    running_bots_count = 0
    user_running_bots = 0
    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        try:
            s_owner_id, _ = script_key_iter.split('_', 1)
            if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
                running_bots_count += 1
                if int(s_owner_id) == user_id: user_running_bots += 1
        except Exception: pass

    pending_count = len(pending_approvals)
    stats_msg = (f"📊 Bot İstatistikleri:\n\n"
                 f"👥 Toplam Kullanıcı: {total_users}\n"
                 f"📁 Toplam Dosya Kaydı: {total_files_records}\n"
                 f"🤖 Aktif Bot: {running_bots_count}\n"
                 f"⏳ Bekleyen Onay: {pending_count}\n")
    if user_id in admin_ids:
        stats_msg += (f"🔒 Bot Durumu: {'Kilitli' if bot_locked else 'Kilitli değil'}\n"
                      f"⚙️ Senin Çalışan Botların: {user_running_bots}")
    else:
        stats_msg += f"⚙️ Senin Çalışan Botların: {user_running_bots}"
    bot.reply_to(message, stats_msg)

def _logic_broadcast_init(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'admin_required')); return
    msg = bot.reply_to(message, t(user_id, 'broadcast_prompt'))
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_toggle_lock_bot(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'admin_required')); return
    global bot_locked
    bot_locked = not bot_locked
    status = "kilitlendi" if bot_locked else "kilidi açıldı"
    logger.warning(f"Bot {status} - Admin {user_id}")
    bot.reply_to(message, f"🔒 Bot {status}.")

def _logic_admin_panel(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'admin_required')); return
    bot.reply_to(message, "👑 Admin Paneli", reply_markup=create_admin_panel(user_id))

def _logic_pending_list(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'admin_required')); return
    if not pending_approvals:
        bot.reply_to(message, t(user_id, 'no_pending')); return

    text = t(user_id, 'admin_pending_list') + "\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for aid, info in list(pending_approvals.items())[:10]:
        text += f"#{aid} - `{info['file_name']}` (User: `{info['user_id']}`)\n"
        row_markup = types.InlineKeyboardMarkup(row_width=2)
        row_markup.row(
            types.InlineKeyboardButton(f"✅ #{aid} Onayla", callback_data=f'approve_{aid}'),
            types.InlineKeyboardButton(f"❌ #{aid} Reddet", callback_data=f'reject_{aid}')
        )
        try:
            bot.send_message(message.chat.id, f"#{aid} - `{info['file_name']}` (User: `{info['user_id']}`)",
                             reply_markup=row_markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Bekleyen onay gönderim hatası: {e}")
    bot.reply_to(message, text, parse_mode='Markdown')

def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message
    else:
        return

    if admin_user_id not in admin_ids:
        reply_func(t(admin_user_id, 'admin_required')); return

    reply_func("🟢 Tüm kullanıcı scriptleri başlatılıyor...")
    started_count = 0; attempted_users = 0; skipped_files = 0

    for target_user_id, files_for_user in dict(user_files).items():
        if not files_for_user: continue
        attempted_users += 1
        user_folder = get_user_folder(target_user_id)
        for file_name, file_type in files_for_user:
            if file_type != 'py': continue
            if not is_bot_running(target_user_id, file_name):
                # Onay bekliyor mu?
                pending = any(info['user_id'] == target_user_id and info['file_name'] == file_name
                              for info in pending_approvals.values())
                if pending:
                    skipped_files += 1
                    continue
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        threading.Thread(target=run_script,
                                         args=(file_path, target_user_id, user_folder, file_name,
                                               admin_message_obj_for_script_runner),
                                         daemon=True).start()
                        started_count += 1
                        time.sleep(0.7)
                    except Exception:
                        skipped_files += 1
                else:
                    skipped_files += 1

    summary_msg = (f"✅ Tüm Scriptler - Tamamlandı:\n\n"
                   f"🚀 Başlatılan: {started_count}\n"
                   f"👥 İşlenen kullanıcı: {attempted_users}\n"
                   f"⏭️ Atlanan/Hata: {skipped_files}")
    reply_func(summary_msg)

def get_uptime():
    uptime = datetime.now() - BOT_START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}g {hours}s {minutes}d {seconds}sn"

# ================== KOMUT İŞLEYİCİLER ==================
@bot.message_handler(commands=['mpx'])
def handle_mpx_command(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'bot_locked')); return

    if not message.text or len(message.text.split()) < 2:
        bot.reply_to(message, "Kullanım: `/mpx sorun nedir?`", parse_mode='Markdown'); return

    query = message.text.split(' ', 1)[1]
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        headers = {"Authorization": f"Bearer {A4F_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": A4F_MODEL, "messages": [{"role": "user", "content": query}], "temperature": 0.7}
        response = requests.post(A4F_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        answer = result.get('choices', [{}])[0].get('message', {}).get('content', 'API yanıt vermedi')
        if len(answer) > 4000:
            for x in range(0, len(answer), 4000):
                bot.reply_to(message, answer[x:x+4000], parse_mode='Markdown')
        else:
            bot.reply_to(message, answer, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"MPX AI hatası: {e}")
        bot.reply_to(message, "API bağlantı hatası. Tekrar dene.")

@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message): _logic_send_welcome(message)

@bot.message_handler(commands=['lang', 'dil'])
def command_lang(message):
    bot.reply_to(message, "🌐 Dil seç / Choose language:", reply_markup=create_lang_menu())

@bot.message_handler(commands=['status'])
def command_show_status(message): _logic_statistics(message)

@bot.message_handler(commands=['uptime'])
def command_uptime(message): _logic_uptime(message)

@bot.message_handler(commands=['ping'])
def ping(message):
    start_ping_time = time.time()
    msg = bot.reply_to(message, "Pong!")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    uptime_str = get_uptime()
    bot.edit_message_text(f"🏓 Pong!\nGecikme: {latency} ms\nÇalışma: {uptime_str}",
                          message.chat.id, msg.message_id)

@bot.message_handler(commands=['pending', 'bekleyen'])
def command_pending(message):
    _logic_pending_list(message)

BUTTON_TEXT_TO_LOGIC = {
    "📢 Güncelleme Kanalı": _logic_updates_channel,
    "📢 Updates Channel": _logic_updates_channel,
    "📤 Dosya Yükle": _logic_upload_file,
    "📤 Upload File": _logic_upload_file,
    "📂 Dosyaları Kontrol Et": _logic_check_files,
    "📂 Check Files": _logic_check_files,
    "⚡ Bot Hızı": _logic_bot_speed,
    "⚡ Bot Speed": _logic_bot_speed,
    "📞 Sahibe Ulaş": _logic_contact_owner,
    "📞 Contact Owner": _logic_contact_owner,
    "📊 İstatistikler": _logic_statistics,
    "📊 Statistics": _logic_statistics,
    "⏱ Çalışma Süresi": _logic_uptime,
    "⏱ Uptime": _logic_uptime,
    "💳 Abonelikler": _logic_subscriptions_panel,
    "💳 Subscriptions": _logic_subscriptions_panel,
    "📢 Duyuru": _logic_broadcast_init,
    "📢 Broadcast": _logic_broadcast_init,
    "🔒 Botu Kilitle": _logic_toggle_lock_bot,
    "🔒 Lock Bot": _logic_toggle_lock_bot,
    "🟢 Tüm Kodları Çalıştır": _logic_run_all_scripts,
    "🟢 Run All Code": _logic_run_all_scripts,
    "👑 Admin Paneli": _logic_admin_panel,
    "👑 Admin Panel": _logic_admin_panel,
    "🤖 MPX AI": lambda m: handle_mpx_command(m),
    "🤖 MPX Ai": lambda m: handle_mpx_command(m),
}

@bot.message_handler(func=lambda message: message.text in BUTTON_TEXT_TO_LOGIC)
def handle_button_text(message):
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func:
        try: logic_func(message)
        except Exception as e: logger.error(f"Buton işleme hatası: {e}", exc_info=True)

@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message): _logic_updates_channel(message)
@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message): _logic_upload_file(message)
@bot.message_handler(commands=['checkfiles'])
def command_check_files(message): _logic_check_files(message)
@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message): _logic_bot_speed(message)
@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message): _logic_contact_owner(message)
@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message): _logic_subscriptions_panel(message)
@bot.message_handler(commands=['statistics'])
def command_statistics(message): _logic_statistics(message)
@bot.message_handler(commands=['broadcast'])
def command_broadcast(message): _logic_broadcast_init(message)
@bot.message_handler(commands=['lockbot'])
def command_lock_bot(message): _logic_toggle_lock_bot(message)
@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message): _logic_admin_panel(message)
@bot.message_handler(commands=['runningallcode'])
def command_run_all_code(message): _logic_run_all_scripts(message)

# ================== DOSYA YÜKLEME ==================
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document
    logger.info(f"Belge: {user_id}: {doc.file_name}")

    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'bot_locked')); return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
        bot.reply_to(message, t(user_id, 'file_limit_reached', current=current_files, limit=limit_str)); return

    file_name = doc.file_name
    if not file_name:
        bot.reply_to(message, "❌ Dosya adı yok."); return

    file_ext = os.path.splitext(file_name)[1].lower()
    # SADECE .py ve .zip kabul
    if file_ext not in ['.py', '.zip']:
        bot.reply_to(message, t(user_id, 'unsupported_type')); return

    max_file_size = 20 * 1024 * 1024
    if doc.file_size > max_file_size:
        bot.reply_to(message, t(user_id, 'file_too_large')); return

    try:
        try:
            bot.forward_message(OWNER_ID, chat_id, message.message_id)
            bot.send_message(OWNER_ID, f"📎 Dosya '{file_name}' - {message.from_user.first_name} (`{user_id}`)",
                             parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Forward hatası: {e}")

        download_wait_msg = bot.reply_to(message, f"📥 `{file_name}` indiriliyor...")
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)
        bot.edit_message_text(f"📥 `{file_name}` indirildi. İşleniyor...", chat_id, download_wait_msg.message_id)
        user_folder = get_user_folder(user_id)

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            # .py dosyası
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(downloaded_file_content)
            save_user_file(user_id, file_name, 'py')

            # Admin onayı gerekli
            request_approval(user_id, file_path, file_name, 'py', message)

    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"TG API hatası: {e}", exc_info=True)
        if "file is too big" in str(e).lower():
            bot.reply_to(message, "❌ Telegram API Hatası: Dosya çok büyük (~20MB).")
        else:
            bot.reply_to(message, f"❌ Telegram API Hatası: {str(e)}")
    except Exception as e:
        logger.error(f"Genel hata: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Beklenmedik hata: {str(e)}")

# ================== CALLBACK İŞLEYİCİLER ==================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: User={user_id}, Data='{data}'")

    if bot_locked and user_id not in admin_ids and data not in [
        'back_to_main', 'speed', 'stats', 'mpx_ai', 'uptime',
        'change_lang', 'setlang_tr', 'setlang_en', 'setlang_ru', 'setlang_ar', 'setlang_hi'
    ] and not data.startswith('approve_') and not data.startswith('reject_'):
        bot.answer_callback_query(call.id, t(user_id, 'bot_locked'), show_alert=True)
        return
    try:
        if data == 'upload': upload_callback(call)
        elif data == 'check_files': check_files_callback(call)
        elif data.startswith('file_'): file_control_callback(call)
        elif data.startswith('start_'): start_bot_callback(call)
        elif data.startswith('stop_'): stop_bot_callback(call)
        elif data.startswith('restart_'): restart_bot_callback(call)
        elif data.startswith('delete_'): delete_bot_callback(call)
        elif data.startswith('logs_'): logs_bot_callback(call)
        elif data == 'speed': speed_callback(call)
        elif data == 'back_to_main': back_to_main_callback(call)
        elif data.startswith('approve_'): handle_approve(call)
        elif data.startswith('reject_'): handle_reject(call)
        elif data == 'pending_list': admin_required_callback(call, lambda c: _logic_pending_list(c.message))
        elif data.startswith('confirm_broadcast_'): handle_confirm_broadcast(call)
        elif data == 'cancel_broadcast': handle_cancel_broadcast(call)
        elif data == 'subscription': admin_required_callback(call, subscription_management_callback)
        elif data == 'stats': stats_callback(call)
        elif data == 'lock_bot': admin_required_callback(call, lock_bot_callback)
        elif data == 'unlock_bot': admin_required_callback(call, unlock_bot_callback)
        elif data == 'run_all_scripts': admin_required_callback(call, run_all_scripts_callback)
        elif data == 'broadcast': admin_required_callback(call, broadcast_init_callback)
        elif data == 'admin_panel': admin_required_callback(call, admin_panel_callback)
        elif data == 'add_admin': owner_required_callback(call, add_admin_init_callback)
        elif data == 'remove_admin': owner_required_callback(call, remove_admin_init_callback)
        elif data == 'list_admins': admin_required_callback(call, list_admins_callback)
        elif data == 'add_subscription': admin_required_callback(call, add_subscription_init_callback)
        elif data == 'remove_subscription': admin_required_callback(call, remove_subscription_init_callback)
        elif data == 'check_subscription': admin_required_callback(call, check_subscription_init_callback)
        elif data == 'change_lang': change_lang_callback(call)
        elif data.startswith('setlang_'): set_lang_callback(call)
        elif data == 'mpx_ai':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id,
                             "🤖 Sorunu /mpx komutuyla sor.\nÖrnek: `/mpx AI nedir?`", parse_mode='Markdown')
        elif data == 'uptime':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"⏱ Çalışma: `{get_uptime()}`", parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "Bilinmeyen işlem.")
    except Exception as e:
        logger.error(f"Callback hatası '{data}': {e}", exc_info=True)
        try: bot.answer_callback_query(call.id, "İşlem hatası.", show_alert=True)
        except Exception: pass

def change_lang_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("🌐 Dil seç / Choose language:", call.message.chat.id,
                              call.message.message_id, reply_markup=create_lang_menu())
    except Exception as e: logger.error(f"Dil menüsü hatası: {e}")

def set_lang_callback(call):
    lang_code = call.data.replace('setlang_', '')
    if lang_code not in TRANSLATIONS: lang_code = 'tr'
    user_id = call.from_user.id
    save_user_lang(user_id, lang_code)
    bot.answer_callback_query(call.id, f"✅ Dil: {lang_code.upper()}")
    chat_id = call.message.chat.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
    welcome_msg_text = (
        f"{t(user_id, 'welcome', name=call.from_user.first_name)}\n\n"
        f"{t(user_id, 'your_id')}: `{user_id}`\n"
        f"{t(user_id, 'files_uploaded')}: {current_files} / {limit_str}\n\n"
        f"📢 {FORCED_CHANNEL}\n💬 {SUPPORT_USERNAME}"
    )
    try:
        bot.edit_message_text(welcome_msg_text, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ana menü güncelleme hatası: {e}")

def admin_required_callback(call, func_to_run):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'admin_required'), show_alert=True); return
    func_to_run(call)

def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'owner_required'), show_alert=True); return
    func_to_run(call)

def upload_callback(call):
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
        bot.answer_callback_query(call.id, t(user_id, 'file_limit_reached', current=current_files, limit=limit_str),
                                  show_alert=True); return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, t(user_id, 'send_file'))

def check_files_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.answer_callback_query(call.id, t(user_id, 'no_files'), show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 " + t(user_id, 'back_to_main'), callback_data='back_to_main'))
            bot.edit_message_text(t(user_id, 'no_files'), chat_id, call.message.message_id, reply_markup=markup)
        except Exception: pass
        return
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        pending = any(info['user_id'] == user_id and info['file_name'] == file_name
                      for info in pending_approvals.values())
        if pending:
            status_icon = "⏳ " + t(user_id, 'waiting_approval_short')
        else:
            status_icon = ("🟢 " + t(user_id, 'running')) if is_running else ("🔴 " + t(user_id, 'stopped'))
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 " + t(user_id, 'back_to_main'), callback_data='back_to_main'))
    try:
        bot.edit_message_text(t(user_id, 'your_files'), chat_id, call.message.message_id,
                              reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" not in str(e): logger.error(f"Dosya listesi hatası: {e}")
    except Exception as e:
        logger.error(f"Dosya listesi hatası: {e}", exc_info=True)

def file_control_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'permission_denied'), show_alert=True)
            check_files_callback(call); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'file_not_found'), show_alert=True)
            check_files_callback(call); return

        bot.answer_callback_query(call.id)
        is_running = is_bot_running(script_owner_id, file_name)
        pending = any(info['user_id'] == script_owner_id and info['file_name'] == file_name
                      for info in pending_approvals.values())
        if pending:
            status_text = "⏳ " + t(requesting_user_id, 'waiting_approval_short')
        else:
            status_text = t(requesting_user_id, 'running') if is_running else t(requesting_user_id, 'stopped')
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?')

        # Onay bekliyorsa start butonu gösterme
        if pending:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.row(
                types.InlineKeyboardButton("🗑️ " + t(requesting_user_id, 'delete'),
                                           callback_data=f'delete_{script_owner_id}_{file_name}')
            )
            markup.add(types.InlineKeyboardButton("🔙 " + t(requesting_user_id, 'back_to_files'),
                                                  callback_data='check_files'))
        else:
            markup = create_control_buttons(script_owner_id, file_name, is_running, requesting_user_id)

        try:
            bot.edit_message_text(
                f"🎛 Kontrol: `{file_name}` ({file_type}) - Kullanıcı `{script_owner_id}`\nDurum: {status_text}",
                call.message.chat.id, call.message.message_id,
                reply_markup=markup, parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" not in str(e): raise
    except Exception as e:
        logger.error(f"file_control hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hata.", show_alert=True)

def start_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'permission_denied'), show_alert=True); return

        # Onay bekliyor mu?
        if any(info['user_id'] == script_owner_id and info['file_name'] == file_name
               for info in pending_approvals.values()):
            bot.answer_callback_query(call.id, "⏳ Bu dosya admin onayı bekliyor.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, t(requesting_user_id, 'file_not_found'), show_alert=True); return

        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"Hata: `{file_name}` kayıp! Yeniden yükle.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name); return

        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"'{file_name}' zaten çalışıyor.", show_alert=True); return

        bot.answer_callback_query(call.id, f"'{file_name}' başlatılıyor...")

        # KRİTİK: Sadece admin veya sahip, kullanıcı kendi .py'sini başlatamaz (onay sonrası admin başlatır)
        # Ancak kendi kullanıcı onaylanmışsa tekrar başlatabilir.
        # Onay kontrolü: pending'de yok + is_running değil + daha önce onaylanmış (user_files'da var).
        # Basitçe: pending yoksa başlatılabilir.

        threading.Thread(target=run_script,
                         args=(file_path, script_owner_id, user_folder, file_name, call.message),
                         daemon=True).start()

        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name)
        status_text = t(requesting_user_id, 'running') if is_now_running else t(requesting_user_id, 'starting')
        try:
            bot.edit_message_text(
                f"🎛 Kontrol: `{file_name}` ({file_type}) - Kullanıcı `{script_owner_id}`\nDurum: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running, requesting_user_id),
                parse_mode='Markdown'
            )
        except Exception: pass
    except Exception as e:
        logger.error(f"start_bot hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hata.", show_alert=True)

def stop_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'permission_denied'), show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, t(requesting_user_id, 'file_not_found'), show_alert=True); return

        file_type = file_info[1]
        script_key = f"{script_owner_id}_{file_name}"

        if not is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"'{file_name}' zaten durdu.", show_alert=True); return

        bot.answer_callback_query(call.id, f"'{file_name}' durduruluyor...")
        process_info = bot_scripts.get(script_key)
        if process_info:
            kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]

        try:
            bot.edit_message_text(
                f"🎛 Kontrol: `{file_name}` ({file_type}) - Kullanıcı `{script_owner_id}`\nDurum: 🔴 {t(requesting_user_id, 'stopped')}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, False, requesting_user_id),
                parse_mode='Markdown'
            )
        except Exception: pass
    except Exception as e:
        logger.error(f"stop_bot hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hata.", show_alert=True)

def restart_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'permission_denied'), show_alert=True); return

        # Onay bekliyor mu?
        if any(info['user_id'] == script_owner_id and info['file_name'] == file_name
               for info in pending_approvals.values()):
            bot.answer_callback_query(call.id, "⏳ Bu dosya admin onayı bekliyor.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, t(requesting_user_id, 'file_not_found'), show_alert=True); return

        file_type = file_info[1]; user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name); script_key = f"{script_owner_id}_{file_name}"

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"Hata: `{file_name}` kayıp!", show_alert=True)
            remove_user_file_db(script_owner_id, file_name); return

        bot.answer_callback_query(call.id, f"'{file_name}' yeniden başlatılıyor...")
        if is_bot_running(script_owner_id, file_name):
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(1.5)

        threading.Thread(target=run_script,
                         args=(file_path, script_owner_id, user_folder, file_name, call.message),
                         daemon=True).start()

        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name)
        status_text = t(requesting_user_id, 'running') if is_now_running else t(requesting_user_id, 'starting')
        try:
            bot.edit_message_text(
                f"🎛 Kontrol: `{file_name}` ({file_type}) - Kullanıcı `{script_owner_id}`\nDurum: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running, requesting_user_id),
                parse_mode='Markdown'
            )
        except Exception: pass
    except Exception as e:
        logger.error(f"restart_bot hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hata.", show_alert=True)

def delete_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'permission_denied'), show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'file_not_found'), show_alert=True); return

        bot.answer_callback_query(call.id, f"'{file_name}' siliniyor...")
        script_key = f"{script_owner_id}_{file_name}"
        if is_bot_running(script_owner_id, file_name):
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(0.5)

        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except OSError: pass
        if os.path.exists(log_path):
            try: os.remove(log_path)
            except OSError: pass

        remove_user_file_db(script_owner_id, file_name)
        try:
            bot.edit_message_text(
                f"✅ `{file_name}` (Kullanıcı `{script_owner_id}`) silindi!",
                call.message.chat.id, call.message.message_id, reply_markup=None, parse_mode='Markdown'
            )
        except Exception:
            bot.send_message(call.message.chat.id, f"`{file_name}` silindi.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"delete_bot hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hata.", show_alert=True)

def logs_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, t(requesting_user_id, 'permission_denied'), show_alert=True); return

        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, f"'{file_name}' için log yok.", show_alert=True); return

        bot.answer_callback_query(call.id)
        try:
            log_content = ""; file_size = os.path.getsize(log_path)
            max_log_kb = 100; max_tg_msg = 4096
            if file_size == 0:
                log_content = "(Log boş)"
            elif file_size > max_log_kb * 1024:
                with open(log_path, 'rb') as f:
                    f.seek(-max_log_kb * 1024, os.SEEK_END)
                    log_bytes = f.read()
                log_content = f"(Son {max_log_kb} KB)\n...\n" + log_bytes.decode('utf-8', errors='ignore')
            else:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()

            if len(log_content) > max_tg_msg:
                log_content = log_content[-max_tg_msg:]
            if not log_content.strip():
                log_content = "(İçerik yok)"

            bot.send_message(chat_id_for_reply, f"📜 Log: `{file_name}`\n```\n{log_content}\n```", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Log okuma hatası: {e}", exc_info=True)
            bot.send_message(chat_id_for_reply, f"Log okuma hatası `{file_name}`.")
    except Exception as e:
        logger.error(f"logs_bot hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hata.", show_alert=True)

def speed_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    start_cb_ping_time = time.time()
    try:
        bot.edit_message_text("⚡ Hız test ediliyor...", chat_id, call.message.message_id)
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_cb_ping_time) * 1000, 2)
        status = "Kilitli değil" if not bot_locked else "Kilitli"
        if user_id == OWNER_ID: user_level = "Sahip"
        elif user_id in admin_ids: user_level = "Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "Premium"
        else: user_level = "Ücretsiz"
        speed_msg = (f"⚡ Bot Hızı ve Durumu:\n\n"
                     f"📡 API Yanıt: {response_time} ms\n"
                     f"🔐 Bot Durumu: {status}\n"
                     f"👤 Seviyen: {user_level}")
        bot.answer_callback_query(call.id)
        bot.edit_message_text(speed_msg, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id))
    except Exception as e:
        logger.error(f"Hız testi hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Hız testi hatası.", show_alert=True)

def back_to_main_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
    expiry_info = ""
    if user_id == OWNER_ID: user_status = "Sahip"
    elif user_id in admin_ids: user_status = "Admin"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "Premium"; days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\nAbonelik: {days_left} gün"
        else: user_status = "Ücretsiz (Süresi dolmuş)"
    else: user_status = "Ücretsiz"

    main_menu_text = (
        f"{t(user_id, 'welcome', name=call.from_user.first_name)}\n\n"
        f"{t(user_id, 'your_id')}: `{user_id}`\n"
        f"{t(user_id, 'your_status')}: {user_status}{expiry_info}\n"
        f"{t(user_id, 'files_uploaded')}: {current_files} / {limit_str}\n\n"
        f"📢 {FORCED_CHANNEL}\n💬 {SUPPORT_USERNAME}"
    )
    try:
        bot.answer_callback_query(call.id)
        bot.edit_message_text(main_menu_text, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" not in str(e): logger.error(f"back_to_main hatası: {e}")
    except Exception as e:
        logger.error(f"back_to_main hatası: {e}", exc_info=True)

def subscription_management_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("💳 Abonelik Yönetimi\nİşlem seç:", call.message.chat.id,
                              call.message.message_id, reply_markup=create_subscription_menu(call.from_user.id))
    except Exception as e: logger.error(f"Abonelik menü hatası: {e}")

def stats_callback(call):
    bot.answer_callback_query(call.id)
    _logic_statistics(call.message)

def lock_bot_callback(call):
    global bot_locked; bot_locked = True
    logger.warning(f"Bot kilitlendi - Admin {call.from_user.id}")
    bot.answer_callback_query(call.id, t(call.from_user.id, 'bot_locked_msg'))
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception: pass

def unlock_bot_callback(call):
    global bot_locked; bot_locked = False
    logger.warning(f"Bot kilidi açıldı - Admin {call.from_user.id}")
    bot.answer_callback_query(call.id, t(call.from_user.id, 'bot_unlocked_msg'))
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception: pass

def run_all_scripts_callback(call):
    _logic_run_all_scripts(call)

def broadcast_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, t(call.from_user.id, 'broadcast_prompt'))
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, t(user_id, 'admin_required')); return
    if message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, t(user_id, 'broadcast_cancelled')); return

    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video):
        bot.reply_to(message, "Boş mesaj gönderilemez. Metin veya medya gönder ya da /cancel.")
        return

    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t(user_id, 'broadcast_confirm'),
                                   callback_data=f"confirm_broadcast_{message.message_id}"),
        types.InlineKeyboardButton("❌ İptal", callback_data="cancel_broadcast")
    )

    preview_text = broadcast_content[:1000].strip() if broadcast_content else "(Medya mesajı)"
    bot.reply_to(message, f"📢 Duyuru Onayı:\n\n```\n{preview_text}\n```\n"
                          f"**{target_count}** kullanıcıya gönderilecek. Emin misin?",
                 reply_markup=markup, parse_mode='Markdown')

def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in admin_ids:
        bot.answer_callback_query(call.id, t(user_id, 'admin_required'), show_alert=True); return
    try:
        original_message = call.message.reply_to_message
        if not original_message:
            raise ValueError("Orijinal mesaj alınamadı.")

        broadcast_text = None; broadcast_photo_id = None; broadcast_video_id = None
        if original_message.text: broadcast_text = original_message.text
        elif original_message.photo: broadcast_photo_id = original_message.photo[-1].file_id
        elif original_message.video: broadcast_video_id = original_message.video.file_id
        else: raise ValueError("Desteklenmeyen mesaj.")

        bot.answer_callback_query(call.id, "Duyuru başlatılıyor...")
        bot.edit_message_text(f"{len(active_users)} kullanıcıya duyuru gönderiliyor...",
                              chat_id, call.message.message_id, reply_markup=None)
        thread = threading.Thread(target=execute_broadcast, args=(
            broadcast_text, broadcast_photo_id, broadcast_video_id,
            original_message.caption if (broadcast_photo_id or broadcast_video_id) else None,
            chat_id), daemon=True)
        thread.start()
    except Exception as e:
        logger.error(f"Duyuru onay hatası: {e}", exc_info=True)
        bot.edit_message_text(f"Duyuru hatası: {e}", chat_id, call.message.message_id, reply_markup=None)

def handle_cancel_broadcast(call):
    bot.answer_callback_query(call.id, t(call.from_user.id, 'broadcast_cancelled'))
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception: pass
    if call.message.reply_to_message:
        try: bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        except Exception: pass

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0; failed_count = 0; blocked_count = 0
    start_exec_time = time.time()
    users_to_broadcast = list(active_users); total_users = len(users_to_broadcast)
    batch_size = 25; delay_batches = 1.5

    for i, user_id_bc in enumerate(users_to_broadcast):
        try:
            if broadcast_text:
                bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
            elif photo_id:
                bot.send_photo(user_id_bc, photo_id, caption=caption,
                               parse_mode='Markdown' if caption else None)
            elif video_id:
                bot.send_video(user_id_bc, video_id, caption=caption,
                               parse_mode='Markdown' if caption else None)
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            err_desc = str(e).lower()
            if any(s in err_desc for s in ["bot was blocked", "user is deactivated",
                                           "chat not found", "kicked from", "restricted"]):
                blocked_count += 1
            elif "flood control" in err_desc or "too many requests" in err_desc:
                retry_after = 5
                match = re.search(r"retry after (\d+)", err_desc)
                if match: retry_after = int(match.group(1)) + 1
                time.sleep(retry_after)
                try:
                    if broadcast_text:
                        bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
                    sent_count += 1
                except Exception: failed_count += 1
            else:
                failed_count += 1
        except Exception:
            failed_count += 1

        if (i + 1) % batch_size == 0 and i < total_users - 1:
            time.sleep(delay_batches)
        elif i % 5 == 0:
            time.sleep(0.2)

    duration = round(time.time() - start_exec_time, 2)
    result_msg = (f"✅ Duyuru Tamamlandı!\n\n"
                  f"📤 Gönderilen: {sent_count}\n"
                  f"❌ Başarısız: {failed_count}\n"
                  f"🚫 Bloklu/Pasif: {blocked_count}\n"
                  f"👥 Hedef: {total_users}\n"
                  f"⏱ Süre: {duration}s")
    logger.info(result_msg)
    try: bot.send_message(admin_chat_id, result_msg)
    except Exception as e: logger.error(f"Duyuru sonucu gönderilemedi: {e}")

def admin_panel_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("👑 Admin Paneli\nAdminleri yönet.", call.message.chat.id,
                              call.message.message_id, reply_markup=create_admin_panel(call.from_user.id))
    except Exception as e: logger.error(f"Admin panel hatası: {e}")

def add_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Admin yapmak için Kullanıcı ID gir.\nİptal: /cancel")
    bot.register_next_step_handler(msg, process_add_admin_id)

def process_add_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID:
        bot.reply_to(message, "Sadece sahip."); return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "İptal edildi."); return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0: raise ValueError()
        if new_admin_id == OWNER_ID:
            bot.reply_to(message, "Sahip zaten sahip."); return
        if new_admin_id in admin_ids:
            bot.reply_to(message, f"`{new_admin_id}` zaten admin."); return
        add_admin_db(new_admin_id)
        bot.reply_to(message, f"✅ `{new_admin_id}` admin yapıldı.")
        try: bot.send_message(new_admin_id, "🎉 Artık adminsin!")
        except Exception: pass
    except ValueError:
        bot.reply_to(message, "Geçersiz ID.")
        msg = bot.send_message(message.chat.id, "ID gir veya /cancel.")
        bot.register_next_step_handler(msg, process_add_admin_id)
    except Exception as e: logger.error(f"Admin ekleme hatası: {e}")

def remove_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Admin silmek için Kullanıcı ID gir.\nİptal: /cancel")
    bot.register_next_step_handler(msg, process_remove_admin_id)

def process_remove_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID:
        bot.reply_to(message, "Sadece sahip."); return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "İptal edildi."); return
    try:
        admin_id_remove = int(message.text.strip())
        if admin_id_remove == OWNER_ID:
            bot.reply_to(message, "Sahip kendini silemez."); return
        if admin_id_remove not in admin_ids:
            bot.reply_to(message, f"`{admin_id_remove}` admin değil."); return
        if remove_admin_db(admin_id_remove):
            bot.reply_to(message, f"✅ `{admin_id_remove}` admin silindi.")
            try: bot.send_message(admin_id_remove, "Artık admin değilsin.")
            except Exception: pass
        else:
            bot.reply_to(message, f"`{admin_id_remove}` silinemedi.")
    except ValueError:
        bot.reply_to(message, "Geçersiz ID.")
        msg = bot.send_message(message.chat.id, "ID gir veya /cancel.")
        bot.register_next_step_handler(msg, process_remove_admin_id)
    except Exception as e: logger.error(f"Admin silme hatası: {e}")

def list_admins_callback(call):
    bot.answer_callback_query(call.id)
    try:
        admin_list_str = "\n".join(f"- `{aid}` {'(Sahip)' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
        if not admin_list_str: admin_list_str = "(Admin yok!)"
        bot.edit_message_text(f"👑 Mevcut Adminler:\n\n{admin_list_str}", call.message.chat.id,
                              call.message.message_id, reply_markup=create_admin_panel(call.from_user.id),
                              parse_mode='Markdown')
    except Exception as e: logger.error(f"Admin listesi hatası: {e}")

def add_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Kullanıcı ID ve gün gir (örn: `12345678 30`).\nİptal: /cancel")
    bot.register_next_step_handler(msg, process_add_subscription_details)

def process_add_subscription_details(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids:
        bot.reply_to(message, t(admin_id_check, 'admin_required')); return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "İptal."); return
    try:
        parts = message.text.split()
        if len(parts) != 2: raise ValueError("Format")
        sub_user_id = int(parts[0].strip()); days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0: raise ValueError("Pozitif olmalı")

        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date_new_sub = datetime.now()
        if current_expiry and current_expiry > start_date_new_sub:
            start_date_new_sub = current_expiry
        new_expiry = start_date_new_sub + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)

        bot.reply_to(message, f"✅ `{sub_user_id}` için {days} günlük abonelik.\nBitiş: {new_expiry:%Y-%m-%d}")
        try:
            bot.send_message(sub_user_id, f"✅ Aboneliğin {days} gün uzatıldı! Bitiş: {new_expiry:%Y-%m-%d}.")
        except Exception: pass
    except ValueError as e:
        bot.reply_to(message, f"Geçersiz: {e}. Format: `ID gün` veya /cancel.")
        msg = bot.send_message(message.chat.id, "ID ve gün gir veya /cancel.")
        bot.register_next_step_handler(msg, process_add_subscription_details)
    except Exception as e: logger.error(f"Abonelik ekleme hatası: {e}")

def remove_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Aboneliği silinecek Kullanıcı ID gir.\nİptal: /cancel")
    bot.register_next_step_handler(msg, process_remove_subscription_id)

def process_remove_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids:
        bot.reply_to(message, "Yetki yok."); return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "İptal."); return
    try:
        sub_user_id_remove = int(message.text.strip())
        if sub_user_id_remove not in user_subscriptions:
            bot.reply_to(message, f"`{sub_user_id_remove}` abonesi yok."); return
        remove_subscription_db(sub_user_id_remove)
        bot.reply_to(message, f"✅ `{sub_user_id_remove}` aboneliği silindi.")
        try: bot.send_message(sub_user_id_remove, "Aboneliğin admin tarafından kaldırıldı.")
        except Exception: pass
    except ValueError:
        bot.reply_to(message, "Geçersiz ID.")
        msg = bot.send_message(message.chat.id, "ID gir veya /cancel.")
        bot.register_next_step_handler(msg, process_remove_subscription_id)
    except Exception as e: logger.error(f"Abonelik silme hatası: {e}")

def check_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Kontrol edilecek Kullanıcı ID gir.\nİptal: /cancel")
    bot.register_next_step_handler(msg, process_check_subscription_id)

def process_check_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids:
        bot.reply_to(message, "Yetki yok."); return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "İptal."); return
    try:
        sub_user_id_check = int(message.text.strip())
        if sub_user_id_check in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id_check].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    days_left = (expiry_dt - datetime.now()).days
                    bot.reply_to(message, f"✅ `{sub_user_id_check}` aktif abonelik.\n"
                                          f"Bitiş: {expiry_dt:%Y-%m-%d %H:%M:%S} ({days_left} gün)")
                else:
                    bot.reply_to(message, f"⚠️ `{sub_user_id_check}` abonelik süresi dolmuş ({expiry_dt:%Y-%m-%d}).")
                    remove_subscription_db(sub_user_id_check)
        else:
            bot.reply_to(message, f"`{sub_user_id_check}` abonelik kaydı yok.")
    except ValueError:
        bot.reply_to(message, "Geçersiz ID.")
        msg = bot.send_message(message.chat.id, "ID gir veya /cancel.")
        bot.register_next_step_handler(msg, process_check_subscription_id)
    except Exception as e: logger.error(f"Abonelik kontrol hatası: {e}")

# ================== KAPANIŞ ==================
def cleanup():
    logger.warning("Kapanış. Süreçler temizleniyor...")
    script_keys_to_stop = list(bot_scripts.keys())
    for key in script_keys_to_stop:
        if key in bot_scripts:
            try: kill_process_tree(bot_scripts[key])
            except Exception: pass

atexit.register(cleanup)

# ================== ANA ÇALIŞTIRMA ==================
if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🤖 Bot Başlatılıyor...")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Base Dir: {BASE_DIR}")
    logger.info(f"Upload Dir: {UPLOAD_BOTS_DIR}")
    logger.info(f"Data Dir: {IROTECH_DIR}")
    logger.info(f"Sahip ID: {OWNER_ID}")
    logger.info(f"Adminler: {admin_ids}")
    logger.info(f"Zorunlu Kanal: {FORCED_CHANNEL}")
    logger.info(f"Destek: {SUPPORT_USERNAME}")
    logger.info(f"Başlangıç: {BOT_START_TIME}")
    logger.info("=" * 50)

    keep_alive()

    logger.info("Polling başlatılıyor...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            logger.warning("Polling ReadTimeout. 5s sonra yeniden başlatılıyor...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"Bağlantı hatası: {ce}. 15s sonra denenecek...")
            time.sleep(15)
        except Exception as e:
            logger.critical(f"Kritik polling hatası: {e}", exc_info=True)
            logger.info("30s sonra yeniden başlatılıyor...")
            time.sleep(30)
        finally:
            time.sleep(1)
