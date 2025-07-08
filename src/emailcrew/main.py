#!/usr/bin/env python
import sys
import os
import warnings
# import logging
# logging.getLogger("crewai").setLevel(logging.DEBUG)
import time
from datetime import datetime
from emailcrew.crew import Emailcrew
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from send_outlook_email import *
import ast
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import json

from flask import Flask, render_template, request
app = Flask(__name__)


def run_crew_and_send_mail(file_path = None):
    # syntax = {
    #         "message": {
    #             "subject": "Subject Goes Here",
    #             "body": {
    #                 "contentType": "Text",
    #                 "content": "all the content of the mail"
    #             },

    #             "toRecipients": [
    #                 {
    #                     "emailAddress": {
    #                         # "address": "faizan.wasif@bluescarf.ai"
    #                         "address": "i220792@nu.edu.pk"
    #                     }
    #                 }
    #             ]
    #         },
    #         "saveToSentItems": "true"
    #     }                            
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
                        "address": "i220792@nu.edu.pk"
                        # "address": "faizan.wasif@bluescarf.ai"
                    }
                }
            ]
        },
        "saveToSentItems": True  # Correct: boolean, and outside "message"
    }

    if file_path:
        onedrive_file_path = file_path
    else:
        onedrive_file_path = "/Email Agent File/document.txt"


    inputs = {
        'topic': 'Someone Stole Goods from Sherlocks Holmes office',
        # 'topic': 'Providing update and explanation of the document',
        'my_name': 'Mahad Rehman',
        'my_signature': 'Computer Science Department\nFAST NUCES Islamabad',
        'recipient_name': 'Sir Faizan',
        'colleague_name': 'Sherlock Holmes' ,
        'colleague_number' : '+92 123456789',
        'current_date': str(datetime.now()),
        'application' : 'outlook',      #can be anything
        'syntax' : syntax,
        # 'information' : 'people name and stuff'              #can i stop and ask the user for it?
    }
    
    try:
        # Downloading the file from OneDrive
        onedrive_file = download_file_from_onedrive(onedrive_file_path)
        if not onedrive_file:
            raise RuntimeError("Download failed")

        # Store just the filename in inputs for the agent to see
        inputs["attachment_name"] = onedrive_file

        # Converting docx/pdf to txt
        attachment_file = os.path.join(os.getcwd(), "knowledge", onedrive_file)
        txt_file = convert_to_txt(attachment_file)

        # Creating the knowledge source
        relative_path = os.path.relpath(txt_file, os.path.join(os.getcwd(), "knowledge"))

        print("📄 Text file generated:", txt_file)
        print("📄 Relative path used for CrewAI:", relative_path)
        print("📂 Current working directory:", os.getcwd())

        # knowledge_source = TextFileKnowledgeSource(file_paths=[txt_path])

        # Create the crew
        crew_obj = Emailcrew(relative_path)
        crew = crew_obj.crew()

        ks = crew_obj.knowledge_source
        print("🧠 Agent knowledge sources:", ks)
        print("🧩 Final chunk count:", len(ks.chunks))


        # Run the crew
        result = crew.kickoff(inputs=inputs)

        try:
            if isinstance(result, dict):
                email_payload = result
            elif isinstance(result, str):
                email_payload = json.loads(result)  # Try loading directly if it's a JSON string
            else:
                # Try to extract JSON-looking substring from the stringified object
                m = re.search(r"\{(?:.|\s)*\}", str(result))
                if not m:
                    raise ValueError("No JSON block found in CrewAI result.")
                email_payload = json.loads(m.group(0))  # Use JSON instead of ast
        except Exception as e:
            raise Exception(f"❌ Failed to parse CrewAI output: {e}\nRaw Output: {result}")


        # Extract the JSON payload from CrewOutput
        # raw = str(result)
        # m = re.search(r"\{(?:.|\s)*\}", raw)
        # if not m:
        #     raise ValueError("No dict literal found in CrewOutput")
        # email_payload = ast.literal_eval(m.group(0))

        # Send the email, attaching the original downloaded file
        attachment_file = os.path.join(os.getcwd(), "knowledge", onedrive_file)
        send_mail(email_payload, attachment_file)

        return
    
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


# Schedule Fnuction
def wait_until_schedule_and_run_every_week(user_time, user_day, file_name = None):

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

    while True:
        if already_sent_today:
            print("\n---------------------------------------\nSent successfully, waiting for next week\n---------------------------------------\n")

        now = datetime.now()
        is_target_day = now.weekday() == days_map[user_day]
        is_target_time = now.hour == scheduled_hour and now.minute == scheduled_minute

        if is_target_day and is_target_time:
            if not already_sent_today:
                print(f"🚀 Running the crew at {now}")
                run_crew_and_send_mail(file_name)
                already_sent_today = True
        else:
            already_sent_today = False  # Reset flag when it's not the scheduled time

        time.sleep(30)


@app.route('/', methods=['GET', 'POST'])
def schedule_email():
    if request.method == 'POST':
        filepath = request.form['filepath']
        day = request.form['day'].lower()
        time = request.form['time']

        # Save to JSON
        schedule_data = {
            "filepath": filepath,
            "day": day,
            "time": time
        }
        with open("schedule_config.json", "w") as f:
            json.dump(schedule_data, f)

        return f"✅ Scheduled email every {day.capitalize()} at {time} using {filepath}"
    
    return render_template('index.html')

import threading

def run_flask():
    app.run(debug=False, use_reloader=False)

'''

conda deactivate
cd Python3.11
conda activate venv/
cd emailcrew
crewai run
'''


def run():
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("🌐 Flask app running in background. Waiting for schedule_config.json...")

    # Wait until user submits form
    import time
    while True:
        try:
            with open("schedule_config.json", "r") as f:
                config = json.load(f)
                break
        except FileNotFoundError:
            time.sleep(2)

    # Extract config
    file_path = config['filepath']
    day = config['day']
    schedule_time = config['time']

    print("📄 File:", file_path)
    print("📅 Day:", day)
    print("⏰ Time:", schedule_time)

    wait_until_schedule_and_run_every_week(schedule_time, day, file_path)

# def run():
#     """
#     Run the crew.
#     """
#     app.run(debug=True)


#     print("🗓️ Please input the day and time to schedule the weekly email.")
#     user_day = input("Enter the day of the week (e.g., Monday): ").strip().lower()
#     user_time = input("Enter the time in 24-hour format (HH:MM): ").strip()

#     file_name="/Email Agent File/document.txt"
#     wait_until_schedule_and_run_every_week(user_time, user_day, file_name)

    

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_date': str(datetime.now())
    }
    try:
        Emailcrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Emailcrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_date": str(datetime.now())
    }
    
    try:
        Emailcrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
