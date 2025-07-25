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
# TODO:
# convert to django

# multi user support

# file path issue -> providde direct link instead

# User control -> Change time -> goback to main screen

# HOW TO RUN
# python manage.py runserver
# '''


# Run the Crew and send mail
# def run_crew_and_send_mail(receiver, file_path=None):
def run_crew_and_send_mail(receiver,
                           file_path=None,
                           topic=None,
                           my_name=None,
                           recipient_name=None):
 
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

    # onedrive_file_path = file_path or "https://1drv.ms/t/c/901cffeb62aca0b5/EatxEQM0bMRDhpcT5-umeF4BOxtRDKMdkxuJpe20PWyuJg?e=bLhKRV"
    onedrive_file_path = file_path or ""

    # inputs = {
    #     'topic': 'email saying look at the attachment which is the work',
    #     'my_name': 'Mahad Rehman',
    #     'recipient_name': 'Sir',
    #     'current_date': str(datetime.now()),
    #     'application': 'outlook',
    #     'syntax': syntax
    # }

    inputs = {
        'topic':          topic,
        'my_name':        my_name,
        'recipient_name': recipient_name,
        'current_date':   str(datetime.now()),
        'application':    'outlook',
        'syntax':         syntax
    }  
    try:
        # onedrive_file = download_file_from_onedrive(onedrive_file_path)
        access_token = get_silent_token()

        # Download the file from OneDrive using the token
        onedrive_file = download_file_from_onedrive(access_token, onedrive_file_path)
        if not onedrive_file:
            raise RuntimeError("Download failed")

        inputs["attachment_name"] = onedrive_file
        attachment_file = os.path.join(os.getcwd(), "knowledge", onedrive_file)

        # Summary Logic Commented
        # txt_file = convert_to_txt(attachment_file)

        # relative_path = os.path.relpath(txt_file, os.path.join(os.getcwd(), "knowledge"))

        # with open(txt_file, "r", encoding="utf-8") as file_object:
        #     content = file_object.read()
        # inputs["attachment_content"] = content

        # crew_obj = Emailcrew(relative_path)

        crew_obj = Emailcrew()
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

        send_mail(access_token, email_payload, attachment_file)


    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


# # Scheduler thread target function
# def wait_until_schedule_and_run_every_week(user_time, user_day, file_name=None, receiver="i220792@nu.edu.pk", stop_event=None):
#     days_map = {
#         'monday': 0, 'tuesday': 1, 'wednesday': 2,
#         'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
#     }

#     if user_day not in days_map:
#         print("❌ Invalid day entered.")
#         return

#     try:
#         scheduled_hour, scheduled_minute = map(int, user_time.split(":"))
#     except:
#         print("❌ Invalid time format. Use HH:MM in 24-hour format.")
#         return

#     print(f"✅ Scheduled to run every {user_day.capitalize()} at {user_time}")
#     print("⏳ Waiting for the scheduled time. Press Ctrl+C to exit.")

#     target_weekday = days_map[user_day.lower()]

#     last_run_date = None

#     while not (stop_event and stop_event.is_set()):
#         now = datetime.now()
#         # Check if it's the scheduled weekday and time
#         if (now.weekday() == target_weekday and
#             now.hour == scheduled_hour and
#             now.minute == scheduled_minute):

#             current_date = now.date()
#             # Ensure we only run once per day
#             if last_run_date != current_date:
#                 print(f"🚀 Running the crew at {now}")
#                 try:
#                     run_crew_and_send_mail(receiver, file_name)
#                 except Exception as e:
#                     print("❌ Error in scheduled run:", e)
#                 last_run_date = current_date
#         # Sleep until next minute boundary to reduce wake-ups
#         sleep_seconds = 60 - now.second
#         time.sleep(sleep_seconds)

#     print("🛑 Schedule cancelled. Exiting schedule thread.")
#     # already_sent_today = False

#     # while not (stop_event and stop_event.is_set()):
#     #     now = datetime.now()
#     #     is_target_day = now.weekday() == days_map[user_day]
#     #     is_target_time = now.hour == scheduled_hour and now.minute == scheduled_minute

#     #     if is_target_day and is_target_time:
#     #         if not already_sent_today:
#     #             print(f"🚀 Running the crew at {now}")
#     #             run_crew_and_send_mail(receiver, file_name)
#     #             already_sent_today = True
#     #     else:
#     #         already_sent_today = False

#     #     time.sleep(30)

#     # print("🛑 Schedule cancelled. Exiting schedule thread.")

# Scheduler thread target function
# def wait_until_schedule_and_run_every_week(user_time, user_day, file_name=None, receiver="i220792@nu.edu.pk", stop_event=None):
def wait_until_schedule_and_run_every_week(user_time, user_day,
        file_name, receiver,
        topic, my_name, recipient_name,
        stop_event):
    
    from datetime import datetime
    import time

    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }

    if user_day.lower() not in days_map:
        print("❌ Invalid day entered.")
        return

    try:
        scheduled_hour, scheduled_minute = map(int, user_time.split(":"))
    except ValueError:
        print("❌ Invalid time format. Use HH:MM in 24-hour format.")
        return

    target_weekday = days_map[user_day.lower()]
    last_run_minute = None  # will store a string "YYYY-MM-DD HH:MM"

    print(f"✅ Scheduled to run every {user_day.capitalize()} at {user_time}")
    print("⏳ Waiting for the scheduled time. Press Ctrl+C to exit.")

    while not (stop_event and stop_event.is_set()):
        now = datetime.now()
        # Are we on the right day/hour/minute?
        if now.weekday() == target_weekday and now.hour == scheduled_hour and now.minute == scheduled_minute:
            current_stamp = now.strftime("%Y-%m-%d %H:%M")
            if current_stamp != last_run_minute:
                print(f"🚀 Running the crew at {now}")
                try:
                    # run_crew_and_send_mail(receiver, file_name)
                    run_crew_and_send_mail(
                        receiver, file_name,
                        topic=topic,
                        my_name=my_name,
                        recipient_name=recipient_name
                    )
                except Exception as e:
                    print("❌ Error in scheduled run:", e)
                last_run_minute = current_stamp

        # Sleep a bit and check again
        time.sleep(5)

    print("🛑 Schedule cancelled. Exiting schedule thread.")



# Global schedule registry and lock
_schedule_registry = {}
_schedule_registry_lock = threading.Lock()

# Receive schedule request from Django
# def set_schedule_config(receiver, filepath, day, time):
    # # thread_key = f"{receiver}_{day.lower()}_{time}"
    # thread_key = f"{receiver.strip().lower()}_{day.lower()}_{time}"
    # with _schedule_registry_lock:
    #     if thread_key in _schedule_registry:
    #         print(f"⚠️ Schedule for {thread_key} already exists. Ignoring duplicate.")
    #         return
def set_schedule_config(receiver, filepath, day, time,
                       topic, my_name, recipient_name):

    thread_key = f"{receiver.strip().lower()}_{day.lower()}_{time}"

    with _schedule_registry_lock:
        if thread_key in _schedule_registry:
            print(f"⚠️ Schedule for {thread_key} already exists. Ignoring duplicate.")
            return

        # Double-check: has this thread already been started in DB?
        for key in _schedule_registry:
            if receiver in key and day.lower() in key and time in key:
                print(f"⚠️ Duplicate schedule thread already exists under a different key: {key}")
                return
            
        stop_event = threading.Event()
        # schedule_thread = threading.Thread(
        #     target=wait_until_schedule_and_run_every_week,
        #     args=(time, day.lower(), filepath, receiver, stop_event),

        schedule_thread = threading.Thread(
            target=wait_until_schedule_and_run_every_week,
            args=(time, day.lower(), filepath, receiver,
                  topic, my_name, recipient_name,
                  stop_event),

            daemon=True
        )
        _schedule_registry[thread_key] = {
            "thread": schedule_thread,
            "stop_event": stop_event
        }
        print("🧵 Current scheduled threads:")
        for key in _schedule_registry:
            print(f"   • {key}")
            
        print("🚦 Received new schedule configuration!")
        print("📄 File:", filepath)
        print("📅 Day:", day)
        print("⏰ Time:", time)

        schedule_thread.start()


# Persistent run loop
def run():
    print("🚦 Email Scheduler Ready. Waiting for configuration via Django...")
    while True:
        time.sleep(5)  # Keeps main thread alive


# Optional tools
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
