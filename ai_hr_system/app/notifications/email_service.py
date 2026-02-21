import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

class EmailService:
    """
    Real asynchronous Email delivery service using SMTP.
    """
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Sends an email using SMTP settings from config.
        """
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("EMAIL SERVICE ERROR: SMTP credentials not set in .env")
            return False

        try:
            # SMTP operations are blocking, run in a separate thread
            return await asyncio.to_thread(self._send_sync, to_email, subject, body)
        except Exception as e:
            print(f"EMAIL SERVICE ERROR: {e}")
            return False

    def _send_sync(self, to_email: str, subject: str, body: str) -> bool:
        """Synchronous part of email sending."""
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        print(f"EMAIL SERVICE: Sending '{subject}' to {to_email}...")
        print(f"EMAIL SERVICE: Using SMTP User: {settings.SMTP_USER}")
        print(f"EMAIL SERVICE: Connecting to {settings.SMTP_SERVER}:{settings.SMTP_PORT}...")
        
        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10) as server:
                server.set_debuglevel(1) # Show full SMTP communication in terminal
                server.starttls() # Secure the connection
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"EMAIL SERVICE: Successfully delivered to {to_email}")
            return True
        except Exception as e:
            print(f"SMTP SYNC ERROR: {e}")
            return False
