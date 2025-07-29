# Gmail Email Scraper

A powerful Python-based Gmail email scraping tool that uses Playwright and AgentQL to extract email data from your Gmail inbox. This tool can handle Google Workspace redirects and provides comprehensive email analysis.

## 🚀 Features

- **Smart Login Handling**: Automatically handles Google Workspace redirects and sign-in flows
- **Dual Scraping Methods**: Uses AgentQL for intelligent extraction with traditional CSS fallback
- **Comprehensive Data Extraction**: Captures sender, subject, date, time, description, read status, attachments, and priority
- **Email Analysis**: Provides insights on top senders, common words, and activity patterns
- **Flexible Filtering**: Filter emails by sender, subject, read status, attachments, and priority
- **Data Export**: Saves all email data to JSON format
- **Session Management**: Remembers login sessions to avoid repeated authentication

## 📋 Prerequisites

- Python 3.7+
- Gmail account
- Google Workspace account (if applicable)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install required packages:**
   ```bash
   pip install playwright agentql python-dotenv
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root with your Gmail credentials:
   ```env
   EMAIL_GMAIL=your-email@gmail.com
   PASSWORD_GMAIL=your-app-password
   ```

   > **Note**: Use an App Password instead of your regular password for security. [Learn how to create an App Password](https://support.google.com/accounts/answer/185833)

## 🎯 Quick Start

1. **Configure your credentials** in the `.env` file
2. **Run the script:**
   ```bash
   python gmaiil_check.py
   ```
3. **Check the output** for email summary and analysis
4. **Find your data** in `emails_data.json`

## 📊 What Gets Scraped

Each email is extracted with the following information:

```json
{
  "sender": "John Doe <john@example.com>",
  "subject": "Meeting Tomorrow",
  "date": "Dec 15",
  "time": "2:30 PM",
  "description": "Email snippet/preview...",
  "is_read": true,
  "has_attachment": false,
  "priority": "normal"
}
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `EMAIL_GMAIL` | Your Gmail email address | Yes |
| `PASSWORD_GMAIL` | Your Gmail app password | Yes |

### Script Customization

**Change max emails to scrape:**
```python
# In scrape_emails_traditional() function
max_emails = 50  # Change this number
```

**Enable filtering examples:**
```python
# In main() function, uncomment these lines:
unread_emails = filter_emails(emails, unread_only=True)
attachment_emails = filter_emails(emails, has_attachment=True)
```

**Start fresh (delete saved session):**
```python
# In main() function, uncomment these lines:
if os.path.exists(STATE_FILE):
    os.remove(STATE_FILE)
```

## 📈 Usage Examples

### Basic Email Scraping
```bash
python gmaiil_check.py
```

### Filter Emails Programmatically
```python
# Filter unread emails
unread_emails = filter_emails(emails, unread_only=True)

# Filter emails with attachments
attachment_emails = filter_emails(emails, has_attachment=True)

# Filter by sender
sender_emails = filter_emails(emails, sender="important@company.com")

# Filter by subject keywords
keyword_emails = filter_emails(emails, subject="meeting")
```

### Email Analysis
The script automatically provides:
- Total email count
- Read vs unread statistics
- Attachment statistics
- Top 5 senders
- Most common words in subjects
- Email activity by hour

## 🏗️ Project Structure

```
AgentQL/
├── gmaiil_check.py          # Main scraping script
├── README.md               # This file
├── .env                    # Environment variables (create this)
├── state.json             # Session state (auto-generated)
├── emails_data.json       # Scraped email data (auto-generated)
├── package.json           # Node.js dependencies
├── playwright.config.js   # Playwright configuration
└── tests/                 # Test files
```

## 🔍 How It Works

### 1. Authentication Flow
- Navigates to Gmail
- Handles Google Workspace redirects
- Clicks "Sign in" button if needed
- Enters credentials using AgentQL
- Saves session state for future use

### 2. Email Scraping
- **AgentQL Method**: Uses intelligent queries to extract email data
- **Traditional Method**: Falls back to CSS selectors if AgentQL fails
- **Simple Method**: Parses row text as final fallback

### 3. Data Processing
- Extracts sender, subject, date, time, description
- Determines read status and attachment presence
- Identifies email priority
- Saves to JSON format

## 🛡️ Security Features

- **App Passwords**: Uses Gmail App Passwords instead of regular passwords
- **Session Management**: Saves login state to avoid repeated authentication
- **Environment Variables**: Keeps credentials secure in `.env` file
- **No Data Storage**: Only processes emails, doesn't store sensitive content

## 🐛 Troubleshooting

### Common Issues

**1. "ElementHandle.get_attribute() takes 2 positional arguments"**
- ✅ **Fixed**: Updated to use correct Playwright API

**2. "Redirected to Google Workspace"**
- ✅ **Fixed**: Added automatic sign-in button detection and clicking

**3. "No emails found"**
- Check if you're logged in properly
- Verify Gmail is loading correctly
- Try increasing the timeout values

**4. "Authentication failed"**
- Verify your `.env` file has correct credentials
- Use an App Password instead of regular password
- Check if 2FA is enabled on your account

**5. "Timeout waiting for emails"**
- Increase timeout values in the script
- Check your internet connection
- Try running with `headless=False` to see what's happening

### Debug Mode

To see what's happening during scraping:
```python
# In main() function, change headless to False:
browser = pw.chromium.launch(headless=False)
```

### Manual Testing

1. **Test login manually:**
   ```bash
   python -c "from gmaiil_check import login; import os; from dotenv import load_dotenv; load_dotenv(); print('Testing login...')"
   ```

2. **Check environment variables:**
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('EMAIL:', os.getenv('EMAIL_GMAIL')); print('PASSWORD:', '***' if os.getenv('PASSWORD_GMAIL') else 'NOT SET')"
   ```

## 📝 Output Files

### `emails_data.json`
Contains all scraped email data in JSON format:
```json
[
  {
    "sender": "example@email.com",
    "subject": "Email Subject",
    "date": "Dec 15",
    "time": "2:30 PM",
    "description": "Email preview...",
    "is_read": true,
    "has_attachment": false,
    "priority": "normal"
  }
]
```

### `state.json`
Contains browser session state for faster subsequent runs.

## 🔄 Advanced Usage

### Custom Email Analysis
```python
# Add custom analysis functions
def custom_email_analysis(emails):
    # Your custom analysis here
    pass

# Call in main() after scraping
custom_email_analysis(emails)
```

### Export to Different Formats
```python
import csv

def save_emails_to_csv(emails, filename="emails.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=emails[0].keys())
        writer.writeheader()
        writer.writerows(emails)
```

### Real-time Monitoring
```python
import time

def monitor_inbox():
    while True:
        emails = scrape_emails(page)
        print(f"Found {len(emails)} emails at {time.strftime('%H:%M:%S')}")
        time.sleep(300)  # Check every 5 minutes
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect Gmail's Terms of Service and use responsibly.

## ⚠️ Disclaimer

- This tool is for personal use only
- Respect Gmail's Terms of Service
- Don't use for spam or malicious purposes
- Be mindful of rate limits
- Use responsibly and ethically

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your environment setup
3. Check the debug output for clues
4. Ensure your Gmail account is accessible
5. Try running with `headless=False` to see the browser

## 🔄 Updates

- **v1.0**: Initial release with basic email scraping
- **v1.1**: Added Google Workspace redirect handling
- **v1.2**: Improved error handling and debugging
- **v1.3**: Added email analysis and filtering features

---

**Happy Scraping! 📧✨** 