# =====================================================
#  🚀 FREEBOTHOSTING SERVER
# =====================================================
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
from threading import Thread
import re
import sys
import atexit
import requests
import gc
from flask import Flask

# ================== OTOMATİK PAKET KURULUMU ==================
def auto_install_packages():
    """Eksik paketleri otomatik + zorla kurar. Hata olsa bile devam eder."""
    required = ['pyTelegramBotAPI', 'Flask', 'requests', 'psutil']
    for pkg in required:
        try:
            check_name = 'telebot' if pkg == 'pyTelegramBotAPI' else pkg.lower()
            __import__(check_name)
            continue
        except ImportError:
            pass
        try:
            print(f"📦 {pkg} kuruluyor...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--quiet',
                 '--no-warn-script-location', '--disable-pip-version-check', pkg],
                capture_output=True, timeout=180, check=False
            )
            print(f"✅ {pkg} kuruldu.")
        except Exception as e:
            print(f"⚠️ {pkg} kurulamadı (devam): {e}")

auto_install_packages()

app = Flask('')

@app.route('/')
def home():
    return "Bot çalışıyor 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    try:
        t = Thread(target=run_flask, daemon=True)
        t.start()
        print("Flask Keep-Alive sunucusu başlatıldı.")
    except Exception as e:
        print(f"Keep-alive hatası (önemsiz): {e}")

BOT_START_TIME = datetime.now()

# ================== ÇOKLU DİL ==================
USER_LANG = {}
TRANSLATIONS = {
    'tr': {
        'welcome': "Hoş geldin, {name}!",
        'your_id': "Kullanıcı ID'n", 'username': "Kullanıcı Adın",
        'your_status': "Durumun", 'files_uploaded': "Yüklenen Dosyalar",
        'upload_file': "📤 Dosya Yükle", 'check_files': "📂 Dosyalarım",
        'bot_speed': "⚡ Bot Hızı", 'statistics': "📊 İstatistikler",
        'updates_channel': "📢 Kanal", 'contact_owner': "📞 Destek",
        'uptime': "⏱ Süre", 'admin_panel': "👑 Admin",
        'broadcast': "📢 Duyuru", 'subscriptions': "💳 Abonelik",
        'lock_bot': "🔒 Kilitle", 'unlock_bot': "🔓 Aç",
        'run_all': "Tümünü Çalıştır", 'ai': "🤖 AI",
        'bot_locked': "Bot kilitli. Daha sonra tekrar deneyin.",
        'file_limit_reached': "Limit doldu ({current}/{limit}).",
        'send_file': "Python (.py) veya ZIP (.zip) gönder.",
        'unsupported_type': "Sadece .py ve .zip!",
        'file_too_large': "Çok büyük (Maks: 20 MB).",
        'no_files': "Dosyan yok.",
        'your_files': "Dosyaların:", 'admin_required': "Admin gerekli.",
        'owner_required': "Sahip gerekli.", 'permission_denied': "İzin yok.",
        'file_not_found': "Bulunamadı.", 'running': "Çalışıyor", 'stopped': "Durdu",
        'start': "Başlat", 'stop': "Durdur", 'restart': "Yeniden",
        'delete': "Sil", 'logs': "Loglar", 'view_logs': "Log Gör",
        'back_to_files': "Geri", 'back_to_main': "Ana Menü",
        'starting': "Başlıyor", 'stopping': "Duruyor",
        'deleting': "Siliniyor", 'restarting': "Yeniden",
        'broadcast_prompt': "Duyuru yaz.\n/cancel iptal.",
        'broadcast_confirm': "Onayla", 'broadcast_sent': "Gönderildi!",
        'broadcast_cancelled': "İptal.", 'bot_locked_msg': "Kilitlendi.",
        'bot_unlocked_msg': "Açıldı.",
        'pending_approval': "⏳ Dosyan admin onayı bekliyor...",
        'approved': "✅ Onaylandı! Başlatılıyor...", 'rejected': "❌ Reddedildi.",
        'approve': "✅ Onayla", 'reject': "❌ Reddet",
        'new_file_approval': "🔔 YENİ DOSYA",
        'file_approved_admin': "✅ Onaylandı.", 'file_rejected_admin': "❌ Reddedildi.",
        'already_processed': "İşlendi.", 'approval_expired': "Süre doldu.",
        'no_pending': "Bekleyen yok.", 'admin_pending_list': "Bekleyenler:",
        'waiting_approval_short': "Onay Bekliyor",
    },
}
for lang in ['en', 'ru', 'ar', 'hi']:
    TRANSLATIONS[lang] = TRANSLATIONS['tr']

def t(user_id, key, **kwargs):
    lang = USER_LANG.get(user_id, 'tr')
    text = TRANSLATIONS.get(lang, TRANSLATIONS['tr']).get(key, TRANSLATIONS['tr'].get(key, key))
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        return text

# ================== AYARLAR ==================
TOKEN = os.environ.get('BOT_TOKEN', '8831078439:AAGk8yFfBfvPYujPfsfOuKsDh35gbs89iSY')
OWNER_ID = int(os.environ.get('OWNER_ID', '8947359034'))
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8947359034'))
UPDATE_CHANNEL = 'https://t.me/generalotp'
FORCED_CHANNEL = 'https://t.me/freebotHostingServer'
SUPPORT_USERNAME = '@ibenler'

A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
VENV_BASE_DIR = os.path.join(BASE_DIR, 'venvs')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

FREE_USER_LIMIT = 6
SUBSCRIBED_USER_LIMIT = 23
ADMIN_LIMIT = 99
OWNER_LIMIT = float('inf')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)
os.makedirs(VENV_BASE_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN, parse_mode=None)

bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False

pending_approvals = {}
approval_counter = [0]
approvals_lock = threading.Lock()

auto_restart_enabled = {}
file_stats = {}
file_locks = {}
file_notes = {}
APPROVAL_TTL_MINUTES = 15

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================== VERİTABANI ==================
def init_db():
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
        c.execute('''CREATE TABLE IF NOT EXISTS file_notes
                     (user_id INTEGER, file_name TEXT, note TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("DB OK.")
    except Exception as e:
        logger.error(f"DB hata: {e}", exc_info=True)

def load_data():
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for uid, exp in c.fetchall():
            try: user_subscriptions[uid] = {'expiry': datetime.fromisoformat(exp)}
            except: pass
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for uid, fn, ft in c.fetchall():
            user_files.setdefault(uid, []).append((fn, ft))
        c.execute('SELECT user_id FROM active_users')
        active_users.update(r[0] for r in c.fetchall())
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(r[0] for r in c.fetchall())
        c.execute('SELECT user_id, lang FROM user_langs')
        for uid, l in c.fetchall(): USER_LANG[uid] = l
        c.execute('SELECT user_id, file_name, note FROM file_notes')
        for uid, fn, note in c.fetchall():
            file_notes[f"{uid}_{fn}"] = note
        conn.close()
    except Exception as e:
        logger.error(f"Load hata: {e}", exc_info=True)

init_db()
load_data()

# ================== YARDIMCI ==================
def get_user_folder(user_id):
    f = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(f, exist_ok=True)
    return f

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    sk = f"{script_owner_id}_{file_name}"
    info = bot_scripts.get(sk)
    if info and info.get('process'):
        try:
            p = psutil.Process(info['process'].pid)
            alive = p.is_running() and p.status() != psutil.STATUS_ZOMBIE
            if not alive:
                if 'log_file' in info and hasattr(info['log_file'], 'close') and not info['log_file'].closed:
                    try: info['log_file'].close()
                    except: pass
                bot_scripts.pop(sk, None)
            return alive
        except psutil.NoSuchProcess:
            if 'log_file' in info and hasattr(info['log_file'], 'close') and not info['log_file'].closed:
                try: info['log_file'].close()
                except: pass
            bot_scripts.pop(sk, None)
            return False
    return False

def kill_process_tree(info):
    try:
        if 'log_file' in info and hasattr(info['log_file'], 'close') and not info['log_file'].closed:
            try: info['log_file'].close()
            except: pass
        proc = info.get('process')
        if not proc or not hasattr(proc, 'pid'): return
        try:
            parent = psutil.Process(proc.pid)
            children = parent.children(recursive=True)
            for child in children:
                try: child.terminate()
                except: pass
            gone, alive = psutil.wait_procs(children, timeout=1)
            for p in alive:
                try: p.kill()
                except: pass
            try: parent.terminate(); parent.wait(timeout=1)
            except:
                try: parent.kill()
                except: pass
        except psutil.NoSuchProcess: pass
    except Exception as e:
        logger.error(f"kill hata: {e}")

# ================== SANAL ORTAM ==================
def ensure_user_venv(user_id):
    venv_dir = os.path.join(VENV_BASE_DIR, f"venv_{user_id}")
    python_bin = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' \
                 else os.path.join(venv_dir, 'bin', 'python')

    if os.path.exists(python_bin):
        return python_bin

    logger.info(f"🛠 venv oluşturuluyor: {venv_dir}")
    try:
        os.makedirs(venv_dir, exist_ok=True)
        result = subprocess.run(
            [sys.executable, '-m', 'venv', venv_dir, '--clear'],
            capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore'
        )
        if result.returncode != 0:
            logger.error(f"venv oluşturma hatası: {result.stderr[:300]}")
            return sys.executable

        try:
            subprocess.run(
                [python_bin, '-m', 'pip', 'install', '--upgrade', 'pip', '--quiet',
                 '--disable-pip-version-check', '--no-warn-script-location'],
                capture_output=True, timeout=120
            )
        except: pass

        if os.path.exists(python_bin):
            logger.info(f"✅ venv hazır: {venv_dir}")
            return python_bin
        else:
            return sys.executable
    except Exception as e:
        logger.error(f"venv hata: {e}")
        return sys.executable

def install_in_venv(user_id, package):
    python_bin = ensure_user_venv(user_id)

    import_name = package.split('==')[0].split('>')[0].split('<')[0]
    import_map = {
        'pyTelegramBotAPI': 'telebot',
        'python-telegram-bot': 'telegram',
        'Pillow': 'PIL',
        'beautifulsoup4': 'bs4',
        'opencv-python': 'cv2',
        'PyYAML': 'yaml',
        'python-dotenv': 'dotenv',
        'python-dateutil': 'dateutil',
    }
    import_name = import_map.get(import_name, import_name.lower())

    try:
        check = subprocess.run([python_bin, '-c', f'import {import_name}'],
                              capture_output=True, timeout=10)
        if check.returncode == 0:
            return True, "Zaten kurulu"
    except: pass

    logger.info(f"📦 {package} zorla kuruluyor...")
    try:
        result = subprocess.run(
            [python_bin, '-m', 'pip', 'install', package,
             '--no-cache-dir', '--disable-pip-version-check',
             '--no-warn-script-location', '--quiet'],
            capture_output=True, text=True, timeout=300,
            encoding='utf-8', errors='ignore'
        )
        if result.returncode == 0:
            verify = subprocess.run([python_bin, '-c', f'import {import_name}'],
                                   capture_output=True, timeout=10)
            if verify.returncode == 0:
                return True, "Kuruldu"
            else:
                return False, "Kuruldu ama import edilemiyor"
        else:
            error_msg = (result.stderr or result.stdout)[-500:]
            return False, error_msg
    except subprocess.TimeoutExpired:
        return False, "Zaman aşımı"
    except Exception as e:
        return False, str(e)

# ================== SİSTEM KAYNAK ==================
def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            'cpu': cpu,
            'ram_percent': ram.percent,
            'ram_used_mb': ram.used / (1024*1024),
            'ram_total_mb': ram.total / (1024*1024),
            'disk_percent': disk.percent,
            'disk_used_gb': disk.used / (1024**3),
            'disk_total_gb': disk.total / (1024**3),
            'processes': len(psutil.pids()),
        }
    except Exception as e:
        logger.error(f"Stats hata: {e}")
        return {}

def format_stats():
    s = get_system_stats()
    if not s: return "İstatistik alınamadı."
    ec = "🟢" if s['cpu'] < 50 else "🟡" if s['cpu'] < 80 else "🔴"
    er = "🟢" if s['ram_percent'] < 60 else "🟡" if s['ram_percent'] < 85 else "🔴"
    return (
        f"💻 **SİSTEM DURUMU**\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{ec} **CPU:** `{s['cpu']:.1f}%`\n"
        f"{er} **RAM:** `{s['ram_percent']:.1f}%` "
        f"(`{s['ram_used_mb']:.0f}` / `{s['ram_total_mb']:.0f}` MB)\n"
        f"💾 **Disk:** `{s['disk_percent']:.1f}%`\n"
        f"⚙️ **Süreç:** `{s['processes']}`\n"
        f"🤖 **Bot:** `{len(bot_scripts)}`\n"
        f"━━━━━━━━━━━━━━━━"
    )

def force_reduce_resources():
    try:
        gc.collect()
        for proc in psutil.process_iter(['pid', 'status']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    try: proc.kill()
                    except: pass
            except: pass
    except Exception as e:
        logger.error(f"force_reduce: {e}")

# ================== TOKEN ==================
def extract_bot_tokens(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return list(set(re.findall(r'\b(\d{8,12}:[A-Za-z0-9_-]{35})\b', content)))
    except: return []

def enforce_bot_signature(token):
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json()
        if not r.get('ok'): return False
        uname = r['result'].get('username', 'Bot')
        try:
            requests.post(f"https://api.telegram.org/bot{token}/setMyName",
                         data={'name': f"{uname} | FREE HOSTING"[:64]}, timeout=10)
            requests.post(f"https://api.telegram.org/bot{token}/setMyDescription",
                         data={'description': f"🚀 {FORCED_CHANNEL} | {SUPPORT_USERNAME}"[:512]}, timeout=10)
        except: pass
        return True
    except: return False

# ================== SCRIPT ÇALIŞTIRMA ==================
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI', 'telegram': 'python-telegram-bot',
    'aiogram': 'aiogram', 'pyrogram': 'pyrogram', 'telethon': 'telethon',
    'telepot': 'telepot', 'tgcrypto': 'tgcrypto', 'bs4': 'beautifulsoup4',
    'requests': 'requests', 'PIL': 'Pillow', 'cv2': 'opencv-python',
    'yaml': 'PyYAML', 'dotenv': 'python-dotenv', 'dateutil': 'python-dateutil',
    'pandas': 'pandas', 'numpy': 'numpy', 'flask': 'Flask',
    'sqlalchemy': 'SQLAlchemy', 'aiohttp': 'aiohttp', 'httpx': 'httpx',
    'pymongo': 'pymongo', 'redis': 'redis', 'psutil': 'psutil',
}

def attempt_install_pip(module_name, message):
    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if package_name is None:
        return False, "Standart kütüphane"
    try:
        bot.reply_to(message, f"📦 `{module_name}` eksik, `{package_name}` kuruluyor...", parse_mode='Markdown')
        ok, detail = install_in_venv(message.from_user.id, package_name)
        if ok:
            bot.reply_to(message, f"✅ `{package_name}` başarıyla kuruldu.", parse_mode='Markdown')
        else:
            bot.reply_to(message, f"❌ `{package_name}` başarısız:\n```\n{detail[:400]}\n```", parse_mode='Markdown')
        return ok, detail
    except Exception as e:
        return False, str(e)

def run_script(script_path, owner_id, user_folder, file_name, msg_obj, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        try: bot.send_message(msg_obj.chat.id, f"❌ '{file_name}' {max_attempts} denemede çalıştırılamadı.")
        except: pass
        return
    sk = f"{owner_id}_{file_name}"

    try:
        if not os.path.exists(script_path):
            try: bot.send_message(msg_obj.chat.id, f"❌ '{file_name}' bulunamadı!")
            except: pass
            remove_user_file_db(owner_id, file_name)
            return

        if attempt == 1:
            check_proc = None
            try:
                check_proc = subprocess.Popen([sys.executable, script_path], cwd=user_folder,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              text=True, encoding='utf-8', errors='ignore')
                _, stderr = check_proc.communicate(timeout=8)
                if check_proc.returncode != 0 and stderr:
                    m = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if m:
                        mod = m.group(1).strip().strip("'\"")
                        if not mod.startswith('.'):
                            ok, _detail = attempt_install_pip(mod, msg_obj)
                            if ok:
                                threading.Thread(target=run_script,
                                    args=(script_path, owner_id, user_folder, file_name, msg_obj, attempt+1),
                                    daemon=True).start()
                                return
                            return
                    else:
                        try: bot.send_message(msg_obj.chat.id, f"❌ Hata:\n```\n{stderr[:400]}\n```", parse_mode='Markdown')
                        except: pass
                        return
            except subprocess.TimeoutExpired:
                if check_proc and check_proc.poll() is None: check_proc.kill()
            except: pass
            finally:
                if check_proc and check_proc.poll() is None:
                    try: check_proc.kill()
                    except: pass

        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        try: log_file = open(log_path, 'w', encoding='utf-8', errors='ignore')
        except Exception as e:
            try: bot.send_message(msg_obj.chat.id, f"❌ Log açılamadı: {e}")
            except: pass
            return

        try:
            env_vars = os.environ.copy()
            env_vars['FREEBOTHOST_CHANNEL'] = FORCED_CHANNEL
            env_vars['FREEBOTHOST_SUPPORT'] = SUPPORT_USERNAME

            startupinfo = None; flags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            venv_python = ensure_user_venv(owner_id)

            process = subprocess.Popen(
                [venv_python, script_path], cwd=user_folder,
                stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                startupinfo=startupinfo, creationflags=flags,
                encoding='utf-8', errors='ignore', env=env_vars
            )

            bot_scripts[sk] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': msg_obj.chat.id, 'script_owner_id': owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder,
                'type': 'py', 'script_key': sk
            }
            file_stats[sk] = file_stats.get(sk, {'restarts':0, 'crashes':0})
            file_stats[sk]['start_time'] = datetime.now()

            try:
                bot.send_message(msg_obj.chat.id,
                    f"✅ `{file_name}` başlatıldı!\n"
                    f"🆔 PID: `{process.pid}`\n"
                    f"🐍 venv: `venv_{owner_id}`",
                    parse_mode='Markdown')
            except: pass

            try:
                for tk in extract_bot_tokens(script_path):
                    threading.Thread(target=enforce_bot_signature, args=(tk,), daemon=True).start()
            except: pass

        except FileNotFoundError:
            if log_file and not log_file.closed: log_file.close()
            try: bot.send_message(msg_obj.chat.id, "❌ Python bulunamadı.")
            except: pass
            bot_scripts.pop(sk, None)
        except Exception as e:
            if log_file and not log_file.closed: log_file.close()
            try: bot.send_message(msg_obj.chat.id, f"❌ Başlatılamadı: {e}")
            except: pass
            bot_scripts.pop(sk, None)
    except Exception as e:
        logger.error(f"run_script kritik: {e}", exc_info=True)
        if sk in bot_scripts:
            kill_process_tree(bot_scripts[sk])
            bot_scripts.pop(sk, None)

# ================== DB İŞLEMLERİ ==================
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files VALUES (?, ?, ?)', (user_id, file_name, file_type))
            conn.commit()
            lst = user_files.setdefault(user_id, [])
            lst[:] = [(fn, ft) for fn, ft in lst if fn != file_name]
            lst.append((file_name, file_type))
        except Exception as e: logger.error(f"save file: {e}")
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id=? AND file_name=?', (user_id, file_name))
            c.execute('DELETE FROM file_notes WHERE user_id=? AND file_name=?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
            file_notes.pop(f"{user_id}_{file_name}", None)
        except Exception as e: logger.error(f"remove file: {e}")
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('INSERT OR IGNORE INTO active_users VALUES (?)', (user_id,))
            conn.commit()
        finally: conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('INSERT OR REPLACE INTO subscriptions VALUES (?, ?)', (user_id, expiry.isoformat()))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
        finally: conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('DELETE FROM subscriptions WHERE user_id=?', (user_id,))
            conn.commit()
            user_subscriptions.pop(user_id, None)
        finally: conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('INSERT OR IGNORE INTO admins VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id)
        finally: conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID: return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            c = conn.execute('DELETE FROM admins WHERE user_id=?', (admin_id,))
            conn.commit()
            ok = c.rowcount > 0
            if ok: admin_ids.discard(admin_id)
            return ok
        finally: conn.close()

def save_user_lang(user_id, lang):
    USER_LANG[user_id] = lang
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('INSERT OR REPLACE INTO user_langs VALUES (?, ?)', (user_id, lang))
            conn.commit()
        finally: conn.close()

def save_file_note(user_id, file_name, note):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            if note:
                conn.execute('INSERT OR REPLACE INTO file_notes VALUES (?, ?, ?)', (user_id, file_name, note))
                file_notes[f"{user_id}_{file_name}"] = note
            else:
                conn.execute('DELETE FROM file_notes WHERE user_id=? AND file_name=?', (user_id, file_name))
                file_notes.pop(f"{user_id}_{file_name}", None)
            conn.commit()
        finally: conn.close()

# ================== MENÜLER ==================
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    b = [
        types.InlineKeyboardButton(t(user_id, 'updates_channel'), url=UPDATE_CHANNEL),
        types.InlineKeyboardButton(t(user_id, 'upload_file'), callback_data='upload'),
        types.InlineKeyboardButton(t(user_id, 'check_files'), callback_data='check_files'),
        types.InlineKeyboardButton(t(user_id, 'bot_speed'), callback_data='speed'),
        types.InlineKeyboardButton(t(user_id, 'statistics'), callback_data='stats'),
        types.InlineKeyboardButton(t(user_id, 'contact_owner'),
                                    url=f'https://t.me/{SUPPORT_USERNAME.replace("@", "")}'),
        types.InlineKeyboardButton(t(user_id, 'ai'), callback_data='mpx_ai'),
        types.InlineKeyboardButton(t(user_id, 'uptime'), callback_data='uptime'),
        types.InlineKeyboardButton("💻 Sistem Durumu", callback_data='sysinfo'),
    ]
    markup.add(b[0])
    markup.add(b[1], b[2])
    markup.add(b[3], b[8])
    markup.add(b[4])
    markup.add(b[5], b[6])
    markup.add(b[7])
    if user_id in admin_ids:
        markup.row(
            types.InlineKeyboardButton(t(user_id, 'subscriptions'), callback_data='subscription'),
            types.InlineKeyboardButton(t(user_id, 'broadcast'), callback_data='broadcast')
        )
        markup.row(
            types.InlineKeyboardButton("🔒 Kilitle" if not bot_locked else "🔓 Aç",
                                       callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton(t(user_id, 'admin_panel'), callback_data='admin_panel')
        )
        markup.row(
            types.InlineKeyboardButton("▶️ Tümünü Çalıştır", callback_data='run_all_scripts'),
            types.InlineKeyboardButton("📋 Bekleyen", callback_data='pending_list')
        )
        markup.row(
            types.InlineKeyboardButton("🧹 Temizlik", callback_data='cleanup_now'),
            types.InlineKeyboardButton("🔥 CPU/RAM Düşür", callback_data='reduce_now')
        )
    return markup

def create_control_buttons(owner_id, fname, is_running=True, requester_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    rid = requester_id or owner_id
    sk = f"{owner_id}_{fname}"
    is_locked = file_locks.get(sk, False)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 " + t(rid, 'stop'), callback_data=f'stop_{owner_id}_{fname}'),
            types.InlineKeyboardButton("🔄 " + t(rid, 'restart'), callback_data=f'restart_{owner_id}_{fname}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ " + t(rid, 'delete'), callback_data=f'delete_{owner_id}_{fname}'),
            types.InlineKeyboardButton("📜 " + t(rid, 'logs'), callback_data=f'logs_{owner_id}_{fname}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 " + t(rid, 'start'), callback_data=f'start_{owner_id}_{fname}'),
            types.InlineKeyboardButton("🗑️ " + t(rid, 'delete'), callback_data=f'delete_{owner_id}_{fname}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 " + t(rid, 'view_logs'), callback_data=f'logs_{owner_id}_{fname}')
        )
    auto = "🔄✅" if auto_restart_enabled.get(sk, False) else "🔄❌"
    lock = "🔒" if is_locked else "🔓"
    markup.row(
        types.InlineKeyboardButton("📊 İstatistik", callback_data=f'stats_file_{owner_id}_{fname}'),
        types.InlineKeyboardButton(auto + " Auto", callback_data=f'toggle_autorestart_{owner_id}_{fname}')
    )
    markup.row(
        types.InlineKeyboardButton("⬇️ Log İndir", callback_data=f'dl_log_{owner_id}_{fname}'),
        types.InlineKeyboardButton(lock + " Kilit", callback_data=f'toggle_lock_{owner_id}_{fname}')
    )
    markup.row(
        types.InlineKeyboardButton("📝 Not", callback_data=f'note_{owner_id}_{fname}')
    )
    markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data='check_files'))
    return markup

def create_admin_panel(user_id):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.row(
        types.InlineKeyboardButton('➕ Admin Ekle', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Admin Sil', callback_data='remove_admin')
    )
    m.row(types.InlineKeyboardButton('📋 Admin Listesi', callback_data='list_admins'))
    m.row(
        types.InlineKeyboardButton("🧹 Temizlik", callback_data='cleanup_now'),
        types.InlineKeyboardButton("🔥 Kaynak Düşür", callback_data='reduce_now')
    )
    m.row(types.InlineKeyboardButton('🔙 Geri', callback_data='back_to_main'))
    return m

def create_subscription_menu(user_id):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.row(
        types.InlineKeyboardButton('➕ Ekle', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Sil', callback_data='remove_subscription')
    )
    m.row(types.InlineKeyboardButton('🔍 Sorgula', callback_data='check_subscription'))
    m.row(types.InlineKeyboardButton('🔙 Geri', callback_data='back_to_main'))
    return m

# ================== ONAY ==================
def request_approval(user_id, file_path, file_name, file_type, message):
    with approvals_lock:
        approval_counter[0] += 1
        aid = approval_counter[0]
        pending_approvals[aid] = {
            'user_id': user_id, 'file_path': file_path, 'file_name': file_name,
            'file_type': file_type, 'user_folder': os.path.dirname(file_path),
            'chat_id': message.chat.id, 'created_at': datetime.now(),
            'message_id': message.message_id,
        }
    uname = message.from_user.first_name
    uusername = message.from_user.username or "Yok"
    bot.reply_to(message, t(user_id, 'pending_approval'), parse_mode='Markdown')
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(t(OWNER_ID, 'approve') + f" #{aid}", callback_data=f'approve_{aid}'),
        types.InlineKeyboardButton(t(OWNER_ID, 'reject') + f" #{aid}", callback_data=f'reject_{aid}')
    )
    text = (
        f"🔔 <b>{t(OWNER_ID, 'new_file_approval')}</b>\n\n"
        f"👤 <b>{uname}</b>\n"
        f"🆔 <code>{user_id}</code>\n"
        f"📛 @{uusername}\n"
        f"📄 <code>{file_name}</code>\n"
        f"📦 <b>{file_type.upper()}</b>\n"
        f"🔢 Onay: <b>#{aid}</b>\n"
        f"⏱ {APPROVAL_TTL_MINUTES} dk\n\n"
        f"Onaylıyor musun?"
    )
    for adm in list(admin_ids):
        try:
            try:
                with open(file_path, 'rb') as f:
                    bot.send_document(adm, f, caption=text, reply_markup=markup, parse_mode='HTML')
            except:
                bot.send_message(adm, text, reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            logger.error(f"approval {adm}: {e}")

def handle_approve(call):
    try: aid = int(call.data.split('_')[1])
    except: bot.answer_callback_query(call.id, "Geçersiz."); return
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'admin_required'), show_alert=True); return
    with approvals_lock:
        info = pending_approvals.pop(aid, None)
        if not info:
            bot.answer_callback_query(call.id, "İşlendi.", show_alert=True); return
    bot.answer_callback_query(call.id, "✅ Onaylandı!")
    uid = info['user_id']; fp = info['file_path']; fn = info['file_name']
    ft = info['file_type']; uf = info['user_folder']; uchat = info['chat_id']
    try:
        bot.edit_message_caption(
            caption=f"✅ <b>ONAYLANDI</b> - <code>{fn}</code> | User: <code>{uid}</code>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
    except:
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except: pass
    try:
        bot.send_message(uchat, t(uid, 'approved'))
    except: pass
    save_user_file(uid, fn, ft)
    class FM:
        def __init__(s, c): s.chat = type('obj', (object,), {'id': c})()
    threading.Thread(target=run_script, args=(fp, uid, uf, fn, FM(uchat)), daemon=True).start()

def handle_reject(call):
    try: aid = int(call.data.split('_')[1])
    except: bot.answer_callback_query(call.id, "Geçersiz."); return
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'admin_required'), show_alert=True); return
    with approvals_lock:
        info = pending_approvals.pop(aid, None)
        if not info:
            bot.answer_callback_query(call.id, "İşlendi."); return
    bot.answer_callback_query(call.id, "❌ Reddedildi.")
    uid = info['user_id']; fp = info['file_path']; fn = info['file_name']; uchat = info['chat_id']
    try:
        if os.path.exists(fp): os.remove(fp)
    except: pass
    remove_user_file_db(uid, fn)
    try:
        bot.edit_message_caption(
            caption=f"❌ <b>REDDEDİLDİ</b> - <code>{fn}</code> | User: <code>{uid}</code>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
    except:
        try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except: pass
    try:
        bot.send_message(uchat, t(uid, 'rejected'))
    except: pass

# ================== WORKER'LAR ==================
def approval_cleanup_worker():
    while True:
        try:
            now = datetime.now()
            expired = []
            with approvals_lock:
                for aid, info in list(pending_approvals.items()):
                    if (now - info['created_at']).total_seconds()/60 >= APPROVAL_TTL_MINUTES:
                        expired.append(aid)
            for aid in expired:
                with approvals_lock:
                    info = pending_approvals.pop(aid, None)
                if not info: continue
                try:
                    if os.path.exists(info['file_path']): os.remove(info['file_path'])
                    try: bot.send_message(info['chat_id'], f"⏰ Onay süresi doldu: `{info['file_name']}`", parse_mode='Markdown')
                    except: pass
                except Exception as e: logger.error(f"TTL: {e}")
        except Exception as e: logger.error(f"cleanup_worker: {e}")
        time.sleep(60)

def watchdog_worker():
    while True:
        try:
            time.sleep(30)
            for sk, info in list(bot_scripts.items()):
                try:
                    proc = info.get('process')
                    if not proc: continue
                    if proc.poll() is not None:
                        oid = info.get('script_owner_id'); fn = info.get('file_name')
                        file_stats.setdefault(sk, {'restarts':0, 'crashes':0})
                        file_stats[sk]['crashes'] += 1
                        if 'log_file' in info and hasattr(info['log_file'], 'close') and not info['log_file'].closed:
                            try: info['log_file'].close()
                            except: pass
                        bot_scripts.pop(sk, None)
                        if auto_restart_enabled.get(sk, False):
                            fp = os.path.join(info.get('user_folder',''), fn)
                            if os.path.exists(fp):
                                file_stats[sk]['restarts'] += 1
                                class FM:
                                    def __init__(s, c): s.chat = type('obj', (object,), {'id': c})()
                                threading.Thread(target=run_script,
                                    args=(fp, oid, info['user_folder'], fn, FM(info.get('chat_id', oid))),
                                    daemon=True).start()
                except Exception as e: logger.error(f"watchdog {sk}: {e}")
        except Exception as e: logger.error(f"watchdog: {e}")

# ================== GİRİŞ MESAJI (YENİ) ==================
def _logic_send_welcome(message):
    uid = message.from_user.id
    cid = message.chat.id
    if bot_locked and uid not in admin_ids:
        bot.send_message(cid, t(uid, 'bot_locked')); return
    if uid not in active_users:
        add_active_user(uid)
        try:
            bot.send_message(OWNER_ID,
                f"🆕 **Yeni Kullanıcı**\nAd: {message.from_user.first_name}\n"
                f"ID: `{uid}`\n@{message.from_user.username or 'Yok'}",
                parse_mode='Markdown')
        except: pass
    fl = get_user_file_limit(uid)
    cf = get_user_file_count(uid)
    ls = str(fl) if fl != float('inf') else "Sınırsız"
    if uid == OWNER_ID: st = "👑 Sahip"
    elif uid in admin_ids: st = "🛡 Admin"
    elif uid in user_subscriptions and user_subscriptions[uid].get('expiry', datetime.min) > datetime.now():
        st = "💎 Premium"
    else: st = "🆓 Ücretsiz"

    # YENİ GİRİŞ MESAJI
    welcome = (
        f"🌟 **MERHABA BEN HOSTING SERVER** 🌟\n\n"
        f"Nasıl yardımcı olabilirim? 👋\n\n"
        f"Aşağıdaki butonlardan seçim yapabilirsiniz. "
        f"Bot yüklemek, dosya kontrolü, istatistikler ve daha fazlası için menüyü kullanın.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **ID:** `{uid}`\n"
        f"📛 **Kullanıcı:** @{message.from_user.username or 'Yok'}\n"
        f"🎖️ **Durum:** {st}\n"
        f"📁 **Dosyalar:** {cf} / {ls}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📢 **Kanal:** {FORCED_CHANNEL}\n"
        f"💬 **Destek:** {SUPPORT_USERNAME}\n\n"
        f"⚠️ Tüm `.py` dosyaları **admin onayı** sonrası çalışır.\n"
        f"🐍 Her bot **kendi sanal ortamında** çalışır."
    )
    try:
        bot.send_message(cid, welcome, reply_markup=create_main_menu_inline(uid), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"welcome: {e}")

def _logic_check_files(message):
    uid = message.from_user.id
    if not user_files.get(uid):
        bot.reply_to(message, "📂 Henüz hiç dosya yüklemediniz."); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for fn, ft in sorted(user_files[uid]):
        is_run = is_bot_running(uid, fn)
        pending = any(i['user_id'] == uid and i['file_name'] == fn for i in pending_approvals.values())
        if pending: icon = "⏳"
        else: icon = "🟢" if is_run else "🔴"
        markup.add(types.InlineKeyboardButton(f"{icon} {fn} ({ft})", callback_data=f'file_{uid}_{fn}'))
    bot.reply_to(message, "📂 **Dosyalarınız:**", reply_markup=markup, parse_mode='Markdown')

def _logic_uptime(message):
    u = datetime.now() - BOT_START_TIME
    d = u.days; h, r = divmod(u.seconds, 3600); m, s = divmod(r, 60)
    bot.reply_to(message, f"⏱ `{d}g {h}s {m}d {s}sn`", parse_mode='Markdown')

def _logic_statistics(message):
    uid = message.from_user.id
    tu = len(active_users)
    tf = sum(len(f) for f in user_files.values())
    rb = sum(1 for k, i in bot_scripts.items() if is_bot_running(i.get('script_owner_id'), i.get('file_name')))
    my = sum(1 for k, i in bot_scripts.items() if i.get('script_owner_id') == uid and is_bot_running(i.get('script_owner_id'), i.get('file_name')))
    s = get_system_stats()
    txt = (
        f"📊 **İSTATİSTİKLER**\n"
        f"👥 Kullanıcı: `{tu}`\n"
        f"📁 Dosya: `{tf}`\n"
        f"🤖 Aktif: `{rb}`\n"
        f"👤 Senin: `{my}`\n"
        f"💻 CPU: `{s.get('cpu', 0):.1f}%` | RAM: `{s.get('ram_percent', 0):.1f}%`"
    )
    bot.reply_to(message, txt, parse_mode='Markdown')

@bot.message_handler(commands=['start', 'help'])
def cmd_start(m): _logic_send_welcome(m)

@bot.message_handler(commands=['files'])
def cmd_files(m): _logic_check_files(m)

@bot.message_handler(commands=['stats'])
def cmd_stats(m): _logic_statistics(m)

@bot.message_handler(commands=['uptime'])
def cmd_uptime(m): _logic_uptime(m)

@bot.message_handler(commands=['sysinfo'])
def cmd_sysinfo(m):
    bot.reply_to(m, format_stats(), parse_mode='Markdown')

@bot.message_handler(commands=['cleanup'])
def cmd_cleanup(m):
    if m.from_user.id not in admin_ids:
        bot.reply_to(m, "Admin gerekli."); return
    gc.collect()
    bot.reply_to(m, "✅ Temizlik tamam.")

@bot.message_handler(commands=['reduce'])
def cmd_reduce(m):
    if m.from_user.id not in admin_ids:
        bot.reply_to(m, "Admin gerekli."); return
    force_reduce_resources()
    s = get_system_stats()
    bot.reply_to(m, f"🔥 CPU: `{s.get('cpu', 0):.1f}%` | RAM: `{s.get('ram_percent', 0):.1f}%`", parse_mode='Markdown')

@bot.message_handler(commands=['mpx'])
def cmd_mpx(m):
    if not m.text or len(m.text.split()) < 2:
        bot.reply_to(m, "Kullanım: `/mpx sorunuz`", parse_mode='Markdown'); return
    q = m.text.split(' ', 1)[1]
    bot.send_chat_action(m.chat.id, 'typing')
    try:
        r = requests.post(A4F_API_URL,
            headers={"Authorization": f"Bearer {A4F_API_KEY}", "Content-Type": "application/json"},
            json={"model": A4F_MODEL, "messages": [{"role": "user", "content": q}], "temperature": 0.7},
            timeout=60).json()
        ans = r.get('choices', [{}])[0].get('message', {}).get('content', 'Yanıt yok')
        bot.reply_to(m, ans[:4000], parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(m, f"API hata: {e}")

# ================== DOSYA YÜKLEME ==================
@bot.message_handler(content_types=['document'])
def handle_doc(message):
    uid = message.from_user.id
    cid = message.chat.id
    if bot_locked and uid not in admin_ids:
        bot.reply_to(message, t(uid, 'bot_locked')); return
    fl = get_user_file_limit(uid); cf = get_user_file_count(uid)
    if cf >= fl:
        bot.reply_to(message, f"❌ Limit dolu ({cf}/{fl})."); return
    doc = message.document
    fn = doc.file_name
    if not fn: bot.reply_to(message, "Dosya adı yok."); return
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ['.py', '.zip']:
        bot.reply_to(message, t(uid, 'unsupported_type')); return
    if doc.file_size > 20*1024*1024:
        bot.reply_to(message, t(uid, 'file_too_large')); return
    try:
        try: bot.forward_message(OWNER_ID, cid, message.message_id)
        except: pass
        wm = bot.reply_to(message, f"📥 `{fn}` indiriliyor...")
        fi = bot.get_file(doc.file_id)
        content = bot.download_file(fi.file_path)
        bot.edit_message_text(f"✅ `{fn}` indirildi. İşleniyor...", cid, wm.message_id)
        uf = get_user_folder(uid)
        if ext == '.zip':
            handle_zip_file(content, fn, message)
        else:
            fp = os.path.join(uf, fn)
            with open(fp, 'wb') as f: f.write(content)
            request_approval(uid, fp, fn, 'py', message)
    except Exception as e:
        logger.error(f"doc: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Hata: {e}")

def handle_zip_file(content, fname, message):
    uid = message.from_user.id
    ufolder = get_user_folder(uid)
    tmp = None
    try:
        tmp = tempfile.mkdtemp(prefix=f"user_{uid}_zip_")
        zp = os.path.join(tmp, fname)
        with open(zp, 'wb') as f: f.write(content)
        with zipfile.ZipFile(zp, 'r') as z:
            for m in z.infolist():
                if not os.path.abspath(os.path.join(tmp, m.filename)).startswith(os.path.abspath(tmp) + os.sep):
                    raise zipfile.BadZipFile("Güvenlik: yolu kötü")
            z.extractall(tmp)
        items = os.listdir(tmp)
        pyf = [x for x in items if x.endswith('.py')]
        main = None
        for p in ['main.py', 'bot.py', 'app.py']:
            if p in pyf: main = p; break
        if not main and pyf: main = pyf[0]
        if not main:
            bot.reply_to(message, "❌ `.py` yok!"); return
        for x in items:
            src = os.path.join(tmp, x); dst = os.path.join(ufolder, x)
            if os.path.isdir(dst): shutil.rmtree(dst)
            elif os.path.exists(dst): os.remove(dst)
            shutil.move(src, dst)
        bot.reply_to(message, f"📦 Arşiv açıldı. Ana: `{main}`\n⏳ Admin onayına gönderiliyor...", parse_mode='Markdown')
        request_approval(uid, os.path.join(ufolder, main), main, 'py', message)
    except zipfile.BadZipFile as e:
        bot.reply_to(message, f"❌ Bozuk ZIP: {e}")
    except Exception as e:
        logger.error(f"zip: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Hata: {e}")
    finally:
        if tmp and os.path.exists(tmp): shutil.rmtree(tmp, ignore_errors=True)

# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid = call.from_user.id
    d = call.data
    if bot_locked and uid not in admin_ids and not (d.startswith('approve_') or d.startswith('reject_')):
        bot.answer_callback_query(call.id, t(uid, 'bot_locked'), show_alert=True); return
    try:
        if d == 'upload': cb_upload(call)
        elif d == 'check_files': cb_files(call)
        elif d.startswith('file_'): cb_file_ctl(call)
        elif d.startswith('start_'): cb_start(call)
        elif d.startswith('stop_'): cb_stop(call)
        elif d.startswith('restart_'): cb_restart(call)
        elif d.startswith('delete_'): cb_delete(call)
        elif d.startswith('logs_'): cb_logs(call)
        elif d == 'speed':
            bot.answer_callback_query(call.id)
            s = get_system_stats()
            bot.send_message(call.message.chat.id,
                f"⚡ CPU: `{s.get('cpu',0):.1f}%` | RAM: `{s.get('ram_percent',0):.1f}%`",
                parse_mode='Markdown')
        elif d == 'back_to_main': cb_back_main(call)
        elif d.startswith('approve_'): handle_approve(call)
        elif d.startswith('reject_'): handle_reject(call)
        elif d == 'pending_list':
            if uid in admin_ids: cb_pending(call)
        elif d.startswith('confirm_broadcast_'): cb_confirm_broadcast(call)
        elif d == 'cancel_broadcast': cb_cancel_broadcast(call)
        elif d == 'subscription':
            if uid in admin_ids: cb_subs(call)
        elif d == 'stats': _logic_statistics(call.message)
        elif d == 'lock_bot':
            if uid in admin_ids: cb_lock(call)
        elif d == 'unlock_bot':
            if uid in admin_ids: cb_unlock(call)
        elif d == 'run_all_scripts':
            if uid in admin_ids: cb_run_all(call)
        elif d == 'broadcast':
            if uid in admin_ids: cb_broadcast(call)
        elif d == 'admin_panel':
            if uid in admin_ids: cb_admin_panel(call)
        elif d == 'add_admin':
            if uid == OWNER_ID: cb_add_admin(call)
        elif d == 'remove_admin':
            if uid == OWNER_ID: cb_remove_admin(call)
        elif d == 'list_admins':
            if uid in admin_ids: cb_list_admins(call)
        elif d == 'add_subscription':
            if uid in admin_ids: cb_add_sub(call)
        elif d == 'remove_subscription':
            if uid in admin_ids: cb_remove_sub(call)
        elif d == 'check_subscription':
            if uid in admin_ids: cb_check_sub(call)
        elif d == 'mpx_ai':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "🤖 `/mpx <soru>` kullanın.", parse_mode='Markdown')
        elif d == 'uptime':
            u = datetime.now() - BOT_START_TIME
            dd = u.days; h, r = divmod(u.seconds, 3600); m, s = divmod(r, 60)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"⏱ `{dd}g {h}s {m}d {s}sn`", parse_mode='Markdown')
        elif d == 'sysinfo':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, format_stats(), parse_mode='Markdown')
        elif d == 'cleanup_now':
            if uid in admin_ids:
                bot.answer_callback_query(call.id, "Temizlik...")
                gc.collect()
                bot.send_message(call.message.chat.id, "🧹 Tamam!")
        elif d == 'reduce_now':
            if uid in admin_ids:
                bot.answer_callback_query(call.id, "Düşürülüyor...")
                force_reduce_resources()
                s = get_system_stats()
                bot.send_message(call.message.chat.id,
                    f"🔥 CPU: `{s.get('cpu',0):.1f}%` | RAM: `{s.get('ram_percent',0):.1f}%`",
                    parse_mode='Markdown')
        elif d.startswith('toggle_autorestart_'): cb_toggle_auto(call)
        elif d.startswith('stats_file_'): cb_file_stats(call)
        elif d.startswith('dl_log_'): cb_dl_log(call)
        elif d.startswith('toggle_lock_'): cb_toggle_lock(call)
        elif d.startswith('note_'): cb_note(call)
        else:
            bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"CB hata '{d}': {e}", exc_info=True)
        try: bot.answer_callback_query(call.id, "Hata.", show_alert=True)
        except: pass

def cb_upload(call):
    uid = call.from_user.id
    fl = get_user_file_limit(uid); cf = get_user_file_count(uid)
    if cf >= fl:
        bot.answer_callback_query(call.id, f"Limit dolu ({cf}/{fl})", show_alert=True); return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📤 Bir `.py` veya `.zip` dosyası gönderin.", parse_mode='Markdown')

def cb_files(call):
    uid = call.from_user.id
    if not user_files.get(uid):
        bot.answer_callback_query(call.id, "Dosyanız yok.", show_alert=True); return
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for fn, ft in sorted(user_files[uid]):
        is_run = is_bot_running(uid, fn)
        pending = any(i['user_id'] == uid and i['file_name'] == fn for i in pending_approvals.values())
        if pending: icon = "⏳"
        else: icon = "🟢" if is_run else "🔴"
        markup.add(types.InlineKeyboardButton(f"{icon} {fn} ({ft})", callback_data=f'file_{uid}_{fn}'))
    markup.add(types.InlineKeyboardButton("🔙 Ana Menü", callback_data='back_to_main'))
    try:
        bot.edit_message_text("📂 **Dosyalarınız:**", call.message.chat.id,
            call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    except: pass

def cb_file_ctl(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        if not any(f[0] == fn for f in user_files.get(oid, [])):
            bot.answer_callback_query(call.id, "Bulunamadı.", show_alert=True); return
        bot.answer_callback_query(call.id)
        is_run = is_bot_running(oid, fn)
        pending = any(i['user_id'] == oid and i['file_name'] == fn for i in pending_approvals.values())
        if pending:
            status = "⏳ Onay Bekliyor"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🗑️ Sil", callback_data=f'delete_{oid}_{fn}'))
            markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data='check_files'))
        else:
            status = "🟢 Çalışıyor" if is_run else "🔴 Durdu"
            markup = create_control_buttons(oid, fn, is_run, rid)
        try:
            bot.edit_message_text(
                f"🎛 **Kontrol**\n📄 `{fn}`\n👤 `{oid}`\n📊 {status}",
                call.message.chat.id, call.message.message_id,
                reply_markup=markup, parse_mode='Markdown')
        except: pass
    except Exception as e:
        logger.error(f"file_ctl: {e}")

def cb_start(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        if any(i['user_id'] == oid and i['file_name'] == fn for i in pending_approvals.values()):
            bot.answer_callback_query(call.id, "Onay bekliyor.", show_alert=True); return
        uf = get_user_folder(oid); fp = os.path.join(uf, fn)
        if not os.path.exists(fp):
            bot.answer_callback_query(call.id, "Kayıp.", show_alert=True); return
        if is_bot_running(oid, fn):
            bot.answer_callback_query(call.id, "Zaten çalışıyor.", show_alert=True); return
        bot.answer_callback_query(call.id, "Başlatılıyor...")
        threading.Thread(target=run_script, args=(fp, oid, uf, fn, call.message), daemon=True).start()
        time.sleep(1.5)
        is_run = is_bot_running(oid, fn)
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(oid, fn, is_run, rid))
        except: pass
    except Exception as e: logger.error(f"start: {e}")

def cb_stop(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        sk = f"{oid}_{fn}"
        if not is_bot_running(oid, fn):
            bot.answer_callback_query(call.id, "Zaten durdu.", show_alert=True); return
        bot.answer_callback_query(call.id, "Durduruluyor...")
        if sk in bot_scripts:
            kill_process_tree(bot_scripts[sk]); del bot_scripts[sk]
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(oid, fn, False, rid))
        except: pass
    except Exception as e: logger.error(f"stop: {e}")

def cb_restart(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        uf = get_user_folder(oid); fp = os.path.join(uf, fn)
        if not os.path.exists(fp):
            bot.answer_callback_query(call.id, "Kayıp.", show_alert=True); return
        bot.answer_callback_query(call.id, "Yeniden...")
        sk = f"{oid}_{fn}"
        if sk in bot_scripts:
            kill_process_tree(bot_scripts[sk]); del bot_scripts[sk]
            time.sleep(1)
        threading.Thread(target=run_script, args=(fp, oid, uf, fn, call.message), daemon=True).start()
        time.sleep(1.5)
        is_run = is_bot_running(oid, fn)
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(oid, fn, is_run, rid))
        except: pass
    except Exception as e: logger.error(f"restart: {e}")

def cb_delete(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        bot.answer_callback_query(call.id, "Siliniyor...")
        sk = f"{oid}_{fn}"
        if sk in bot_scripts:
            kill_process_tree(bot_scripts[sk]); del bot_scripts[sk]
            time.sleep(0.5)
        uf = get_user_folder(oid)
        fp = os.path.join(uf, fn)
        lp = os.path.join(uf, f"{os.path.splitext(fn)[0]}.log")
        for p in [fp, lp]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass
        remove_user_file_db(oid, fn)
        try:
            bot.edit_message_text(f"✅ `{fn}` silindi.", call.message.chat.id,
                call.message.message_id, reply_markup=None, parse_mode='Markdown')
        except: pass
    except Exception as e: logger.error(f"delete: {e}")

def cb_logs(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        uf = get_user_folder(oid)
        lp = os.path.join(uf, f"{os.path.splitext(fn)[0]}.log")
        if not os.path.exists(lp):
            bot.answer_callback_query(call.id, "Log yok.", show_alert=True); return
        bot.answer_callback_query(call.id)
        size = os.path.getsize(lp)
        if size > 100*1024:
            with open(lp, 'rb') as f:
                f.seek(-100*1024, os.SEEK_END)
                content = f.read().decode('utf-8', errors='ignore')
            content = f"(son 100KB)\n...\n" + content
        else:
            with open(lp, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
        if not content.strip(): content = "(boş)"
        if len(content) > 4000: content = content[-4000:]
        bot.send_message(call.message.chat.id, f"📜 `{fn}`\n```\n{content}\n```", parse_mode='Markdown')
    except Exception as e: logger.error(f"logs: {e}")

def cb_back_main(call):
    uid = call.from_user.id
    fl = get_user_file_limit(uid); cf = get_user_file_count(uid)
    ls = str(fl) if fl != float('inf') else "Sınırsız"
    txt = (
        f"🌟 **MERHABA BEN HOSTING SERVER** 🌟\n\n"
        f"Nasıl yardımcı olabilirim? 👋\n\n"
        f"Aşağıdaki butonlardan seçim yapabilirsiniz.\n\n"
        f"👤 ID: `{uid}`\n📁 Dosya: `{cf}/{ls}`\n"
        f"📢 {FORCED_CHANNEL}\n💬 {SUPPORT_USERNAME}"
    )
    try:
        bot.answer_callback_query(call.id)
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
            reply_markup=create_main_menu_inline(uid), parse_mode='Markdown')
    except: pass

def cb_pending(call):
    if not pending_approvals:
        bot.answer_callback_query(call.id, "Bekleyen yok.", show_alert=True); return
    bot.answer_callback_query(call.id)
    for aid, info in list(pending_approvals.items()):
        m = types.InlineKeyboardMarkup()
        m.row(
            types.InlineKeyboardButton(f"✅ #{aid}", callback_data=f'approve_{aid}'),
            types.InlineKeyboardButton(f"❌ #{aid}", callback_data=f'reject_{aid}')
        )
        try:
            bot.send_message(call.message.chat.id,
                f"#{aid} - `{info['file_name']}` (User: `{info['user_id']}`)",
                reply_markup=m, parse_mode='Markdown')
        except: pass

def cb_lock(call):
    global bot_locked; bot_locked = True
    bot.answer_callback_query(call.id, "🔒 Kilitlendi.")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
            reply_markup=create_main_menu_inline(call.from_user.id))
    except: pass

def cb_unlock(call):
    global bot_locked; bot_locked = False
    bot.answer_callback_query(call.id, "🔓 Açıldı.")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
            reply_markup=create_main_menu_inline(call.from_user.id))
    except: pass

def cb_run_all(call):
    bot.answer_callback_query(call.id, "Başlatılıyor...")
    count = 0
    for uid, files in dict(user_files).items():
        uf = get_user_folder(uid)
        for fn, ft in files:
            if ft != 'py': continue
            if is_bot_running(uid, fn): continue
            if any(i['user_id'] == uid and i['file_name'] == fn for i in pending_approvals.values()): continue
            fp = os.path.join(uf, fn)
            if os.path.exists(fp):
                threading.Thread(target=run_script, args=(fp, uid, uf, fn, call.message), daemon=True).start()
                count += 1
                time.sleep(0.7)
    bot.send_message(call.message.chat.id, f"✅ {count} bot başlatıldı.")

def cb_broadcast(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📢 Duyuru yaz.\n/cancel iptal.")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(m):
    uid = m.from_user.id
    if uid not in admin_ids: return
    if m.text and m.text.lower() == '/cancel':
        bot.reply_to(m, "İptal."); return
    target = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Onayla", callback_data=f"confirm_broadcast_{m.message_id}"),
        types.InlineKeyboardButton("❌ İptal", callback_data="cancel_broadcast")
    )
    preview = (m.text or "(medya)")[:1000]
    bot.reply_to(m, f"📢 **Onay?**\n\n```\n{preview}\n```\n\n**{target}** kişiye.",
                 reply_markup=markup, parse_mode='Markdown')

def cb_confirm_broadcast(call):
    if call.from_user.id not in admin_ids: return
    try:
        orig = call.message.reply_to_message
        if not orig: raise ValueError("Orijinal yok.")
        text = orig.text
        bot.answer_callback_query(call.id, "Başladı...")
        bot.edit_message_text(f"{len(active_users)} kişiye...", call.message.chat.id,
            call.message.message_id, reply_markup=None)
        threading.Thread(target=do_broadcast, args=(text, call.message.chat.id), daemon=True).start()
    except Exception as e:
        bot.answer_callback_query(call.id, f"Hata: {e}", show_alert=True)

def cb_cancel_broadcast(call):
    bot.answer_callback_query(call.id, "İptal.")
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

def do_broadcast(text, admin_chat):
    sent = 0; failed = 0; blocked = 0
    for i, uid in enumerate(list(active_users)):
        try:
            bot.send_message(uid, text, parse_mode='Markdown')
            sent += 1
        except telebot.apihelper.ApiTelegramException as e:
            err = str(e).lower()
            if any(s in err for s in ["bot was blocked", "chat not found", "deactivated"]):
                blocked += 1
            else: failed += 1
        except: failed += 1
        if (i+1) % 25 == 0: time.sleep(1.5)
        else: time.sleep(0.05)
    bot.send_message(admin_chat, f"✅ {sent} | ❌ {failed} | 🚫 {blocked}")

def cb_subs(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("💳 Abonelik", call.message.chat.id, call.message.message_id,
        reply_markup=create_subscription_menu(call.from_user.id))

def cb_admin_panel(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("👑 Admin", call.message.chat.id, call.message.message_id,
        reply_markup=create_admin_panel(call.from_user.id))

def cb_add_admin(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Admin ID gir.\n/cancel")
    bot.register_next_step_handler(msg, process_add_admin)

def process_add_admin(m):
    if m.from_user.id != OWNER_ID: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        nid = int(m.text.strip())
        if nid in admin_ids: bot.reply_to(m, "Zaten."); return
        add_admin_db(nid)
        bot.reply_to(m, f"✅ `{nid}` admin.", parse_mode='Markdown')
    except: bot.reply_to(m, "Geçersiz.")

def cb_remove_admin(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Admin ID sil.\n/cancel")
    bot.register_next_step_handler(msg, process_remove_admin)

def process_remove_admin(m):
    if m.from_user.id != OWNER_ID: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        nid = int(m.text.strip())
        if remove_admin_db(nid): bot.reply_to(m, f"✅ `{nid}` silindi.", parse_mode='Markdown')
        else: bot.reply_to(m, f"Silinemedi.")
    except: bot.reply_to(m, "Geçersiz.")

def cb_list_admins(call):
    bot.answer_callback_query(call.id)
    lst = "\n".join(f"- `{a}` {'(Sahip)' if a == OWNER_ID else ''}" for a in sorted(admin_ids))
    bot.edit_message_text(f"👑 **Adminler:**\n\n{lst}", call.message.chat.id,
        call.message.message_id, reply_markup=create_admin_panel(call.from_user.id), parse_mode='Markdown')

def cb_add_sub(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Format: `ID gün`\n/cancel", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_add_sub)

def process_add_sub(m):
    if m.from_user.id not in admin_ids: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        p = m.text.split()
        if len(p) != 2: raise ValueError()
        uid = int(p[0]); days = int(p[1])
        cur = user_subscriptions.get(uid, {}).get('expiry')
        start = max(datetime.now(), cur) if cur else datetime.now()
        new_exp = start + timedelta(days=days)
        save_subscription(uid, new_exp)
        bot.reply_to(m, f"✅ `{uid}` +{days}g -> {new_exp:%Y-%m-%d}", parse_mode='Markdown')
    except: bot.reply_to(m, "Geçersiz.")

def cb_remove_sub(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Sil ID.\n/cancel")
    bot.register_next_step_handler(msg, process_remove_sub)

def process_remove_sub(m):
    if m.from_user.id not in admin_ids: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        uid = int(m.text.strip())
        if uid not in user_subscriptions: bot.reply_to(m, "Yok."); return
        remove_subscription_db(uid)
        bot.reply_to(m, f"✅ silindi.", parse_mode='Markdown')
    except: bot.reply_to(m, "Geçersiz.")

def cb_check_sub(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "ID gir.\n/cancel")
    bot.register_next_step_handler(msg, process_check_sub)

def process_check_sub(m):
    if m.from_user.id not in admin_ids: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        uid = int(m.text.strip())
        if uid in user_subscriptions:
            exp = user_subscriptions[uid].get('expiry')
            if exp and exp > datetime.now():
                bot.reply_to(m, f"✅ {exp:%Y-%m-%d}", parse_mode='Markdown')
            else:
                bot.reply_to(m, "⚠️ Dolmuş."); remove_subscription_db(uid)
        else: bot.reply_to(m, "Yok.")
    except: bot.reply_to(m, "Geçersiz.")

def cb_toggle_auto(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        sk = f"{oid}_{fn}"
        auto_restart_enabled[sk] = not auto_restart_enabled.get(sk, False)
        state = "AÇIK" if auto_restart_enabled[sk] else "KAPALI"
        bot.answer_callback_query(call.id, f"Auto: {state}")
        is_run = is_bot_running(oid, fn)
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(oid, fn, is_run, rid))
        except: pass
    except Exception as e: logger.error(f"auto: {e}")

def cb_file_stats(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        sk = f"{oid}_{fn}"
        st = file_stats.get(sk, {'restarts':0, 'crashes':0})
        is_run = is_bot_running(oid, fn)
        up = "—"
        if st.get('start_time') and is_run:
            d = datetime.now() - st['start_time']
            h, r = divmod(d.seconds, 3600); mn, s = divmod(r, 60)
            up = f"{d.days}g {h}s {mn}d {s}sn"
        auto = "✅" if auto_restart_enabled.get(sk, False) else "❌"
        lock = "🔒" if file_locks.get(sk, False) else "🔓"
        msg = (f"📊 `{fn}`\n"
               f"👤 `{oid}`\n"
               f"🔌 {'🟢' if is_run else '🔴'}\n"
               f"⏱ `{up}`\n"
               f"🔄 {auto} | {lock}\n"
               f"↻ `{st.get('restarts', 0)}`\n"
               f"💥 `{st.get('crashes', 0)}`")
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
    except Exception as e: logger.error(f"stats: {e}")

def cb_dl_log(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        lp = os.path.join(get_user_folder(oid), f"{os.path.splitext(fn)[0]}.log")
        if not os.path.exists(lp):
            bot.answer_callback_query(call.id, "Log yok.", show_alert=True); return
        with open(lp, 'rb') as f:
            bot.send_document(call.message.chat.id, f,
                caption=f"📜 `{fn}`", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Gönderildi.")
    except Exception as e: logger.error(f"dl_log: {e}")

def cb_toggle_lock(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        sk = f"{oid}_{fn}"
        file_locks[sk] = not file_locks.get(sk, False)
        state = "🔒" if file_locks[sk] else "🔓"
        bot.answer_callback_query(call.id, state)
        is_run = is_bot_running(oid, fn)
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(oid, fn, is_run, rid))
        except: pass
    except Exception as e: logger.error(f"lock: {e}")

def cb_note(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        bot.answer_callback_query(call.id)
        cur = file_notes.get(f"{oid}_{fn}", "")
        msg = bot.send_message(call.message.chat.id,
            f"📝 `{fn}` not:\n\nMevcut: {cur or '(yok)'}\n\nSil: `sil`\n/cancel",
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_note, oid, fn)
    except Exception as e: logger.error(f"note: {e}")

def process_note(m, oid, fn):
    if m.from_user.id != oid and m.from_user.id not in admin_ids: return
    if m.text and m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    note = m.text.strip() if m.text else ""
    if note.lower() == 'sil': note = ""
    save_file_note(oid, fn, note[:500])
    bot.reply_to(m, "✅ Not kaydedildi." if note else "✅ Silindi.")

# ================== CLEANUP ==================
def cleanup_all():
    logger.warning("Kapanış - süreçler temizleniyor...")
    for sk in list(bot_scripts.keys()):
        if sk in bot_scripts:
            try: kill_process_tree(bot_scripts[sk])
            except: pass

atexit.register(cleanup_all)

# ================== MAIN ==================
if __name__ == '__main__':
    logger.info("="*50)
    logger.info("🚀 BOT BAŞLATILIYOR")
    logger.info(f"👑 Sahip: {OWNER_ID}")
    logger.info(f"📢 Kanal: {FORCED_CHANNEL}")
    logger.info("="*50)

    keep_alive()

    threading.Thread(target=approval_cleanup_worker, daemon=True).start()
    threading.Thread(target=watchdog_worker, daemon=True).start()

    while True:
        try:
            bot.infinity_polling(logger_level=logging.WARNING, timeout=60,
                                 long_polling_timeout=30, skip_pending=True)
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            time.sleep(15)
        except Exception as e:
            logger.critical(f"Polling: {e}", exc_info=True)
            time.sleep(30)
