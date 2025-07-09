#!/usr/bin/env python
import sys
import os
import warnings
import time
import json
import threading
from datetime import datetime
from emailcrew.crew import Emailcrew
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from emailcrew.send_outlook_email import *

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


'''
TODO:
convert to django

multi user support

file path issue -> providde direct link instead

User control -> Change time -> goback to main screen

HOW TO RUN
python manage.py runserver
'''

# Function for running the crew
def run_crew_and_send_mail(receiver, file_path=None):
    syntax = {
        "message": {
            "subject": "Subject Goes Here",
            "body": {
                "contentType": "Text",
                "content": "all the content of the mail"
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": receiver
                    }
                }
            ]
        },
        "saveToSentItems": True
    }

    onedrive_file_path = file_path or "/Email Agent File/user_preference.txt"

    inputs = {
        'topic': 'Providing update and explanation of the document',
        'my_name': 'Mahad Rehman',
        'my_signature': 'Computer Science Department\nFAST NUCES Islamabad',
        'recipient_name': 'Sir',
        'colleague_name': 'Sherlock Holmes',
        'colleague_number': '+92 123456789',
        'current_date': str(datetime.now()),
        'application': 'outlook',
        'syntax': syntax
    }

    try:
        onedrive_file = download_file_from_onedrive(onedrive_file_path)
        if not onedrive_file:
            raise RuntimeError("Download failed")

        inputs["attachment_name"] = onedrive_file
        attachment_file = os.path.join(os.getcwd(), "knowledge", onedrive_file)
        txt_file = convert_to_txt(attachment_file)

        relative_path = os.path.relpath(txt_file, os.path.join(os.getcwd(), "knowledge"))

        with open(txt_file, "r") as file_object:
            content = file_object.read()
        inputs["attachment_content"] = content

        crew_obj = Emailcrew(relative_path)
        crew = crew_obj.crew()
        result = crew.kickoff(inputs=inputs)

        if isinstance(result, dict):
            email_payload = result
        elif isinstance(result, str):
            email_payload = json.loads(result)
        else:
            import re
            m = re.search(r"\{(?:.|\s)*\}", str(result))
            if not m:
                raise ValueError("No JSON block found in CrewAI result.")
            email_payload = json.loads(m.group(0))

        send_mail(email_payload, attachment_file)

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


# 🕑 Weekly Schedule Function
def wait_until_schedule_and_run_every_week(user_time, user_day, file_name=None, receiver="i220792@nu.edu.pk", stop_event=None):
    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }

    if user_day not in days_map:
        print("❌ Invalid day entered.")
        return

    try:
        scheduled_hour, scheduled_minute = map(int, user_time.split(":"))
    except:
        print("❌ Invalid time format. Use HH:MM in 24-hour format.")
        return

    print(f"✅ Scheduled to run every {user_day.capitalize()} at {user_time}")
    print("⏳ Waiting for the scheduled time. Press Ctrl+C to exit.")

    already_sent_today = False

    while not (stop_event and stop_event.is_set()):
        now = datetime.now()
        is_target_day = now.weekday() == days_map[user_day]
        is_target_time = now.hour == scheduled_hour and now.minute == scheduled_minute

        if is_target_day and is_target_time:
            if not already_sent_today:
                print(f"🚀 Running the crew at {now}")
                run_crew_and_send_mail(receiver, file_name)
                already_sent_today = True
        else:
            already_sent_today = False

        time.sleep(30)

    print("🛑 Schedule cancelled. Exiting current schedule thread.")


# 🔄 Shared schedule control
_schedule_config = {}
_schedule_event = threading.Event()
_current_scheduler_thread = None
_stop_event = None

def set_schedule_config(receiver, filepath, day, time):
    global _schedule_config
    _schedule_config = {
        'receiver': receiver,
        'filepath': filepath,
        'day': day.lower(),
        'time': time
    }
    _schedule_event.set()


# 🧠 Main run loop
def run():
    global _current_scheduler_thread, _stop_event

    print("🚦 Email Scheduler Ready. Waiting for configuration via Django...")

    while True:
        _schedule_event.wait()
        print("🚦 Received new schedule configuration!")

        if _stop_event is not None:
            print("🛑 Stopping previous scheduler...")
            _stop_event.set()
            _current_scheduler_thread.join()

        _stop_event = threading.Event()

        receiver = _schedule_config['receiver']
        file_path = _schedule_config['filepath']
        day = _schedule_config['day']
        schedule_time = _schedule_config['time']

        print("📄 File:", file_path)
        print("📅 Day:", day)
        print("⏰ Time:", schedule_time)

        _schedule_event.clear()

        _current_scheduler_thread = threading.Thread(
            target=wait_until_schedule_and_run_every_week,
            args=(schedule_time, day, file_path, receiver, _stop_event),
            daemon=True
        )
        _current_scheduler_thread.start()


# Other CrewAI utilities
def train():
    inputs = {
        "topic": "AI LLMs",
        'current_date': str(datetime.now())
    }
    try:
        Emailcrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    try:
        Emailcrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    inputs = {
        "topic": "AI LLMs",
        "current_date": str(datetime.now())
    }
    try:
        Emailcrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
