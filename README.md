# 📧 Professional Bulk Mail Sender for Lead Generation – Web UI

A powerful, self-hosted web application for sending personalized bulk emails with attachments. This tool provides a modern, user-friendly interface for managing recipient lists, email templates, and tracking the progress of email campaigns. It transforms a basic command-line script into a fully interactive dashboard.

---

## 🌟 Features

### 🔥 Modern Web Dashboard
- Clean, responsive UI built for light mode.
- Manage email campaigns from a single interactive interface.

### 🔐 Secure Credential Handling
- Enter your Gmail and App Password once.
- Stored securely in a local `config.json` file.

### 📂 File Management
- Upload CSV or Excel files containing recipient email addresses.
- Set a default list for your campaign.
- Delete unused files directly from the interface.

### 📎 Resume/Proposal Attachment
- Upload a single PDF to be attached to all outgoing emails.
- Delete or re-upload the file as needed.

### 📝 Customizable Email Templates
- Load preset templates or write your own subject and body.
- Edit in a pop-up modal.
- Use `{greeting}` to auto-personalize names from email addresses.

### 📨 Batch Sending & Progress Tracking
- **Live Counter**: Displays number of emails sent in real-time.
- **Batch Size (Stopper)**: Control how many emails to send in a single run (default: 400).
- **Reset Counter**: Restart your campaign anytime.

### 💻 Real-Time System Console
- Live status log of every email sent.
- View errors and success messages instantly.

### 👥 Account Management
- Easily reset stored credentials to switch sending accounts.

---

## 🗂 Project Structure

```
/bulk-mail-sender/
│
├── app.py                # Flask backend with all application logic
├── index.html            # Main frontend interface
├── uploads/              # Auto-created. Stores uploaded CSV and PDF files
├── static/               # Contains static files like favicon.ico
├── config.json           # Auto-created. Stores credentials and settings
├── email_counter.json    # Auto-created. Tracks email sending progress
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## ⚙️ Setup and Installation

### 1. Prerequisites
- Ensure **Python 3** is installed.
  ```bash
  python --version
  ```

### 2. Clone or Download
- Download and unzip this repository to a dedicated folder.

### 3. Install Required Packages
Navigate to the project directory in your terminal:
```bash
pip install -r requirements.txt
```

### 4. Set Up Gmail App Password (Required)
> **Do not use your regular Gmail password.**

1. **Enable 2-Step Verification** on your Google account.  
2. **Generate an App Password**:
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Select **Mail** as the app.
   - Select your device (e.g., Windows Computer).
   - Click **Generate** and copy the 16-character password.

🔗 [Watch Guide on YouTube](https://youtu.be/GsXyF5Zb5UY?si=2_AC3gAnxcMZly1I)

---

## ▶️ Running the Application

1. Open terminal and navigate to your project folder.
2. Run the Flask server:
   ```bash
   python app.py
   ```
3. Once the server is running, open your browser and go to:
   ```
   http://127.0.0.1:5001
   ```

---

## 💡 How to Use the Dashboard

1. **Enter Gmail Credentials**  
   - Input your Gmail address and 16-digit App Password.  
   - Click **Save and Continue**.

2. **Upload Resume / Proposal**  
   - Upload the PDF file you want to send with emails.

3. **Upload Recipient List**  
   - Upload a CSV or Excel file containing recipient emails.  
   - Must have a column named `email`.

4. **Set Default File**  
   - Click **Set Default** next to the uploaded recipient list.

5. **Edit Email Template**  
   - Click **Edit / Select Template**.  
   - Add subject and body. Use `{greeting}` to personalize.  
   - Click **Save and Use**.

6. **Set Batch Size (Optional)**  
   - Adjust the **Stopper** value to control batch sending.

7. **Start Sending Emails**  
   - Click **Start Sending Emails**.

8. **Monitor Progress**  
   - Watch live logs and email counter in the dashboard.

---

## 📌 Notes

- The `{greeting}` placeholder in the email template is automatically replaced with a name extracted from the email address.
- Attachments are sent to **every recipient**.
- You can **reset email counter** to restart your campaign.
- You can **reset credentials** to switch Gmail accounts.

---

## 📧 Disclaimer

This tool uses Gmail’s SMTP servers and is subject to Gmail’s sending limits and anti-spam policies. Avoid sending spam or unsolicited emails.

---

## 🛠️ Future Improvements

- Dark mode support.
- Scheduling options.
- Multi-attachment support.
- Gmail API integration.

---

## 🙌 Contributing

Pull requests and suggestions are welcome!  
Please fork the repo and submit your ideas or improvements.

---

## 📄 License

This project is open-source and free to use for personal and professional purposes. No commercial license required.
