import json
import logging
import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_random_exponential

import cohere
import tomli

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
    def generate_tweet(self, summary: str, link: str) -> dict:
        """
        Generate a Tweet about a research paper using Cohere's command model.

        Parameters:
        - summary (str): Summary of the research paper
        - link (str): Link to the research paper

        Returns:
        - dict: Tweet and link to the research paper as a JSON dictionary
        """
        tweet = self.templates['tweet']['prompt']
        prompt = PromptTemplate.from_template(tweet).format(summary=summary,
                                                            link=link)

        response = self.cohere.generate(
            model='command',
            prompt=prompt,
            max_tokens=150,
            num_generations=1,
            temperature=0.3,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE',
        )

        logging.debug(response)
        return json.loads(response.generations[0].text)
    

    def generate_email(self, sender, institution, receivers, paper, topic) -> str:     
        """
        Generate a professional cold email to the authors of a research paper using Cohere's command model.

        Parameters:
        - sender (str): Name of the sender
        - institution (str): Institution of the sender
        - receivers (list): Names of the receivers
        - paper (str): Title of the research paper
        - topic (str): Topic of the research paper
        """
        receivers = ', '.join(receivers[:-1]) + ' and ' + receivers[-1]

        email = self.templates['email']['prompt']
        prompt = PromptTemplate.from_template(email).format(sender=sender, 
                                                            institution=institution, 
                                                            receivers=receivers, 
                                                            paper=paper, 
                                                            topic=topic)
                
        response = self.cohere.generate(
            model='command',
            prompt=prompt,
            max_tokens=500,
            temperature=0.1,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )

        logging.debug(response.generations[0].text)
        return response.generations[0].text


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