from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
import os
from dotenv import load_dotenv

# from send_outlook_email import convert_to_txt
from emailcrew.send_outlook_email import *


load_dotenv()

@CrewBase
class Emailcrew():
    """Emailcrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, rel_path=""):
        self.knowledge_source = TextFileKnowledgeSource(
            file_paths=[rel_path],
            chunk_size=150,  # Trying smaller chunks
            chunk_overlap=50
        )        
        
        print("🔍 Initializing with knowledge source:", self.knowledge_source.file_paths)

    @agent
    def email_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['email_writer'],
            verbose=True,
            # knowledge_sources=[self.knowledge_source],

            # embedder={
            #     "provider": "openai",
            #     "config": {"model": "text-embedding-3-small"}
            # },
            
        )

    @task
    def email_task(self) -> Task:
        return Task(
            config=self.tasks_config['email_task'], # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Emailcrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # embedder={  # ⚙️ Required for agent-level knowledge to be embedded
            #     "provider": "openai",
            #     "config": {"model": "text-embedding-3-small"}
            # }
            
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
