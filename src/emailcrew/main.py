#!/usr/bin/env python
import sys
import os
import warnings

import logging
logging.getLogger("crewai").setLevel(logging.DEBUG)

from datetime import datetime
from emailcrew.crew import Emailcrew
# from urllib.parse import quote
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from send_outlook_email import *
import ast

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


    # onedrive_file_path = "/Email Agent File/attachment.docx"
    onedrive_file_path = "/Email Agent File/document.txt"
    # onedrive_file_path = "/Email Agent File/user_preference.txt"
    # onedrive_file_path = "/Email Agent File/Transformers Architecture to a kid.docx"
    # onedrive_file_path = quote("/Email Agent File/attachment.txt")
    # onedrive_file_path = quote("/Email Agent File/user_preference.txt")
    # onedrive_file_path = quote("/Email Agent File/Transformers Architecture to a kid.docx")
    
    inputs = {
        'topic': 'Providing update and explanation of the document',
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
        # 1️⃣ Download the file from OneDrive
        onedrive_file = download_file_from_onedrive(onedrive_file_path)
        if not onedrive_file:
            raise RuntimeError("Download failed")

        # 2️⃣ Store just the filename in inputs for the agent to see
        inputs["attachment_name"] = onedrive_file

        # 3️⃣ Convert docx/pdf to txt
        attachment_file = os.path.join(os.getcwd(), "knowledge", onedrive_file)
        txt_file = convert_to_txt(attachment_file)
        # txt_path = os.path.abspath(txt_file)
        # txt_path = os.path.relpath(txt_file, os.path.join(os.getcwd(), "knowledge"))

        # 4️⃣ Create the knowledge source
        relative_path = os.path.relpath(txt_file, os.path.join(os.getcwd(), "knowledge"))
        # knowledge_source = TextFileKnowledgeSource(file_paths=[relative_path])
        
        # knowledge_source = TextFileKnowledgeSource(
        #     file_paths=[relative_path],
        #     chunk_size=150,  # Trying smaller chunks
        #     chunk_overlap=50
        # )        

        print("📄 Text file generated:", txt_file)
        print("📄 Relative path used for CrewAI:", relative_path)
        print("📂 Current working directory:", os.getcwd())

        # knowledge_source = TextFileKnowledgeSource(file_paths=[txt_path])

        # 5️⃣ Create the crew
        crew_obj = Emailcrew(relative_path)
        crew = crew_obj.crew()

        # crew.agents[0].knowledge = knowledge_source
        # print("🧠 Agent knowledge sources:", crew.agents[0].knowledge)
        ks = crew_obj.knowledge_source
        print("🧠 Agent knowledge sources:", ks)
        print("🧩 Final chunk count:", len(ks.chunks))


        # 7️⃣ Run the crew
        result = crew.kickoff(inputs=inputs)

        # 4️⃣ Extract the JSON payload from CrewOutput
        raw = str(result)
        m = re.search(r"\{(?:.|\s)*\}", raw)
        if not m:
            raise ValueError("No dict literal found in CrewOutput")
        email_payload = ast.literal_eval(m.group(0))

        # 5️⃣ Send the email, attaching the original downloaded file
        attachment_file = os.path.join(os.getcwd(), "knowledge", onedrive_file)
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
