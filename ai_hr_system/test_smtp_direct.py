import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_smtp():
    server_addr = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")

    print(f"Testing SMTP for {user} on {server_addr}:{port}...")

    if not user or not password:
        print("ERROR: SMTP_USER or SMTP_PASSWORD not set in .env")
        return

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = user # Send to self
    msg['Subject'] = "SMTP Diagnostic Test"
    msg.attach(MIMEText("This is a test email from the AI HR System diagnostic script.", 'plain'))

    try:
        print("Connecting to server...")
        server = smtplib.SMTP(server_addr, port, timeout=15)
        server.set_debuglevel(1) # Show full SMTP log
        
        print("Starting TLS...")
        server.starttls()
        
        print("Logging in...")
        server.login(user, password)
        
        print("Sending message...")
        server.send_message(msg)
        
        server.quit()
        print("\n[SUCCESS] Email sent successfully! Please check your inbox (and spam).")
    except smtplib.SMTPAuthenticationError:
        print("\n[FAILURE] Authentication failed. Check your App Password.")
    except Exception as e:
        print(f"\n[FAILURE] An error occurred: {e}")

if __name__ == "__main__":
    test_smtp()
