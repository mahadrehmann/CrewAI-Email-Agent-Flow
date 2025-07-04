#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from emailcrew.crew import Emailcrew
from send_outlook_email import *

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
                            "address": "i220792@nu.edu.pk"
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }

    inputs = {
        'topic': 'done implementing the crewai email sender', # add signature
        'my_name': 'Mahad Rehman',
        'my_signature': 'Computer Science Department\nFAST NUCES Islamabad',
        'recipient_name': 'Sir Faizan the Great',
        'colleague_name': 'Sherlock Holmes' ,
        'colleague_number' : '+92 123456789',
        'current_date': str(datetime.now()),
        'application' : 'outlook',      #can be anything
        'syntax' : syntax,

        # 'information' : 'cook name and stuff'              #can i stop and ask the user for it?
    }
    
    try:
        final_answer = Emailcrew().crew().kickoff(inputs=inputs)
        # final_answer = "Emailcrew().crew().kickoff(inputs=inputs)"
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
        print("Final JSON is", email_payload)

        send_mail(email_payload)

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


'''
output:


Running the Crew
╭─────────────────────────────────────────────────────────────── Crew Execution Started ────────────────────────────────────────────────────────────────╮
│                                                                                                                                                       │
│  Crew Execution Started                                                                                                                               │
│  Name: crew                                                                                                                                           │
│  ID: 8309e786-eced-4354-860f-51b900e27052                                                                                                             │
│  Tool Args:                                                                                                                                           │
│                                                                                                                                                       │
│                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🚀 Crew: crew
├── 📋 Task: d13c2736-910a-4557-b19a-9257ead9b08b
│   Status: Executing Task...
└── ✅ Knowledge Retrieval Completed
╭─────────────────────────────────────────────────────────────── 📚 Retrieved Knowledge ────────────────────────────────────────────────────────────────╮
│                                                                                                                                                       │
│  Additional Information: Today I studied CrewAi, in which i looked at these:                                                                          │
│                                                                                                                                                       │
│  crewAI is built on top of LangChain with a modular design principle in mind. Its main components consist of agents, tools, tasks, processes and      │
│  crews.                                                                                                                                               │
│                                                                                                                                                       │
│  crewAI facilitates agent collaboration by allowing users to assemble agents into teams, or crews that work to execute a common goal or task.         │
│                                                                                                                                                       │
│  crewAI offers autonomous behavior through its hierarchical process that uses an autonomously generated manager agent                                 │
│                                                                                                                                                       │
│  Agent at...                                                                                                                                          │
│                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────────────────────────────────────────────── 🤖 Agent Started ───────────────────────────────────────────────────────────────────╮
│                                                                                                                                                       │
│  Agent: Write an email for Daily Report about the documentation                                                                                       │
│                                                                                                                                                       │
│  Task: Write an email about Daily Report about the documentation.  Make sure to write it in a well structured manner, the date is 2025-07-02          │
│  20:09:58.520199, My name is Mahad Rehman, recipient's name is Sir Faizan the Great. Use these if applicable: Colleague Name: Sherlock, colleague's   │
│  phone number: 1122 2211.                                                                                                                             │
│                                                                                                                                                       │
│                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🚀 Crew: crew
├── 📋 Task: d13c2736-910a-4557-b19a-9257ead9b08b
│   Status: Executing Task...
└── ✅ Knowledge Retrieval Completed
╭──────────────────────────────────────────────────────────────── ✅ Agent Final Answer ────────────────────────────────────────────────────────────────╮
│                                                                                                                                                       │
│  Agent: Write an email for Daily Report about the documentation                                                                                       │
│                                                                                                                                                       │
│  Final Answer:                                                                                                                                        │
│  Subject: Daily Documentation Report - July 2, 2025                                                                                                   │
│                                                                                                                                                       │
│  Dear Sir Faizan the Great,                                                                                                                           │
│                                                                                                                                                       │
│  This email provides a daily report on my documentation efforts for July 2, 2025.                                                                     │
│                                                                                                                                                       │
│  Today's focus was on researching and documenting the CrewAI framework.  CrewAI is built upon LangChain and employs a modular design centered around  │
│  agents, tools, tasks, processes, and crews.  Key findings are summarized below:                                                                      │
│                                                                                                                                                       │
│  **Core Components:**                                                                                                                                 │
│                                                                                                                                                       │
│  * **Agents:**  Defined by attributes like role, goal, and backstory.  These attributes dictate the agent's behavior and purpose within the system.   │
│  An example instantiation is:                                                                                                                         │
│                                                                                                                                                       │
│  ```python                                                                                                                                            │
│  agent = Agent(                                                                                                                                       │
│       role= 'Customer Support',                                                                                                                       │
│       goal= 'Handles customer inqueries and problems',                                                                                                │
│       backstory= 'You are a customer support specialist for a chain restaurant. You are responsible for handling customer calls and providing         │
│       customer support and inputting feedback data.'                                                                                                  │
│       )                                                                                                                                               │
│  ```                                                                                                                                                  │
│                                                                                                                                                       │
│  * **Tools:** CrewAI offers a toolkit of search tools using the Retrieval-Augmented Generation (RAG) methodology.  Examples include                   │
│  `JSONSearchTool`, `GithubSearchTool`, and `YouTubeChannelSearchTool`.                                                                                │
│                                                                                                                                                       │
│  * **Tasks:** Define specific actions for agents.  An example:                                                                                        │
│                                                                                                                                                       │
│  ```python                                                                                                                                            │
│  data_collection = Task(                                                                                                                              │
│       description= "Gather data from customer interactions, transaction history, and support tickets"                                                 │
│       expected_output= "An organized collection of data that can be preprocessed",                                                                    │
│       agent=data_science_agent,                                                                                                                       │
│                                                                                                                                                       │
│  )                                                                                                                                                    │
│  ```                                                                                                                                                  │
│                                                                                                                                                       │
│  * **Crews:** Allow for collaborative agent work.  Agents are assembled into crews to achieve common goals. An example:                               │
│                                                                                                                                                       │
│  ```python                                                                                                                                            │
│  my_crew = Crew(                                                                                                                                      │
│      agents=[data_science_agent, customer_support_agent],                                                                                             │
│      tasks=[customer_support_task, data_collection_task],                                                                                             │
│      process=Process.sequential,                                                                                                                      │
│      full_output=True,                                                                                                                                │
│      verbose=True,                                                                                                                                    │
│  )                                                                                                                                                    │
│  ```                                                                                                                                                  │
│                                                                                                                                                       │
│  * **Processes:**  Define the workflow (e.g., sequential, parallel) for a crew's tasks.                                                               │
│                                                                                                                                                       │
│                                                                                                                                                       │
│  **Next Steps:**                                                                                                                                      │
│                                                                                                                                                       │
│  Tomorrow, I plan to delve deeper into the implementation details of CrewAI's agent communication and task management mechanisms.  I will also        │
│  explore specific use cases and potential limitations.  If any questions arise, I can be reached at 1122 2211 (Sherlock can also assist).             │
│                                                                                                                                                       │
│                                                                                                                                                       │
│  Sincerely,                                                                                                                                           │
│                                                                                                                                                       │
│  Mahad Rehman                                                                                                                                         │
│  Computer Science Department                                                                                                                          │
│  FAST NUCES Islamabad                                                                                                                                 │
│                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

🚀 Crew: crew
├── 📋 Task: d13c2736-910a-4557-b19a-9257ead9b08b
│   Assigned to: Write an email for Daily Report about the documentation
│
│   Status: ✅ Completed
└── ✅ Knowledge Retrieval Completed
╭─────────────────────────────────────────────────────────────────── Task Completion ───────────────────────────────────────────────────────────────────╮
│                                                                                                                                                       │
│  Task Completed                                                                                                                                       │
│  Name: d13c2736-910a-4557-b19a-9257ead9b08b                                                                                                           │
│  Agent: Write an email for Daily Report about the documentation                                                                                       │
│                                                                                                                                                       │
│  Tool Args:                                                                                                                                           │
│                                                                                                                                                       │
│                                                                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


'''


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
