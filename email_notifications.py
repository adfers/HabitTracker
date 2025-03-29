"""
Module to handle email notifications for the Python learning tracker.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import streamlit as st

# Global settings
DEFAULT_REMINDER_TIME = "09:00"  # 9:00 AM
DEFAULT_REMINDER_MESSAGE = "Remember to practice Python today! Your scheduled topic: {topic}"
DEFAULT_SENDER_EMAIL = "pythonlearningtracker@gmail.com"  # Using the app's Gmail address

def send_email(to_email, subject, message):
    """
    Send an email to the given email address with the specified subject and message.
    
    Args:
        to_email: The recipient's email address
        subject: The email subject
        message: The email message body (HTML formatted)
        
    Returns:
        True if successful, False otherwise
    """
    # This will use the app's email to send notifications
    sender_email = DEFAULT_SENDER_EMAIL
    password = os.environ.get("EMAIL_PASSWORD", "")
    
    if not password:
        st.error("Email password not configured. Please add EMAIL_PASSWORD to environment variables.")
        return False
    
    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    
    # Add HTML message body
    msg.attach(MIMEText(message, "html"))
    
    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        
        # Send the email
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False


def send_reminder(email, day_info):
    """
    Send a reminder email about today's Python learning topic.
    
    Args:
        email: The recipient's email address
        day_info: Information about the day's topic
        
    Returns:
        True if successful, False otherwise
    """
    # Prepare the message
    subject = "Python Learning Reminder"
    message = f"""
    <html>
    <body>
    <h2>Python Learning Tracker - Daily Reminder</h2>
    <p>Hello Python learner!</p>
    <p>This is a friendly reminder about today's learning topic:</p>
    <div style="background-color: #f0f8ff; padding: 15px; border-left: 5px solid #3366cc; margin: 10px 0;">
        <h3>Day {day_info['day']}: {day_info['topic']}</h3>
        <p><strong>Practice:</strong> {day_info['practice']}</p>
        <p><strong>Scheduled for:</strong> {day_info['formatted_date']}</p>
    </div>
    <p>Don't forget to mark your progress in the Python Learning Tracker!</p>
    <p>Happy coding!</p>
    </body>
    </html>
    """
    
    # Send the email
    return send_email(email, subject, message)


def send_missed_day_notification(email, day_info):
    """
    Send a notification when a day of learning is missed.
    
    Args:
        email: The recipient's email address
        day_info: Information about the missed day
        
    Returns:
        True if successful, False otherwise
    """
    subject = "Python Learning - Missed Practice Day"
    message = f"""
    <html>
    <body>
    <h2>Python Learning Tracker - Missed Day Alert</h2>
    <p>Hello Python learner!</p>
    <p>We noticed you missed your Python practice yesterday. Don't worry - it happens to everyone!</p>
    <div style="background-color: #fff0f0; padding: 15px; border-left: 5px solid #dc3545; margin: 10px 0;">
        <h3>Today's topic: Day {day_info['day']}: {day_info['topic']}</h3>
        <p>Why not catch up today? Remember, consistency is key to learning programming!</p>
    </div>
    <p>Don't break your learning streak - a little practice every day is better than a long session once a week.</p>
    <p>Happy coding!</p>
    </body>
    </html>
    """
    
    return send_email(email, subject, message)


def check_and_send_daily_reminder(email, reminder_time, day_info):
    """
    Check if it's time to send a daily reminder and send if needed.
    
    Args:
        email: The recipient's email address
        reminder_time: The time to send the reminder (format: "HH:MM")
        day_info: Information about the day's topic
        
    Returns:
        True if reminder was sent, False otherwise
    """
    now = datetime.now()
    
    # Parse reminder time
    try:
        hour, minute = map(int, reminder_time.split(':'))
        reminder_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Check if it's time to send the reminder (within the last 5 minutes)
        time_diff = (now - reminder_datetime).total_seconds()
        if 0 <= time_diff < 300:  # Within 5 minutes after reminder time
            return send_reminder(email, day_info)
    except (ValueError, AttributeError):
        pass
    
    return False


def check_for_missed_days(email, progress_data, current_day_info):
    """
    Check if any days were missed and send notifications.
    
    Args:
        email: The recipient's email address
        progress_data: The progress data for all days
        current_day_info: Information about the current day
        
    Returns:
        True if notification was sent, False otherwise
    """
    now = datetime.now()
    yesterday = (now - timedelta(days=1)).date()
    
    # Find yesterday's day in the curriculum
    yesterday_idx = None
    for i, day_data in enumerate(progress_data):
        day_scheduled_date = day_data.get('scheduled_date')
        if day_scheduled_date and day_scheduled_date.date() == yesterday:
            yesterday_idx = i
            break
    
    if yesterday_idx is not None:
        # Check if yesterday was completed
        yesterday_completed = progress_data[yesterday_idx].get('completed', False)
        if not yesterday_completed:
            # Send notification about missed day
            return send_missed_day_notification(email, current_day_info)
    
    return False