import smtplib
import time
import os
import json
import pandas as pd
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS # Import CORS
from werkzeug.utils import secure_filename
import logging
from threading import Thread

# --- Basic Setup ---
app = Flask(__name__, template_folder='.', static_folder='static')
CORS(app) # Enable CORS for all routes and origins

# --- Configuration & Globals ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
ALLOWED_RESUME_EXTENSIONS = {'.pdf'}
COUNTER_FILE = "email_counter.json"
CONFIG_FILE = "config.json"
LOGS = [] # In-memory log storage

# --- Ensure necessary folders and files exist ---
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(app.static_folder):
    os.makedirs(app.static_folder)


# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
def log_message(message):
    """Adds a message to the in-memory log and prints it."""
    logging.info(message)
    LOGS.append(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# --- Helper Functions ---

def allowed_file(filename, allowed_set):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           os.path.splitext(filename)[1].lower() in allowed_set

def save_config(data):
    """Saves configuration data to a JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_config():
    """Loads configuration data from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def load_counter():
    """Loads the email sent counter from its file."""
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            try:
                data = json.load(f)
                return data.get('counter', 0)
            except json.JSONDecodeError:
                return 0
    return 0

def save_counter(counter):
    """Saves the email sent counter to its file."""
    with open(COUNTER_FILE, 'w') as f:
        json.dump({'counter': counter}, f)

def get_email_templates():
    """
    This function now returns a dictionary of available email templates.
    In a real app, this could read from a directory of template files.
    """
    return {
        "default": {
            "subject": "Hi, I am Akash Sakhare",
            "body": """{greeting},

I hope you're having a productive and meaningful day.

My name is Akash Sakhare, and I’m currently working as a Junior Software Engineer in Bangalore. I’m reaching out to explore any potential openings for AI/ML or Software Engineer roles at your organization. I’ve been following the impactful work your team delivers, and I’d be excited to contribute my skills and passion to such a forward-thinking environment.

I’ve attached my resume for your review. If there are any current or upcoming opportunities where I could contribute, I’d love to connect and discuss further.

Warm regards,
Akash Sakhare
"""
        },
        "concise": {
            "subject": "AI/Data Science Opportunity",
            "body": """{greeting},

I hope this email finds you well. I'm Akash Sakhare, a Junior Software Engineer with experience in AI development, and I'm interested in exploring opportunities with your team.

My key achievements include building ML pipelines, developing conversational AI, and fine-tuning LLMs. I'm passionate about solving real-world problems through AI.

I've attached my resume for your consideration. I'd appreciate the opportunity to discuss how my skills align with your current needs.

Best regards,
Akash Sakhare
"""
        }
    }

def extract_name(email):
    """Extracts a name from an email address for personalization."""
    try:
        local_part = email.split('@')[0]
        # Remove common separators and non-alphabetic characters
        name = re.sub(r'[^a-zA-Z]', ' ', local_part).strip()
        # Capitalize the first letter of each part of the name
        name = ' '.join([part.capitalize() for part in name.split()])
        return name if name else "there"
    except:
        return "there"

# --- Email Sending Logic (Threaded) ---

def send_emails_task(config):
    """The core email sending logic, designed to be run in a background thread."""
    global LOGS
    LOGS.clear() # Clear logs for the new session
    
    log_message("Email sending process started.")

    # Load configuration
    sender_email = config.get("email")
    app_password = config.get("password")
    stopper_value = int(config.get("stopper", 100))
    csv_file_path = config.get("default_file")
    template_name = config.get("template_name", "default")
    template_subject = config.get("template_subject", "Hello")
    template_body = config.get("template_body", "Hi {greeting}")
    resume_filename = config.get("resume_file") 

    if not all([sender_email, app_password, csv_file_path]):
        log_message("ERROR: Missing credentials, stopper value, or default CSV file.")
        return
        
    resume_path = os.path.join(UPLOAD_FOLDER, resume_filename) if resume_filename else None


    # Load email list from CSV
    try:
        full_csv_path = os.path.join(UPLOAD_FOLDER, csv_file_path)
        data = pd.read_csv(full_csv_path, encoding="utf-8")
        # Find email column (case-insensitive)
        email_column = next((col for col in data.columns if 'email' in col.lower()), None)
        if not email_column:
            log_message(f"ERROR: No 'email' column found in {csv_file_path}.")
            return
        data = data.dropna(subset=[email_column])
        email_list = data[email_column].str.strip().tolist()
        log_message(f"Loaded {len(email_list)} emails from {csv_file_path}.")
    except Exception as e:
        log_message(f"ERROR loading CSV file: {e}")
        return

    start_counter = load_counter()
    end_counter = min(start_counter + stopper_value, len(email_list))

    if start_counter >= len(email_list):
        log_message("All emails have already been sent!")
        return

    log_message(f"Preparing to send emails from index {start_counter} to {end_counter-1}.")

    # Connect to SMTP server
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        log_message("Successfully connected to Gmail SMTP server.")
    except Exception as e:
        log_message(f"ERROR: Failed to connect to SMTP server. Check credentials. Details: {e}")
        return

    # Loop and send emails
    for i in range(start_counter, end_counter):
        receiver = email_list[i]
        greeting = f"Hi {extract_name(receiver)}"
        
        msg = MIMEMultipart()
        msg["From"] = formataddr(("Akash Sakhare", sender_email))
        msg["To"] = receiver
        msg["Subject"] = template_subject
        
        body = template_body.format(greeting=greeting)
        msg.attach(MIMEText(body, "plain"))

        # Attach resume if path is provided
        if resume_path and os.path.exists(resume_path):
            try:
                with open(resume_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(resume_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(resume_path)}"'
                msg.attach(part)
            except Exception as e:
                log_message(f"Warning: Could not attach resume for {receiver}. Error: {e}")
        elif resume_filename:
             log_message(f"Warning: Resume file '{resume_filename}' not found. Sending without attachment.")


        try:
            server.sendmail(sender_email, receiver, msg.as_string())
            current_counter = i + 1
            log_message(f"SUCCESS: Email sent to {receiver} ({current_counter}/{len(email_list)})")
            save_counter(current_counter)
            time.sleep(5) # Rate limiting
        except Exception as e:
            log_message(f"ERROR sending to {receiver}: {e}")
            # Optional: decide if you want to stop on error or continue
    
    server.quit()
    log_message("Batch finished. SMTP server connection closed.")


# --- Flask Routes (API) ---

@app.route("/")
def index():
    """Serves the main HTML page."""
    return render_template("index.html")

# NOTE: Removed the specific /favicon.ico route. 
# Flask will automatically serve it from the static folder
# when requested via url_for('static', filename='favicon.ico').

@app.route('/api/save-credentials', methods=['POST'])
def save_credentials():
    """Saves user email and app password to the config."""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    if not password or len(password) != 16:
        return jsonify({'error': 'App Password must be 16 characters long.'}), 400
    
    config = load_config()
    config['email'] = email
    config['password'] = password
    save_config(config)
    
    return jsonify({'success': True, 'message': 'Credentials saved successfully.'})

@app.route('/api/credentials/clear', methods=['POST'])
def clear_credentials():
    """Clears the saved credentials from the config file."""
    config = load_config()
    if 'email' in config:
        del config['email']
    if 'password' in config:
        del config['password']
    save_config(config)
    return jsonify({'success': True, 'message': 'Credentials cleared.'})

@app.route('/api/files', methods=['GET'])
def list_files():
    """Lists all uploaded CSV/Excel files."""
    files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f, ALLOWED_EXTENSIONS)]
    config = load_config()
    default_file = config.get('default_file')
    return jsonify({'files': files, 'default_file': default_file})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'File type not allowed. Please upload CSV or Excel files.'}), 400
    
@app.route('/api/resume/upload', methods=['POST'])
def upload_resume():
    """Handles resume uploads."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename, ALLOWED_RESUME_EXTENSIONS):
        filename = secure_filename(file.filename)
        # To avoid conflicts, you might want to save all resumes with a standard name
        # or handle multiple resumes. For simplicity, we'll overwrite.
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        config = load_config()
        config['resume_file'] = filename
        save_config(config)
        
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

@app.route('/api/resume', methods=['GET'])
def get_resume():
    """Gets the current resume file name."""
    config = load_config()
    return jsonify({'resume_file': config.get('resume_file')})

@app.route('/api/resume/delete', methods=['POST'])
def delete_resume():
    """Deletes the resume file."""
    config = load_config()
    resume_filename = config.get('resume_file')
    if resume_filename:
        file_path = os.path.join(UPLOAD_FOLDER, resume_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        del config['resume_file']
        save_config(config)
        return jsonify({'success': True})
    return jsonify({'error': 'No resume file to delete'}), 404


@app.route('/api/files/set-default', methods=['POST'])
def set_default_file():
    """Sets a file as the default for sending emails."""
    filename = request.json.get('filename')
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
        
    config = load_config()
    config['default_file'] = filename
    save_config(config)
    return jsonify({'success': True})

@app.route('/api/files/delete', methods=['POST'])
def delete_file():
    """Deletes an uploaded file."""
    filename = request.json.get('filename')
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        # Also remove from config if it was the default
        config = load_config()
        if config.get('default_file') == filename:
            del config['default_file']
            save_config(config)
        return jsonify({'success': True})
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/templates', methods=['GET'])
def api_get_templates():
    """Returns the available email templates."""
    config = load_config()
    return jsonify({
        'templates': get_email_templates(),
        'current_template': config.get('current_template', {})
    })

@app.route('/api/templates/save', methods=['POST'])
def save_template():
    """Saves the currently active/edited email template."""
    data = request.json
    config = load_config()
    config['current_template'] = {
        "name": data.get("name"),
        "subject": data.get("subject"),
        "body": data.get("body")
    }
    save_config(config)
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Gets the current status of the application."""
    config = load_config()
    counter = load_counter()
    return jsonify({
        'counter': counter,
        'stopper': int(config.get('stopper', 100)),
        'email': config.get('email', '')
    })

@app.route('/api/stopper', methods=['POST'])
def set_stopper():
    """Sets the stopper value (batch size)."""
    value = request.json.get('value')
    try:
        stopper_value = int(value)
        if stopper_value <= 0:
            raise ValueError
        config = load_config()
        config['stopper'] = stopper_value
        save_config(config)
        return jsonify({'success': True})
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid stopper value. Must be a positive number.'}), 400

@app.route('/api/counter/reset', methods=['POST'])
def reset_counter():
    """Resets the email counter to 0."""
    save_counter(0)
    log_message("Counter has been reset to 0.")
    return jsonify({'success': True})

@app.route('/api/send', methods=['POST'])
def start_sending():
    """Starts the email sending process in a background thread."""
    config = load_config()
    
    # Use the saved custom template if it exists, otherwise use a default
    template_info = config.get('current_template', {})
    template_name = template_info.get('name', 'default')
    
    all_templates = get_email_templates()
    
    if template_name in all_templates and not template_info.get('body'):
        template_subject = all_templates[template_name]['subject']
        template_body = all_templates[template_name]['body']
    else: # Use custom saved template
        template_subject = template_info.get('subject', 'Hello')
        template_body = template_info.get('body', 'Hi {greeting}')

    
    send_config = {
        "email": config.get('email'),
        "password": config.get('password'),
        "stopper": config.get('stopper', 100),
        "default_file": config.get('default_file'),
        "resume_file": config.get('resume_file'),
        "template_name": template_name,
        "template_subject": template_subject,
        "template_body": template_body,
    }

    # Start the sending task in a new thread
    thread = Thread(target=send_emails_task, args=(send_config,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Email sending process initiated.'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Returns the current logs."""
    return jsonify({'logs': LOGS})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
