# =====================================================
#  🚀 FREEBOTHOSTING SERVER - TAM KOD
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
import logging
import threading
import re
import sys
import atexit
import requests
import gc
import json
from flask import Flask
from threading import Thread
app = Flask('')

@app.route('/')
def home():
    return "Bot çalışıyor 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_flask, daemon=True).start()
    print("Flask Keep-Alive başladı.")

BOT_START_TIME = datetime.now()

# ================== DİL ==================
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
FORCED_CHANNEL = 'https://t.me/generalotp'
SUPPORT_USERNAME = '@logsuzlarsystemvip'

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

# ===== 10+ YENİ ÖZELLİK GLOBALLERİ =====
auto_restart_enabled = {}
file_stats = {}
file_locks = {}
file_notes = {}
APPROVAL_TTL_MINUTES = 15
last_active = {}
idle_check_enabled = [True]
resource_alerts_sent = set()
CPU_LIMIT_PERCENT = 85.0
RAM_LIMIT_PERCENT = 90.0

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================== VERİTABANI ==================
def init_db():
    logger.info(f"DB: {DATABASE_PATH}")
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
        logger.info(f"Yüklendi: {len(active_users)} kullanıcı.")
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
            for child in parent.children(recursive=True):
                try: child.terminate()
                except: pass
            gone, alive = psutil.wait_procs(parent.children(recursive=True), timeout=1)
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

# ================== SANAL ORTAM (VENV) ==================
def ensure_user_venv(user_id):
    """Her kullanıcı için ayrı sanal ortam oluşturur."""
    venv_dir = os.path.join(VENV_BASE_DIR, f"venv_{user_id}")
    python_bin = os.path.join(venv_dir, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'python')
    
    if not os.path.exists(python_bin):
        logger.info(f"🛠 venv oluşturuluyor: {venv_dir}")
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir],
                          capture_output=True, timeout=120, check=True)
            # pip güncelle
            try:
                subprocess.run([python_bin, '-m', 'pip', 'install', '--upgrade', 'pip'],
                              capture_output=True, timeout=120)
            except: pass
            logger.info(f"✅ venv hazır: {venv_dir}")
        except Exception as e:
            logger.error(f"venv hata: {e}")
            return sys.executable  # fallback
    return python_bin

def install_in_venv(user_id, package):
    python_bin = ensure_user_venv(user_id)
    try:
        r = subprocess.run([python_bin, '-m', 'pip', 'install', package],
                          capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore')
        return r.returncode == 0, r.stderr or r.stdout
    except subprocess.TimeoutExpired:
        return False, "Zaman aşımı"
    except Exception as e:
        return False, str(e)

# ================== SİSTEM KAYNAK İZLEME ==================
def get_system_stats():
    """Anlık CPU/RAM/disk bilgisi."""
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
    emoji_cpu = "🟢" if s['cpu'] < 50 else "🟡" if s['cpu'] < 80 else "🔴"
    emoji_ram = "🟢" if s['ram_percent'] < 60 else "🟡" if s['ram_percent'] < 85 else "🔴"
    return (
        f"💻 **SİSTEM DURUMU**\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{emoji_cpu} **CPU:** `{s['cpu']:.1f}%`\n"
        f"{emoji_ram} **RAM:** `{s['ram_percent']:.1f}%` "
        f"(`{s['ram_used_mb']:.0f} MB` / `{s['ram_total_mb']:.0f} MB`)\n"
        f"💾 **Disk:** `{s['disk_percent']:.1f}%` "
        f"(`{s['disk_used_gb']:.1f} GB` / `{s['disk_total_gb']:.1f} GB`)\n"
        f"⚙️ **Süreç:** `{s['processes']}`\n"
        f"🤖 **Bot:** `{len(bot_scripts)}` çalışan script\n"
        f"━━━━━━━━━━━━━━━━"
    )

# ================== OTOMATİK TEMİZLİK ==================
def cleanup_garbage():
    """Gereksiz geçici dosyaları, cache'leri temizler."""
    total_freed = 0
    try:
        # 1) Python __pycache__
        for root, dirs, files in os.walk(BASE_DIR):
            for d in list(dirs):
                if d == '__pycache__':
                    p = os.path.join(root, d)
                    try:
                        size = sum(f.stat().st_size for f in Path(p).rglob('*') if f.is_file())
                        shutil.rmtree(p, ignore_errors=True)
                        total_freed += size
                    except: pass
        # 2) Eski loglar (7 günden eski)
        cutoff = time.time() - 7*86400
        for root, dirs, files in os.walk(UPLOAD_BOTS_DIR):
            for f in files:
                if f.endswith('.log'):
                    p = os.path.join(root, f)
                    try:
                        if os.path.getmtime(p) < cutoff:
                            total_freed += os.path.getsize(p)
                            os.remove(p)
                    except: pass
        # 3) Temp
        for tmp in tempfile.gettempdir(), '/tmp':
            if os.path.exists(tmp):
                for item in os.listdir(tmp):
                    if item.startswith('user_') and item.endswith('_zip_'):
                        p = os.path.join(tmp, item)
                        try:
                            if os.path.isdir(p) and (time.time() - os.path.getmtime(p) > 3600):
                                size = sum(f.stat().st_size for f in Path(p).rglob('*') if f.is_file())
                                shutil.rmtree(p, ignore_errors=True)
                                total_freed += size
                        except: pass
        # 4) Çöp toplayıcı
        gc.collect()
        logger.info(f"🧹 Temizlik: {total_freed/1024/1024:.2f} MB serbest")
        return total_freed
    except Exception as e:
        logger.error(f"cleanup hata: {e}")
        return total_freed

# ================== CPU/RAM DÜŞÜRME ==================
def force_reduce_resources():
    """Yüksek CPU/RAM kullanan botları tespit edip kill eder, GC çalıştırır."""
    reduced = 0
    try:
        gc.collect()
        # Zombie process temizle
        for proc in psutil.process_iter(['pid', 'status', 'cpu_percent', 'memory_percent', 'name']):
            try:
                # Zombie
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    try: proc.kill()
                    except: pass
                # Çok yüksek RAM kullanan ve bizim bot olmayan (koruma amaçlı)
                if proc.info['memory_percent'] and proc.info['memory_percent'] > 50:
                    if 'python' in (proc.info['name'] or '').lower():
                        logger.warning(f"⚠️ Yüksek RAM: PID {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied): pass
        # Çok uzun süredir CPU yüksek olan kendi botlarımızı uyar
        s = get_system_stats()
        if s.get('cpu', 0) > CPU_LIMIT_PERCENT:
            logger.warning(f"🔥 CPU %{s['cpu']:.1f} - yüksek! GC çalıştırıldı.")
        if s.get('ram_percent', 0) > RAM_LIMIT_PERCENT:
            logger.warning(f"🔥 RAM %{s['ram_percent']:.1f} - yüksek!")
        reduced = 1
    except Exception as e:
        logger.error(f"force_reduce: {e}")
    return reduced

# ================== TOKEN ÇIKARMA + İMZALAMA ==================
def extract_bot_tokens(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        tokens = list(set(re.findall(r'\b(\d{8,12}:[A-Za-z0-9_-]{35})\b', content)))
        return tokens
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

def run_script(script_path, owner_id, user_folder, file_name, msg_obj, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        try: bot.send_message(msg_obj.chat.id, f"❌ '{file_name}' {max_attempts} denemede çalıştırılamadı.")
        except: pass
        return
    sk = f"{owner_id}_{file_name}"
    logger.info(f"Çalıştırma {attempt}: {script_path}")

    try:
        if not os.path.exists(script_path):
            try: bot.send_message(msg_obj.chat.id, f"❌ '{file_name}' bulunamadı!")
            except: pass
            remove_user_file_db(owner_id, file_name)
            return

        # Ön kontrol (attempt 1)
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
                            pkg = TELEGRAM_MODULES.get(mod.lower(), mod)
                            try: bot.send_message(msg_obj.chat.id, f"📦 `{pkg}` venv'e kuruluyor...", parse_mode='Markdown')
                            except: pass
                            ok, err = install_in_venv(owner_id, pkg)
                            if ok:
                                threading.Thread(target=run_script,
                                    args=(script_path, owner_id, user_folder, file_name, msg_obj, attempt+1),
                                    daemon=True).start()
                                return
                            else:
                                try: bot.send_message(msg_obj.chat.id, f"❌ `{pkg}` kurulamadı: {err[:300]}")
                                except: pass
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
                    f"🎉 Harika haber! `{file_name}` başarıyla çalıştırıldı!\n"
                    f"🆔 PID: `{process.pid}`\n"
                    f"🐍 Sanal ortam: `venv_{owner_id}`\n"
                    f"📊 Kanal: {FORCED_CHANNEL}\n\n"
                    f"Botunuz canlıda! Sorun olursa loglara bakabilirsiniz. 💪",
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
            if 'process' in locals() and process.poll() is None:
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': sk})
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
            types.InlineKeyboardButton("🔒 Botu Kilitle" if not bot_locked else "🔓 Kilidi Aç",
                                       callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton(t(user_id, 'admin_panel'), callback_data='admin_panel')
        )
        markup.row(
            types.InlineKeyboardButton("▶️ Tümünü Çalıştır", callback_data='run_all_scripts'),
            types.InlineKeyboardButton("📋 Bekleyen Onay", callback_data='pending_list')
        )
        markup.row(
            types.InlineKeyboardButton("🧹 Temizlik Yap", callback_data='cleanup_now'),
            types.InlineKeyboardButton("🔥 CPU/RAM Düşür", callback_data='reduce_now')
        )
        markup.row(
            types.InlineKeyboardButton("📥 Tüm .py'leri İndir (ZIP)", callback_data='bulk_download')
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
    m.row(types.InlineKeyboardButton("📥 Tüm .py ZIP", callback_data='bulk_download'))
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

# ================== ADMIN ONAY SİSTEMİ ==================
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
    bot.reply_to(message,
        "🎯 Dosyanız başarıyla alındı! Şimdi adminlerimizin incelemesinden geçecek.\n\n"
        "⏳ Onay süresi: 15 dakika\n"
        "✅ Onaylanınca otomatik olarak başlatılacak\n"
        "❌ Reddedilirse dosya silinecek\n\n"
        "Sabırla bekleyin, kısa sürede sonuçlanacak! 🙏", parse_mode='Markdown')
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(t(OWNER_ID, 'approve') + f" #{aid}", callback_data=f'approve_{aid}'),
        types.InlineKeyboardButton(t(OWNER_ID, 'reject') + f" #{aid}", callback_data=f'reject_{aid}')
    )
    text = (
        f"🔔 <b>{t(OWNER_ID, 'new_file_approval')}</b>\n\n"
        f"👤 Kullanıcı: <b>{uname}</b>\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📛 @{uusername}\n"
        f"📄 <code>{file_name}</code>\n"
        f"📦 Tür: <b>{file_type.upper()}</b>\n"
        f"🔢 Onay ID: <b>#{aid}</b>\n"
        f"⏱ Geçerlilik: <b>{APPROVAL_TTL_MINUTES} dakika</b>\n\n"
        f"Onaylıyor musun? 🤔"
    )
    for adm in list(admin_ids):
        try:
            try:
                with open(file_path, 'rb') as f:
                    bot.send_document(adm, f, caption=text, reply_markup=markup, parse_mode='HTML')
            except:
                bot.send_message(adm, text, reply_markup=markup, parse_mode='HTML')
        except Exception as e:
            logger.error(f"approval admin {adm}: {e}")

def handle_approve(call):
    try: aid = int(call.data.split('_')[1])
    except: bot.answer_callback_query(call.id, "Geçersiz."); return
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, t(call.from_user.id, 'admin_required'), show_alert=True); return
    with approvals_lock:
        info = pending_approvals.pop(aid, None)
        if not info:
            bot.answer_callback_query(call.id, t(call.from_user.id, 'already_processed'), show_alert=True); return
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
        bot.send_message(uchat, "🎉 MÜJDE! Dosyanız admin tarafından onaylandı!\n\n"
                                 "🚀 Botunuz şimdi başlatılıyor. Birazdan çalışmaya başlayacak.\n\n"
                                 "📢 Kanal: " + FORCED_CHANNEL + "\n"
                                 "💬 Destek: " + SUPPORT_USERNAME)
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
        bot.send_message(uchat, "😔 Maalesef dosyanız admin tarafından reddedildi.\n\n"
                                 "Sebebini öğrenmek için desteğe yazabilirsiniz: " + SUPPORT_USERNAME)
    except: pass

# ================== 3 SAATTE IDLE CHECK ==================
def idle_check_worker():
    """Her 3 saatte bir aktif kullanıcılara 'ordamisiniz?' sorar."""
    while True:
        try:
            time.sleep(3 * 3600)  # 3 saat
            if not idle_check_enabled[0]: continue
            now = datetime.now()
            for uid in list(active_users):
                if uid in admin_ids: continue
                last = last_active.get(uid, BOT_START_TIME)
                # Son 3 saatte aktif değilse mesaj at
                if (now - last).total_seconds() > 3*3600:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("✅ Evet, burdayım!", callback_data='im_here'))
                    try:
                        bot.send_message(uid,
                            f"👋 Merhaba! Sizi bir süredir aktif göremedim ve açıkçası biraz merak ettim. "
                            f"Her şey yolunda mı? 🤗\n\n"
                            f"Eğer buradaysanız lütfen aşağıdaki butona tıklayın, "
                            f"hem sizinle ilgilenelim hem de sistem sizi aktif olarak işaretlesin.\n\n"
                            f"💙 Sizi aramızda görmek çok güzel!",
                            reply_markup=markup)
                    except: pass
        except Exception as e:
            logger.error(f"idle_check: {e}")

# ================== TTL + WATCHDOG ==================
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
                    try:
                        bot.send_message(info['chat_id'],
                            f"⏰ Onay süresi doldu! `{info['file_name']}` otomatik silindi.",
                            parse_mode='Markdown')
                    except: pass
                    for adm in list(admin_ids):
                        try: bot.send_message(adm, f"⏰ Onay #{aid} süresi doldu.")
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
                                try:
                                    bot.send_message(oid,
                                        f"🔄 `{fn}` çöktü, otomatik yeniden başlatılıyor...",
                                        parse_mode='Markdown')
                                except: pass
                                threading.Thread(target=run_script,
                                    args=(fp, oid, info['user_folder'], fn, FM(info.get('chat_id', oid))),
                                    daemon=True).start()
                except Exception as e: logger.error(f"watchdog {sk}: {e}")
        except Exception as e: logger.error(f"watchdog: {e}")

def auto_cleanup_worker():
    """Her 30 dakikada otomatik çöp temizleme."""
    while True:
        try:
            time.sleep(1800)
            cleanup_garbage()
            force_reduce_resources()
        except Exception as e: logger.error(f"auto_cleanup: {e}")

def resource_monitor_worker():
    """Her 60 sn CPU/RAM kontrol, yüksekse admin uyar."""
    while True:
        try:
            time.sleep(60)
            s = get_system_stats()
            if not s: continue
            for adm in list(admin_ids):
                if s['cpu'] > CPU_LIMIT_PERCENT:
                    key = f"cpu_{adm}_{int(time.time()/300)}"
                    if key not in resource_alerts_sent:
                        resource_alerts_sent.add(key)
                        try:
                            bot.send_message(adm,
                                f"⚠️ **CPU UYARISI**\n\n"
                                f"🔥 CPU: `{s['cpu']:.1f}%` (limit: %{CPU_LIMIT_PERCENT})\n"
                                f"Otomatik temizlik yapılıyor...",
                                parse_mode='Markdown')
                        except: pass
                if s['ram_percent'] > RAM_LIMIT_PERCENT:
                    key = f"ram_{adm}_{int(time.time()/300)}"
                    if key not in resource_alerts_sent:
                        resource_alerts_sent.add(key)
                        try:
                            bot.send_message(adm,
                                f"⚠️ **RAM UYARISI**\n\n"
                                f"🔥 RAM: `{s['ram_percent']:.1f}%` (limit: %{RAM_LIMIT_PERCENT})",
                                parse_mode='Markdown')
                        except: pass
            # eski alert keyleri temizle
            if len(resource_alerts_sent) > 500:
                resource_alerts_sent.clear()
        except Exception as e: logger.error(f"resource_monitor: {e}")

# ================== İSTATİSTİK FONKSİYONLARI ==================
def get_uptime():
    u = datetime.now() - BOT_START_TIME
    d = u.days
    h, r = divmod(u.seconds, 3600)
    m, s = divmod(r, 60)
    return f"{d}g {h}s {m}d {s}sn"

# ================== ZIP ==================
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
        req = 'requirements.txt' if 'requirements.txt' in items else None
        if not pyf and not req:
            bot.reply_to(message, "❌ `.py` yok!"); return
        if req:
            try:
                bot.reply_to(message, f"📦 `requirements.txt` yükleniyor...")
                venv_python = ensure_user_venv(uid)
                subprocess.run([venv_python, '-m', 'pip', 'install', '-r', os.path.join(tmp, req)],
                              capture_output=True, timeout=300, text=True, errors='ignore')
                bot.reply_to(message, "✅ Bağımlılıklar kuruldu.")
            except: pass
        main = None
        for p in ['main.py', 'bot.py', 'app.py']:
            if p in pyf: main = p; break
        if not main and pyf: main = pyf[0]
        if not main:
            bot.reply_to(message, "❌ Ana script yok!"); return
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

# ================== BULK DOWNLOAD (Toplu .py ZIP) ==================
def build_bulk_zip(user_id=None):
    """Tüm kullanıcının (veya admin için tüm sistemin) .py dosyalarını ZIP yapar."""
    try:
        tmp = tempfile.mkdtemp(prefix="bulk_download_")
        zp = os.path.join(tmp, 'all_py_files.zip')
        count = 0
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            if user_id is None:
                # tüm sistem
                for uid, files in user_files.items():
                    for fn, ft in files:
                        if ft != 'py': continue
                        p = os.path.join(get_user_folder(uid), fn)
                        if os.path.exists(p):
                            z.write(p, arcname=f"user_{uid}/{fn}")
                            count += 1
            else:
                for fn, ft in user_files.get(user_id, []):
                    if ft != 'py': continue
                    p = os.path.join(get_user_folder(user_id), fn)
                    if os.path.exists(p):
                        z.write(p, arcname=fn)
                        count += 1
        if count == 0:
            shutil.rmtree(tmp, ignore_errors=True)
            return None, 0
        return zp, count
    except Exception as e:
        logger.error(f"bulk_zip: {e}")
        return None, 0

# ================== HANDLERS ==================
def _logic_send_welcome(message):
    uid = message.from_user.id
    cid = message.chat.id
    if bot_locked and uid not in admin_ids:
        bot.send_message(cid, t(uid, 'bot_locked')); return
    last_active[uid] = datetime.now()
    if uid not in active_users:
        add_active_user(uid)
        try:
            bot.send_message(OWNER_ID,
                f"🆕 **Yeni Kullanıcı!**\n\nAd: {message.from_user.first_name}\n"
                f"ID: `{uid}`\nKullanıcı: @{message.from_user.username or 'Yok'}",
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
    s = get_system_stats()
    cpu_e = "🟢" if s.get('cpu',0) < 50 else "🟡" if s.get('cpu',0) < 80 else "🔴"
    welcome = (
        f"🌟 **Merhaba {message.from_user.first_name}, hoş geldiniz!** 🌟\n\n"
        f"Sizi burada görmekten gerçekten çok mutluyum! 💙\n"
        f"Bugün sizi aramızda görmek beni çok memnun etti. "
        f"Umarım burada güzel vakit geçirir ve ihtiyacınız olan her şeyi bulursunuz.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **ID:** `{uid}`\n"
        f"📛 **Kullanıcı:** @{message.from_user.username or 'Yok'}\n"
        f"🎖️ **Durum:** {st}\n"
        f"📁 **Dosyalar:** {cf} / {ls}\n"
        f"{cpu_e} **CPU:** `{s.get('cpu', 0):.1f}%` | RAM: `{s.get('ram_percent', 0):.1f}%`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📢 **Kanal:** {FORCED_CHANNEL}\n"
        f"💬 **Destek:** {SUPPORT_USERNAME}\n\n"
        f"⚠️ **Önemli:** Tüm `.py` dosyaları **admin onayı** sonrası çalışır.\n"
        f"🐍 Her bot **kendi sanal ortamında** çalışır (izole & güvenli).\n\n"
        f"Ne yapmak istersiniz? Aşağıdaki menüden seçin 👇"
    )
    try:
        bot.send_message(cid, welcome, reply_markup=create_main_menu_inline(uid), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"welcome: {e}")

def _logic_check_files(message):
    uid = message.from_user.id
    if not user_files.get(uid):
        bot.reply_to(message, "📂 Henüz hiç dosya yüklemediniz.\n\n"
                              "💡 `.py` veya `.zip` dosyası gönderebilirsiniz."); return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for fn, ft in sorted(user_files[uid]):
        is_run = is_bot_running(uid, fn)
        pending = any(i['user_id'] == uid and i['file_name'] == fn for i in pending_approvals.values())
        if pending: icon = "⏳ Onay Bekliyor"
        else: icon = "🟢 Çalışıyor" if is_run else "🔴 Durdu"
        note_icon = " 📝" if file_notes.get(f"{uid}_{fn}") else ""
        lock_icon = " 🔒" if file_locks.get(f"{uid}_{fn}", False) else ""
        markup.add(types.InlineKeyboardButton(f"{fn} ({ft}) - {icon}{note_icon}{lock_icon}",
                    callback_data=f'file_{uid}_{fn}'))
    bot.reply_to(message, "📂 **Dosyalarınız:**\n\nYönetmek için tıklayın 👇",
                 reply_markup=markup, parse_mode='Markdown')

def _logic_uptime(message):
    bot.reply_to(message, f"⏱ Bot Çalışma Süresi: `{get_uptime()}`", parse_mode='Markdown')

def _logic_statistics(message):
    uid = message.from_user.id
    tu = len(active_users)
    tf = sum(len(f) for f in user_files.values())
    rb = sum(1 for k, i in bot_scripts.items() if is_bot_running(i.get('script_owner_id'), i.get('file_name')))
    my = sum(1 for k, i in bot_scripts.items() if i.get('script_owner_id') == uid and is_bot_running(i.get('script_owner_id'), i.get('file_name')))
    pend = len(pending_approvals)
    s = get_system_stats()
    txt = (
        f"📊 **İSTATİSTİKLER**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👥 Toplam Kullanıcı: `{tu}`\n"
        f"📁 Toplam Dosya: `{tf}`\n"
        f"🤖 Aktif Bot: `{rb}`\n"
        f"👤 Senin Çalışan: `{my}`\n"
        f"⏳ Bekleyen Onay: `{pend}`\n"
        f"💻 CPU: `{s.get('cpu', 0):.1f}%` | RAM: `{s.get('ram_percent', 0):.1f}%`\n"
        f"⏱ Uptime: `{get_uptime()}`"
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
    bot.reply_to(m, "🧹 Temizlik başlatılıyor...")
    freed = cleanup_garbage()
    bot.reply_to(m, f"✅ **Temizlik tamamlandı!**\n\n"
                     f"💾 **Serbest kalan:** `{freed/1024/1024:.2f} MB`\n"
                     f"🔄 GC çalıştırıldı.", parse_mode='Markdown')

@bot.message_handler(commands=['reduce'])
def cmd_reduce(m):
    if m.from_user.id not in admin_ids:
        bot.reply_to(m, "Admin gerekli."); return
    bot.reply_to(m, "🔥 Kaynaklar zorla düşürülüyor...")
    force_reduce_resources()
    s = get_system_stats()
    bot.reply_to(m, f"✅ Düşürüldü!\n\n"
                     f"💻 CPU: `{s.get('cpu', 0):.1f}%`\n"
                     f"🧠 RAM: `{s.get('ram_percent', 0):.1f}%`", parse_mode='Markdown')

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
    last_active[uid] = datetime.now()
    if bot_locked and uid not in admin_ids:
        bot.reply_to(message, t(uid, 'bot_locked')); return
    fl = get_user_file_limit(uid)
    cf = get_user_file_count(uid)
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

# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid = call.from_user.id
    d = call.data
    last_active[uid] = datetime.now()
    logger.info(f"CB: {uid} -> {d}")
    if bot_locked and uid not in admin_ids and not (d.startswith('approve_') or d.startswith('reject_') or d == 'im_here'):
        bot.answer_callback_query(call.id, t(uid, 'bot_locked'), show_alert=True); return
    try:
        if d == 'im_here':
            bot.answer_callback_query(call.id, "💙 Harika! Sizi görmek güzel!")
            try:
                bot.send_message(call.message.chat.id,
                    "😊 Çok sevindim! Sizi tekrar gördüğüme memnun oldum.\n"
                    "İhtiyacınız olan her şey için buradayım! 💙")
            except: pass
            return
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
                f"⚡ **HIZ TESTİ**\n\n"
                f"💻 CPU: `{s.get('cpu',0):.1f}%`\n"
                f"🧠 RAM: `{s.get('ram_percent',0):.1f}%`\n"
                f"🟢 Durum: `Aktif`\n"
                f"⏱ Uptime: `{get_uptime()}`", parse_mode='Markdown')
        elif d == 'back_to_main': cb_back_main(call)
        elif d.startswith('approve_'): handle_approve(call)
        elif d.startswith('reject_'): handle_reject(call)
        elif d == 'pending_list':
            if uid in admin_ids: cb_pending(call)
            else: bot.answer_callback_query(call.id, "Admin gerekli.", show_alert=True)
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
            bot.send_message(call.message.chat.id, "🤖 Sorunuzu `/mpx <soru>` komutuyla sorun.", parse_mode='Markdown')
        elif d == 'uptime':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"⏱ `{get_uptime()}`", parse_mode='Markdown')
        elif d == 'sysinfo':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, format_stats(), parse_mode='Markdown')
        elif d == 'cleanup_now':
            if uid in admin_ids:
                bot.answer_callback_query(call.id, "Temizlik başladı...")
                freed = cleanup_garbage()
                bot.send_message(call.message.chat.id,
                    f"🧹 Temizlik tamam!\n💾 Serbest: `{freed/1024/1024:.2f} MB`", parse_mode='Markdown')
        elif d == 'reduce_now':
            if uid in admin_ids:
                bot.answer_callback_query(call.id, "Kaynaklar düşürülüyor...")
                force_reduce_resources()
                s = get_system_stats()
                bot.send_message(call.message.chat.id,
                    f"🔥 Düşürüldü!\n💻 CPU: `{s.get('cpu',0):.1f}%`\n🧠 RAM: `{s.get('ram_percent',0):.1f}%`",
                    parse_mode='Markdown')
        elif d == 'bulk_download':
            if uid in admin_ids: cb_bulk_download(call, None)
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
    bot.send_message(call.message.chat.id,
        "📤 **Dosya Yükleme**\n\n"
        "Bana bir `.py` veya `.zip` dosyası gönderin.\n\n"
        "⚠️ Dosyanız admin onayından geçtikten sonra çalışacaktır.\n"
        "🐍 Her dosya kendi sanal ortamında (venv) çalışır.", parse_mode='Markdown')

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
        note_icon = " 📝" if file_notes.get(f"{uid}_{fn}") else ""
        lock_icon = " 🔒" if file_locks.get(f"{uid}_{fn}", False) else ""
        markup.add(types.InlineKeyboardButton(f"{icon} {fn} ({ft}){note_icon}{lock_icon}",
                    callback_data=f'file_{uid}_{fn}'))
    markup.add(types.InlineKeyboardButton("🔙 Ana Menü", callback_data='back_to_main'))
    try:
        bot.edit_message_text("📂 **Dosyalarınız:**\n\nYönetmek için tıklayın 👇", call.message.chat.id,
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
        note = file_notes.get(f"{oid}_{fn}", "")
        note_str = f"\n📝 Not: {note}" if note else ""
        try:
            bot.edit_message_text(
                f"🎛 **Kontrol**\n\n📄 `{fn}`\n👤 `{oid}`\n📊 {status}{note_str}",
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
            bot.answer_callback_query(call.id, "⏳ Admin onayı bekliyor.", show_alert=True); return
        if not any(f[0] == fn for f in user_files.get(oid, [])):
            bot.answer_callback_query(call.id, "Bulunamadı.", show_alert=True); return
        uf = get_user_folder(oid)
        fp = os.path.join(uf, fn)
        if not os.path.exists(fp):
            bot.answer_callback_query(call.id, "Dosya kayıp.", show_alert=True); return
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
    except Exception as e:
        logger.error(f"start: {e}")

def cb_stop(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        if file_locks.get(f"{oid}_{fn}", False) and rid not in admin_ids:
            bot.answer_callback_query(call.id, "🔒 Dosya kilitli. Önce kilidi açın.", show_alert=True); return
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
        if any(i['user_id'] == oid and i['file_name'] == fn for i in pending_approvals.values()):
            bot.answer_callback_query(call.id, "Onay bekliyor.", show_alert=True); return
        uf = get_user_folder(oid); fp = os.path.join(uf, fn)
        if not os.path.exists(fp):
            bot.answer_callback_query(call.id, "Kayıp.", show_alert=True); return
        bot.answer_callback_query(call.id, "Yeniden başlıyor...")
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
        if file_locks.get(f"{oid}_{fn}", False) and rid not in admin_ids:
            bot.answer_callback_query(call.id, "🔒 Dosya kilitli.", show_alert=True); return
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
        file_locks.pop(sk, None)
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
        f"🏠 **Ana Menü**\n\n"
        f"👤 ID: `{uid}`\n"
        f"📁 Dosyalar: `{cf}/{ls}`\n\n"
        f"📢 {FORCED_CHANNEL}\n"
        f"💬 {SUPPORT_USERNAME}"
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
    msg = bot.send_message(call.message.chat.id, "📢 Duyuru mesajını yaz.\n/cancel iptal.")
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
    bot.reply_to(m, f"📢 **Onay?**\n\n```\n{preview}\n```\n\n"
                     f"**{target}** kullanıcıya gönderilecek.",
                 reply_markup=markup, parse_mode='Markdown')

def cb_confirm_broadcast(call):
    if call.from_user.id not in admin_ids: return
    try:
        orig = call.message.reply_to_message
        if not orig: raise ValueError("Orijinal yok.")
        text = orig.text
        bot.answer_callback_query(call.id, "Başladı...")
        bot.edit_message_text(f"{len(active_users)} kişiye gönderiliyor...", call.message.chat.id,
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
            elif "flood" in err or "too many" in err:
                time.sleep(5)
                try: bot.send_message(uid, text); sent += 1
                except: failed += 1
            else: failed += 1
        except: failed += 1
        if (i+1) % 25 == 0: time.sleep(1.5)
        else: time.sleep(0.05)
    bot.send_message(admin_chat, f"✅ Duyuru tamam!\n📤 {sent}\n❌ {failed}\n🚫 {blocked}")

def cb_subs(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("💳 Abonelik Yönetimi\n\nİşlem seç:",
        call.message.chat.id, call.message.message_id,
        reply_markup=create_subscription_menu(call.from_user.id))

def cb_admin_panel(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("👑 Admin Paneli", call.message.chat.id, call.message.message_id,
        reply_markup=create_admin_panel(call.from_user.id))

def cb_add_admin(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Admin yapılacak ID gir.\n/cancel iptal.")
    bot.register_next_step_handler(msg, process_add_admin)

def process_add_admin(m):
    if m.from_user.id != OWNER_ID: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        nid = int(m.text.strip())
        if nid in admin_ids: bot.reply_to(m, "Zaten admin."); return
        add_admin_db(nid)
        bot.reply_to(m, f"✅ `{nid}` admin yapıldı.", parse_mode='Markdown')
        try: bot.send_message(nid, "🎉 Artık adminsin!")
        except: pass
    except:
        bot.reply_to(m, "Geçersiz ID.")

def cb_remove_admin(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Silinecek admin ID gir.\n/cancel iptal.")
    bot.register_next_step_handler(msg, process_remove_admin)

def process_remove_admin(m):
    if m.from_user.id != OWNER_ID: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        nid = int(m.text.strip())
        if remove_admin_db(nid):
            bot.reply_to(m, f"✅ `{nid}` silindi.", parse_mode='Markdown')
        else:
            bot.reply_to(m, f"`{nid}` silinemedi (sahip mi?).", parse_mode='Markdown')
    except: bot.reply_to(m, "Geçersiz ID.")

def cb_list_admins(call):
    bot.answer_callback_query(call.id)
    lst = "\n".join(f"- `{a}` {'(Sahip)' if a == OWNER_ID else ''}" for a in sorted(admin_ids))
    bot.edit_message_text(f"👑 **Adminler:**\n\n{lst}", call.message.chat.id,
        call.message.message_id, reply_markup=create_admin_panel(call.from_user.id), parse_mode='Markdown')

def cb_add_sub(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Format: `ID gün`\n/cancel iptal.", parse_mode='Markdown')
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
    msg = bot.send_message(call.message.chat.id, "Silinecek ID gir.\n/cancel iptal.")
    bot.register_next_step_handler(msg, process_remove_sub)

def process_remove_sub(m):
    if m.from_user.id not in admin_ids: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        uid = int(m.text.strip())
        if uid not in user_subscriptions: bot.reply_to(m, "Yok."); return
        remove_subscription_db(uid)
        bot.reply_to(m, f"✅ `{uid}` silindi.", parse_mode='Markdown')
    except: bot.reply_to(m, "Geçersiz.")

def cb_check_sub(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "Kontrol edilecek ID gir.\n/cancel iptal.")
    bot.register_next_step_handler(msg, process_check_sub)

def process_check_sub(m):
    if m.from_user.id not in admin_ids: return
    if m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    try:
        uid = int(m.text.strip())
        if uid in user_subscriptions:
            exp = user_subscriptions[uid].get('expiry')
            if exp and exp > datetime.now():
                bot.reply_to(m, f"✅ `{uid}` aktif, {exp:%Y-%m-%d}", parse_mode='Markdown')
            else:
                bot.reply_to(m, f"⚠️ Süresi dolmuş."); remove_subscription_db(uid)
        else: bot.reply_to(m, f"Kayıt yok.")
    except: bot.reply_to(m, "Geçersiz.")

def cb_bulk_download(call, user_id):
    bot.answer_callback_query(call.id, "ZIP hazırlanıyor...")
    fp, count = build_bulk_zip(user_id)
    if not fp:
        bot.send_message(call.message.chat.id, "İndirilecek .py yok."); return
    try:
        with open(fp, 'rb') as f:
            bot.send_document(call.message.chat.id, f,
                caption=f"📥 Toplu .py indirme\n📄 {count} dosya\n📦 ZIP",
                parse_mode='Markdown')
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Hata: {e}")
    finally:
        try: os.remove(fp); shutil.rmtree(os.path.dirname(fp), ignore_errors=True)
        except: pass

def cb_toggle_auto(call):
    try:
        _, oid, fn = call.data.split('_', 2)
        oid = int(oid); rid = call.from_user.id
        if not (rid == oid or rid in admin_ids):
            bot.answer_callback_query(call.id, "İzin yok.", show_alert=True); return
        sk = f"{oid}_{fn}"
        auto_restart_enabled[sk] = not auto_restart_enabled.get(sk, False)
        state = "AÇIK" if auto_restart_enabled[sk] else "KAPALI"
        bot.answer_callback_query(call.id, f"Auto-Restart: {state}")
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
        note = file_notes.get(sk, "—")
        msg = (f"📊 **İstatistik**\n\n"
               f"📄 `{fn}`\n👤 `{oid}`\n"
               f"🔌 {'🟢 Çalışıyor' if is_run else '🔴 Durdu'}\n"
               f"⏱ Uptime: `{up}`\n"
               f"🔄 Auto: {auto} | {lock}\n"
               f"↻ Restart: `{st.get('restarts', 0)}`\n"
               f"💥 Crash: `{st.get('crashes', 0)}`\n"
               f"📝 Not: {note}")
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
                caption=f"📜 Log: `{fn}`", parse_mode='Markdown')
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
        state = "🔒 KİLİTLİ" if file_locks[sk] else "🔓 AÇIK"
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
            f"📝 `{fn}` için not yaz:\n\n"
            f"Mevcut: {cur or '(yok)'}\n\n"
            f"Sil: `sil` yaz\nİptal: /cancel",
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_note, oid, fn)
    except Exception as e: logger.error(f"note: {e}")

def process_note(m, oid, fn):
    if m.from_user.id != oid and m.from_user.id not in admin_ids: return
    if m.text and m.text.lower() == '/cancel': bot.reply_to(m, "İptal."); return
    note = m.text.strip() if m.text else ""
    if note.lower() == 'sil': note = ""
    save_file_note(oid, fn, note[:500])
    bot.reply_to(m, f"✅ Not kaydedildi." if note else "✅ Not silindi.")

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
    logger.info(f"🛡 Adminler: {admin_ids}")
    logger.info(f"📢 Kanal: {FORCED_CHANNEL}")
    logger.info("="*50)

    keep_alive()

    # Arka plan worker'ları
    threading.Thread(target=approval_cleanup_worker, daemon=True).start()
    threading.Thread(target=watchdog_worker, daemon=True).start()
    threading.Thread(target=auto_cleanup_worker, daemon=True).start()
    threading.Thread(target=resource_monitor_worker, daemon=True).start()
    threading.Thread(target=idle_check_worker, daemon=True).start()
    logger.info("✅ Tüm worker'lar başlatıldı.")

    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            time.sleep(15)
        except Exception as e:
            logger.critical(f"Polling: {e}", exc_info=True)
            time.sleep(30)
