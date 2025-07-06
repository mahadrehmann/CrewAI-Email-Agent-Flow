#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from emailcrew.crew import Emailcrew
from send_outlook_email import *
from urllib.parse import quote

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
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
                            # "address": "faizan.wasif@bluescarf.ai"
                            "address": "i220792@nu.edu.pk"
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }                            


    onedrive_file_path = quote("/Email Agent File/user_preference.txt")
    # onedrive_file_path = quote("/Email Agent File/Transformers Architecture to a kid.docx")
    
    inputs = {
        'topic': 'Funny email about Sir Theodore the Third passing his Knight Status to Ashfaq who lives down the street',
        'my_name': 'Mahad Rehman',
        'my_signature': 'Computer Science Department\nFAST NUCES Islamabad',
        'recipient_name': 'Monseur Madam',
        'colleague_name': 'Sherlock Holmes' ,
        'colleague_number' : '+92 123456789',
        'current_date': str(datetime.now()),
        'application' : 'outlook',      #can be anything
        'syntax' : syntax,
        # 'information' : 'people name and stuff'              #can i stop and ask the user for it?
    }
    
    try:
        final_answer = Emailcrew().crew().kickoff(inputs=inputs)
        print("\nFinal Answer:\n")
        print(final_answer, type(final_answer))

        import re, ast

        # 1. Get the raw repr
        raw = str(final_answer)

        # 2. Strip any markdown fences like ```json … ```
        #    This regex pulls out the {...} block
        m = re.search(r"\{(?:.|\s)*\}", raw)
        if not m:
            raise ValueError("No dict literal found in CrewOutput")

        dict_str = m.group(0)

        # 3. Safely evaluate the Python literal into a dict
        email_payload = ast.literal_eval(dict_str)
        # print("Final JSON is", email_payload)

        #get the file from one drive
        onedrive_file = download_file_from_onedrive(onedrive_file_path)
        attachment_file= f"D:\\Codes\\BlueScarf\\Python3.11\\emailcrew\\knowledge\\{onedrive_file}"

        # Sendin the mail
        send_mail(email_payload, attachment_file)

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


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
