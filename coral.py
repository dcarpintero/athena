"""
Coral is a Python library for generating structured responses using Pydantic, Langchain Expression Language, Cohere's LLM.
"""
import logging
import os

import cohere
import tomli

from dotenv import load_dotenv
from langchain.llms import Cohere
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_random_exponential
)

class Tweet(BaseModel):
    text: str = Field(description="Tweet text")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if "https://" not in v:
            logging.error("Tweet does not include a link to the paper!")
            raise ValueError("Tweet must include a link to the paper!")
        return v

class Email(BaseModel):
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")

class CohereEngine:
    """
    """

    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s [%(levelname)s] %(message)s")
        self.vars = self.__load_environment_vars()
        self.cohere = self.__cohere_client(self.vars["COHERE_API_KEY"])
        self.templates = self.__load_prompt_templates()

        logging.info("Initialized CohereEngine")


    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(5))
    def generate_tweet(self, summary: str, link: str) -> Tweet:
        """
        Generate an structured Tweet object about a research paper.
        Under the hood it uses Cohere's LLM, a custom Pydantic Tweet Model, and Langchain Expression Language with Templates.

        Parameters:
        - summary (str): Summary of the research paper
        - link (str): Link to the research paper

        Returns:
        - Tweet: Tweet object
        """
        logging.info("Generating tweet...")

        model = Cohere(model='command', temperature=0.3, max_tokens=150)
        prompt = PromptTemplate.from_template(self.templates['tweet']['prompt'])
        parser = PydanticOutputParser(pydantic_object=Tweet)

        tweet_chain = prompt | model | parser
        tweet = tweet_chain.invoke({"summary": summary, "link": link})

        logging.debug(tweet)
        logging.info("Tweet generated")
        return tweet
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def generate_email(self, sender, institution, receivers, paper, topic) -> Email:     
        """
        Generate an structured Email object to the authors of a research paper.
        Under the hood it uses Cohere's LLM, a custom Pydantic Email Model, and Langchain Expression Language with Templates.

        Parameters:
        - sender (str): Name of the sender
        - institution (str): Institution of the sender
        - receivers (list): Names of the receivers
        - paper (str): Title of the research paper
        - topic (str): Topic of the research paper
        """
        logging.info("Generating email...")

        receivers = ', '.join(receivers[:-1]) + ' and ' + receivers[-1]

        model = Cohere(model='command', temperature=0.1, max_tokens=500)
        prompt = PromptTemplate.from_template(self.templates['email']['prompt'])
        parser = PydanticOutputParser(pydantic_object=Email)

        email_chain = prompt | model | parser
        email = email_chain.invoke({"sender": sender, 
                                    "institution": institution, 
                                    "receivers": receivers, 
                                    "paper": paper, 
                                    "topic": topic})
        
        logging.debug(email)
        logging.info("Email generated")

        return email
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def summarize(self) -> str:
        pass


    def __load_environment_vars(self):
        """
        Load environment variables from .env file
        """
        logging.info("Loading environment variables...")

        load_dotenv()
        required_vars = ["COHERE_API_KEY"]
        env_vars = {var: os.getenv(var) for var in required_vars}
        for var, value in env_vars.items():
            if not value:
                raise EnvironmentError(f"{var} environment variable not set.")
        
        logging.info("Environment variables loaded")
        return env_vars
    

    def __load_prompt_templates(self):
        """
        Load prompt templates from prompts/athena.toml
        """
        logging.info("Loading prompt templates...")

        try:
            with open("prompts/athena.toml", "rb") as f:
                prompts = tomli.load(f)
        except FileNotFoundError as e:
            logging.error(e)
            raise OSError("Prompt templates file not found.")
        
        logging.info("Prompt templates loaded")
        return prompts
    
    
    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(5))
    def __cohere_client(self, cohere_api_key):
        """
        Initialize Cohere client

        Parameters:
        - cohere_api_key (str): Cohere API key

        Returns:
        - cohere.Client: Cohere client
        """
        return cohere.Client(cohere_api_key)