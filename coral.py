import json
import logging
import os

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

import cohere

class CohereEngine:
    """
    """

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s [%(levelname)s] %(message)s")
        self.vars = self.__load_environment_vars()
        self.cohere = self.__cohere_client(self.vars["COHERE_API_KEY"])

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
        prompt = f"""
            Write a short Tweet about this research paper '{summary}'. Include hashtags and the link to the paper in the tweet: {link}
            Format your response as a JSON dictionary as in the following example:
    
            EXAMPLE:
            {{
                "tweet" = "Exploring AI's language frontiers with 'BERT: Pre-training of Deep Bidirectional Transformers' by Devlin et al. (2018). \
                           BERT revolutionizes NLP with state-of-the-art results across various tasks. \
                           Read more: [https://arxiv.org/abs/1810.04805] #AI #NLP #MachineLearning 🤖💬",
            }} 
            
            --
        """

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

        return json.loads(response.generations[0].text)
    

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