import agentql
import os
from playwright.sync_api import sync_playwright
#from pyairtable import Api
from dotenv import load_dotenv
from agentql.ext.playwright.sync_api import Page
import json
from playwright.sync_api import sync_playwright
import agentql
import re


# Import the synchronous playwright library
# This library is used to launch the browser and interact with the web page





URL = "https://accounts.google.com/signin/v2/identifier?service=mail&continue=https://mail.google.com/mail/&hl=en"
INBOX_URL = "https://mail.google.com/mail/u/0/#inbox"
STATE_FILE = "state.json"
#------------------------------------------------Queries------------------------------------->
#We need to provide a query for the email.
EMAIL_INPUT_QUERY="""
    {identifierid{
    input}
    }
"""
#Get Password
PASSWORD_QUERY="""
    {
        password{
            input
    }
    }
"""

EMAIL_DESC="""{
    email_description(description of email named noreply)
}"""

NEXT_BTN_QUERY = """
{
  next
}
"""

SIGN_IN_BTN_QUERY = """
{
  sign_in_button
}
"""

#---------------------------------------------Functions------------------------------------------>
def login(page):
    load_dotenv()
    #Get user info
    USER_NAME=os.getenv("EMAIL_GMAIL")
    PASSWORD=os.getenv("PASSWORD_GMAIL")
    
    #print("USER_NAME repr:", repr(USER_NAME))
    #print("PASSWORD repr: ", repr(PASSWORD))

    # Navigate to the initial URL
    page.goto(URL)

    #Email
    response_email = page.query_elements(EMAIL_INPUT_QUERY)
    response_email.identifierid.input.fill(USER_NAME)
    response = page.query_elements(NEXT_BTN_QUERY)
    response.next.click()
    #page.wait_for_timeout(1000)

    # Password
    response_password = page.query_elements(PASSWORD_QUERY)
    response_password.password.input.fill(PASSWORD)
    response = page.query_elements(NEXT_BTN_QUERY)
    response.next.click()
    #page.wait_for_timeout(1000)

     # — wait until you're actually in Gmail —
    page.wait_for_url("https://mail.google.com/mail/u/0/*", timeout=60_000)
    page.wait_for_selector("tr.zA", timeout=60_000)

    # Additional check to ensure we're on Gmail and not Google Workspace
    current_url = page.url
    print(f"URL after login: {current_url}")
    if "workspace.google.com" in current_url or "mail.google.com" not in current_url:
        print("Login redirected to Google Workspace or non-Gmail URL, trying direct Gmail URL...")
        # If redirected to workspace, try direct Gmail URL
        page.goto("https://mail.google.com/mail/u/0/#inbox", timeout=60_000)
        page.wait_for_selector("tr.zA", timeout=60_000)
        
        # Check if we're still on workspace
        current_url = page.url
        if "workspace.google.com" in current_url:
            print("Still on Google Workspace, trying alternative Gmail URL...")
            # Try different Gmail URLs to force regular Gmail
            gmail_urls = [
                "https://mail.google.com/mail/u/0/",
                "https://mail.google.com/mail/u/0/#inbox",
                "https://mail.google.com/mail/u/0/?ui=2&ik=&view=pt&search=inbox",
                "https://mail.google.com/mail/u/0/?ui=2&ik=&view=pt"
            ]
            
            for gmail_url in gmail_urls:
                try:
                    page.goto(gmail_url, timeout=30_000)
                    page.wait_for_selector("tr.zA", timeout=30_000)
                    current_url = page.url
                    if "mail.google.com" in current_url and "workspace.google.com" not in current_url:
                        print(f"Successfully reached Gmail with URL: {gmail_url}")
                        break
                except Exception as e:
                    print(f"Failed with URL {gmail_url}: {e}")
                    continue
            
        print(f"Final URL after login redirect: {page.url}")
        
    # — now persist the fully‑logged‑in state —
    page.context.storage_state(path=STATE_FILE)
#-------------------------------------------------------------------------------
def open_inbox(page):
            # direct‐nav to the inbox
            page.goto(INBOX_URL, timeout=60_000)
            
            # Check if we're on Google Workspace page
            current_url = page.url
            print(f"Current URL after navigation: {current_url}")
            
            if "workspace.google.com" in current_url:
                print("On Google Workspace page, looking for Sign in button...")
                
                # Try to find and click the Sign in button on Google Workspace using AgentQL
                try:
                    print("Looking for Sign in button using AgentQL...")
                    response = page.query_elements(SIGN_IN_BTN_QUERY)
                    response.sign_in_button.click()
                    print("Clicked Sign in button using AgentQL")
                    sign_in_clicked = True
                    
                    # Wait for navigation to login page
                    page.wait_for_url("**/accounts.google.com/**", timeout=30_000)
                    print("Successfully navigated to Google login page")
                    
                except Exception as e:
                    print(f"AgentQL sign in button not found: {e}")
                    
                    # Fallback to traditional selectors
                    sign_in_clicked = False
                    sign_in_selectors = [
                        "a[href*='signin']",
                        "a[data-action='signin']", 
                        "button[data-action='signin']",
                        "a[aria-label*='Sign in']",
                        "button[aria-label*='Sign in']",
                        "a:has-text('Sign in')",
                        "button:has-text('Sign in')",
                        "a[href*='accounts.google.com']",
                        "a[data-testid='signin']",
                        "button[data-testid='signin']",
                        "a[role='button']:has-text('Sign in')",
                        "button[role='button']:has-text('Sign in')",
                        "a[class*='signin']",
                        "button[class*='signin']",
                        "a[class*='login']",
                        "button[class*='login']",
                        "a[class*='auth']",
                        "button[class*='auth']"
                    ]
                    
                    for selector in sign_in_selectors:
                        try:
                            # Wait for the sign in button to be visible
                            page.wait_for_selector(selector, timeout=5_000)
                            print(f"Found Sign in button with selector: {selector}")
                            
                            # Click the sign in button
                            page.click(selector)
                            print("Clicked Sign in button")
                            sign_in_clicked = True
                            
                            # Wait for navigation to login page
                            page.wait_for_url("**/accounts.google.com/**", timeout=30_000)
                            print("Successfully navigated to Google login page")
                            break
                            
                        except Exception as e:
                            print(f"Selector {selector} not found or click failed: {e}")
                            continue
                
                if not sign_in_clicked:
                    print("Could not find Sign in button, trying direct Gmail URL...")
                    page.goto("https://mail.google.com/mail/u/0/#inbox", timeout=60_000)
                else:
                    # Now we should be on the login page, proceed with login
                    print("Proceeding with login after clicking Sign in...")
                    login(page)
                    return
            
            # Try to wait for Gmail selectors
            try:
                page.wait_for_selector("tr.zA", timeout=10_000)
                print("Found Gmail selector: tr.zA")
            except Exception as e:
                print(f"Gmail selector not found: {e}")
                print("Checking if we need to handle workspace redirect...")
                
                # Check current URL again
                current_url = page.url
                if "workspace.google.com" in current_url:
                    print("Still on Google Workspace, trying alternative Gmail URL...")
                    # Try different Gmail URLs to force regular Gmail
                    gmail_urls = [
                        "https://mail.google.com/mail/u/0/",
                        "https://mail.google.com/mail/u/0/#inbox",
                        "https://mail.google.com/mail/u/0/?ui=2&ik=&view=pt&search=inbox",
                        "https://mail.google.com/mail/u/0/?ui=2&ik=&view=pt"
                    ]
                    
                    for gmail_url in gmail_urls:
                        try:
                            page.goto(gmail_url, timeout=30_000)
                            page.wait_for_selector("tr.zA", timeout=30_000)
                            current_url = page.url
                            if "mail.google.com" in current_url and "workspace.google.com" not in current_url:
                                print(f"Successfully reached Gmail with URL: {gmail_url}")
                                break
                        except Exception as e:
                            print(f"Failed with URL {gmail_url}: {e}")
                            continue
                    
                print(f"Final URL: {page.url}")
    
#----------------------------------------------------------------------------
def scrape_emails(page: Page) -> list:
    """
    Scrape all emails from the Gmail inbox.
    Returns a list of dictionaries containing email information.
    """
    print("Starting email scraping...")
    
    # Wait for emails to load
    try:
        page.wait_for_selector("tr.zA", timeout=30_000)
        print("Emails loaded successfully")
    except Exception as e:
        print(f"Error waiting for emails: {e}")
        return []
    
    # Query to get all emails using AgentQL
    emails_query = """
    {
        emails {
            sender
            subject
            date
            time
            description
            is_read
            has_attachment
            priority
        }
    }
    """
    
    try:
        # Get emails using AgentQL
        response = page.query_data(emails_query)
        print(f"Found {len(response.emails) if hasattr(response, 'emails') else 'unknown'} emails using AgentQL")
        
        if hasattr(response, 'emails') and response.emails:
            emails_data = []
            for email in response.emails:
                email_info = {
                    'sender': getattr(email, 'sender', 'Unknown'),
                    'subject': getattr(email, 'subject', 'No Subject'),
                    'date': getattr(email, 'date', 'Unknown'),
                    'time': getattr(email, 'time', 'Unknown'),
                    'description': getattr(email, 'description', ''),
                    'is_read': getattr(email, 'is_read', False),
                    'has_attachment': getattr(email, 'has_attachment', False),
                    'priority': getattr(email, 'priority', 'normal')
                }
                emails_data.append(email_info)
            
            print(f"Successfully scraped {len(emails_data)} emails")
            return emails_data
            
    except Exception as e:
        print(f"AgentQL email scraping failed: {e}")
        print("Falling back to traditional scraping method...")
    
    # Fallback: Traditional scraping method
    return scrape_emails_traditional(page)

def scrape_emails_traditional(page: Page) -> list:
    """
    Traditional method to scrape emails using CSS selectors.
    """
    emails_data = []
    
    try:
        # Wait for email rows to be present
        page.wait_for_selector("tr.zA", timeout=30_000)
        
        # Get all email rows
        email_rows = page.query_selector_all("tr.zA")
        print(f"Found {len(email_rows)} email rows")
        
        # Debug: Let's see what's in the first few rows
        if email_rows:
            print("Debug: Analyzing first email row structure...")
            first_row = email_rows[0]
            try:
                print(f"Row HTML: {first_row.inner_html()[:500]}...")
                print(f"Row text: {first_row.inner_text()[:200]}...")
            except Exception as debug_error:
                print(f"Debug error: {debug_error}")
        
        # Limit to first 50 emails for performance, but you can increase this
        max_emails = 50
        emails_to_process = min(len(email_rows), max_emails)
        
        for i, row in enumerate(email_rows[:emails_to_process]):
            try:
                # Extract email information using various selectors
                email_info = {}
                
                # First, try to get all text content and parse it
                row_text = row.inner_text()
                if row_text.strip():
                    # Split by newlines and try to extract information
                    lines = [line.strip() for line in row_text.split('\n') if line.strip()]
                    
                    if len(lines) >= 1:
                        email_info['sender'] = lines[0]
                    if len(lines) >= 2:
                        email_info['subject'] = lines[1]
                    if len(lines) >= 3:
                        email_info['description'] = lines[2]
                    if len(lines) >= 4:
                        email_info['date'] = lines[-1]  # Usually date is at the end
                        email_info['time'] = lines[-1]
                    
                    # Set defaults for missing fields
                    email_info.setdefault('sender', 'Unknown')
                    email_info.setdefault('subject', 'No Subject')
                    email_info.setdefault('description', '')
                    email_info.setdefault('date', 'Unknown')
                    email_info.setdefault('time', 'Unknown')
                    email_info.setdefault('is_read', True)  # Assume read if we can see it
                    email_info.setdefault('has_attachment', False)
                    email_info.setdefault('priority', 'normal')
                    
                    emails_data.append(email_info)
                    print(f"Scraped email {i+1} (simple method): {email_info['sender']} - {email_info['subject']}")
                    continue
                
                # Sender
                sender_elem = row.query_selector("td.xY.xX span.yP")
                if sender_elem:
                    email_info['sender'] = sender_elem.inner_text().strip()
                else:
                    # Try alternative sender selectors
                    sender_selectors = [
                        "span.yP",
                        "span[email]",
                        "td.xY.xX span",
                        "span[data-thread-id]",
                        "td[role='gridcell'] span",
                        "span[data-thread-id]",
                        "td.xY.xX div span",
                        "span[title*='@']"
                    ]
                    for selector in sender_selectors:
                        sender_elem = row.query_selector(selector)
                        if sender_elem:
                            email_info['sender'] = sender_elem.inner_text().strip()
                            break
                    else:
                        email_info['sender'] = 'Unknown'
                
                # Subject
                subject_elem = row.query_selector("td.xY.xX span.y6")
                if subject_elem:
                    email_info['subject'] = subject_elem.inner_text().strip()
                else:
                    # Try alternative subject selectors
                    subject_selectors = [
                        "span.y6",
                        "span[data-thread-id]",
                        "td.xY.xX span:not(.yP)",
                        "td[role='gridcell'] span:not([title*='@'])",
                        "span[data-legacy-message-id]",
                        "td.xY.xX div span",
                        "span[title]:not([title*='@'])"
                    ]
                    for selector in subject_selectors:
                        subject_elem = row.query_selector(selector)
                        if subject_elem:
                            email_info['subject'] = subject_elem.inner_text().strip()
                            break
                    else:
                        email_info['subject'] = 'No Subject'
                
                # Date/Time
                date_elem = row.query_selector("td.xW.xY span.xT")
                if date_elem:
                    email_info['date'] = date_elem.inner_text().strip()
                    email_info['time'] = date_elem.inner_text().strip()
                else:
                    # Try alternative date selectors
                    date_selectors = [
                        "span.xT",
                        "td.xW.xY span",
                        "span[title*=':']",
                        "td[role='gridcell'] span[title]",
                        "span[title*='PM']",
                        "span[title*='AM']",
                        "span[title*='202']",
                        "td.xW.xY div span"
                    ]
                    for selector in date_selectors:
                        date_elem = row.query_selector(selector)
                        if date_elem:
                            date_text = date_elem.inner_text().strip()
                            email_info['date'] = date_text
                            email_info['time'] = date_text
                            break
                    else:
                        email_info['date'] = 'Unknown'
                        email_info['time'] = 'Unknown'
                
                # Description/Snippet
                snippet_elem = row.query_selector("td.xY.xX span.y2")
                if snippet_elem:
                    email_info['description'] = snippet_elem.inner_text().strip()
                else:
                    # Try alternative snippet selectors
                    snippet_selectors = [
                        "span.y2",
                        "span[data-thread-id] + span",
                        "td.xY.xX span:not(.yP):not(.y6)"
                    ]
                    for selector in snippet_selectors:
                        snippet_elem = row.query_selector(selector)
                        if snippet_elem:
                            email_info['description'] = snippet_elem.inner_text().strip()
                            break
                    else:
                        email_info['description'] = ''
                
                # Read status
                email_info['is_read'] = 'zA' in (row.get_attribute('class') or '')
                
                # Attachment indicator
                attachment_elem = row.query_selector("span.TK")
                email_info['has_attachment'] = attachment_elem is not None
                
                # Priority (starred, important, etc.)
                priority_elem = row.query_selector("span.T-KT")
                email_info['priority'] = 'important' if priority_elem else 'normal'
                
                # If we couldn't get proper data, try a fallback approach
                if email_info['sender'] == 'Unknown' and email_info['subject'] == 'No Subject':
                    try:
                        # Get all text from the row and try to parse it
                        row_text = row.inner_text()
                        if row_text.strip():
                            # Split by common delimiters and take the first few parts
                            parts = row_text.split('\n')
                            if len(parts) >= 2:
                                email_info['sender'] = parts[0].strip()
                                email_info['subject'] = parts[1].strip()
                                if len(parts) >= 3:
                                    email_info['description'] = parts[2].strip()
                    except Exception as fallback_error:
                        print(f"Fallback parsing failed for email {i+1}: {fallback_error}")
                
                emails_data.append(email_info)
                print(f"Scraped email {i+1}: {email_info['sender']} - {email_info['subject']}")
                
            except Exception as e:
                print(f"Error scraping email {i+1}: {e}")
                continue
        
        print(f"Successfully scraped {len(emails_data)} emails using traditional method")
        return emails_data
        
    except Exception as e:
        print(f"Traditional email scraping failed: {e}")
        return []

def save_emails_to_file(emails: list, filename: str = "emails_data.json"):
    """
    Save scraped emails to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)
        print(f"Emails saved to {filename}")
    except Exception as e:
        print(f"Error saving emails to file: {e}")

def display_emails_summary(emails: list):
    """
    Display a summary of scraped emails.
    """
    if not emails:
        print("No emails found.")
        return
    
    print(f"\n=== EMAIL SUMMARY ===")
    print(f"Total emails: {len(emails)}")
    
    # Count read vs unread
    read_count = sum(1 for email in emails if email.get('is_read', False))
    unread_count = len(emails) - read_count
    print(f"Read: {read_count}, Unread: {unread_count}")
    
    # Count emails with attachments
    attachment_count = sum(1 for email in emails if email.get('has_attachment', False))
    print(f"Emails with attachments: {attachment_count}")
    
    # Show first few emails
    print(f"\n=== FIRST 5 EMAILS ===")
    for i, email in enumerate(emails[:5]):
        print(f"{i+1}. From: {email.get('sender', 'Unknown')}")
        print(f"   Subject: {email.get('subject', 'No Subject')}")
        print(f"   Date: {email.get('date', 'Unknown')}")
        print(f"   Read: {'Yes' if email.get('is_read', False) else 'No'}")
        print(f"   Attachment: {'Yes' if email.get('has_attachment', False) else 'No'}")
        print()

def filter_emails(emails: list, **filters) -> list:
    """
    Filter emails based on various criteria.
    
    Args:
        emails: List of email dictionaries
        **filters: Keyword arguments for filtering
            - sender: Filter by sender email/name
            - subject: Filter by subject keywords
            - unread_only: Show only unread emails
            - has_attachment: Show only emails with attachments
            - priority: Filter by priority (important/normal)
    
    Returns:
        Filtered list of emails
    """
    filtered_emails = emails.copy()
    
    if 'sender' in filters:
        sender_filter = filters['sender'].lower()
        filtered_emails = [email for email in filtered_emails 
                          if sender_filter in email.get('sender', '').lower()]
    
    if 'subject' in filters:
        subject_filter = filters['subject'].lower()
        filtered_emails = [email for email in filtered_emails 
                          if subject_filter in email.get('subject', '').lower()]
    
    if filters.get('unread_only', False):
        filtered_emails = [email for email in filtered_emails 
                          if not email.get('is_read', False)]
    
    if filters.get('has_attachment', False):
        filtered_emails = [email for email in filtered_emails 
                          if email.get('has_attachment', False)]
    
    if 'priority' in filters:
        priority_filter = filters['priority'].lower()
        filtered_emails = [email for email in filtered_emails 
                          if email.get('priority', 'normal').lower() == priority_filter]
    
    return filtered_emails

def analyze_emails(emails: list):
    """
    Analyze email patterns and provide insights.
    """
    if not emails:
        print("No emails to analyze.")
        return
    
    print(f"\n=== EMAIL ANALYSIS ===")
    
    # Top senders
    sender_counts = {}
    for email in emails:
        sender = email.get('sender', 'Unknown')
        sender_counts[sender] = sender_counts.get(sender, 0) + 1
    
    top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"Top 5 senders:")
    for sender, count in top_senders:
        print(f"  {sender}: {count} emails")
    
    # Subject analysis
    subjects = [email.get('subject', '') for email in emails]
    common_words = {}
    for subject in subjects:
        words = subject.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                common_words[word] = common_words.get(word, 0) + 1
    
    top_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nMost common words in subjects:")
    for word, count in top_words:
        print(f"  '{word}': {count} times")
    
    # Time analysis
    time_patterns = {}
    for email in emails:
        time_str = email.get('time', '')
        if time_str and ':' in time_str:
            hour = time_str.split(':')[0]
            time_patterns[hour] = time_patterns.get(hour, 0) + 1
    
    if time_patterns:
        print(f"\nEmail activity by hour:")
        for hour in sorted(time_patterns.keys()):
            print(f"  {hour}:00 - {time_patterns[hour]} emails")
#----------------------------------------------------------------------------
def main():
    # load .env and configure AgentQL
    load_dotenv()
    #agentql.configure({ "apiKey": os.getenv("AGENTQL_API_KEY") })
    
    # Uncomment the next line if you want to start fresh (delete saved session)
    # if os.path.exists(STATE_FILE):
    #     os.remove(STATE_FILE)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)

        # 1) Create or load a context with saved state
        if os.path.exists(STATE_FILE):
            context = browser.new_context(storage_state=STATE_FILE)
        else:
            context = browser.new_context()

        # 2) Wrap one page in that context
        page = agentql.wrap(context.new_page())

        # 3) If we haven’t logged in yet, do it now on *this* page
        if not os.path.exists(STATE_FILE):
            # First try to go to Gmail directly
            page.goto(INBOX_URL, timeout=60_000)
            
            # Check if we're redirected to Google Workspace
            current_url = page.url
            if "workspace.google.com" in current_url:
                print("Redirected to Google Workspace, handling sign-in flow...")
                open_inbox(page)  # This will handle the sign-in button click
            else:
                # If we're already on Gmail, proceed with login
                page.goto(URL, timeout=60_000)
                login(page)
                # After login, go to inbox on the same page
                open_inbox(page)
        else:
            # If we have saved state, just go directly to inbox
            open_inbox(page)

        # 5) Scrape emails from the inbox
        print("\n=== STARTING EMAIL SCRAPING ===")
        emails = scrape_emails(page)
        
        if emails:
            # Display summary
            display_emails_summary(emails)
            
            # Save to file
            save_emails_to_file(emails)
            
            # Analyze emails
            analyze_emails(emails)
            
            # Example filtering (uncomment to use)
            # unread_emails = filter_emails(emails, unread_only=True)
            # print(f"\nUnread emails: {len(unread_emails)}")
            
            # attachment_emails = filter_emails(emails, has_attachment=True)
            # print(f"Emails with attachments: {len(attachment_emails)}")
            
        else:
            print("No emails were scraped.")

        context.close()
        browser.close()
    
#---------------------------------Main----------------------------->
if __name__ == "__main__":
    main()
