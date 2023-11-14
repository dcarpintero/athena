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
        logging.basicConfig(level=logging.DEBUG,
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
                "tweet" : "Exploring AI's language frontiers with 'BERT: Pre-training of Deep Bidirectional Transformers' by Devlin et al. (2018). \
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

        prompt = f"""
            Create a JSON-formatted response for a professional cold email. The email is from myself, {sender}, a researcher at {institution}, \
            addressed to {receivers}, authors of the research paper '{paper}'. The email should express respect for their work, \
            briefly introduce my research interests, and inquire about their willingness to collaborate on an upcoming project that aligns with our mutual interests.

            EXAMPLE:
            {{
                "subject": "Collaboration on {topic} with {institution}"
                "email": "Dear {receivers},\n\nI hope this message finds you well. My name is {sender}, and I'm a researcher specializing in {topic} at {institution}. \ 
                          After reading your influential paper, '{topic}', I was deeply impressed by your insights and findings. And I am reaching out to explore the \
                          possibility of collaborating on a project that I believe could benefit greatly from your expertise. I would be honored to discuss this further \
                          if you are interested.\n\nLooking forward to the possibility of working together.\n\nBest regards,\n{sender}"
            }}
            --
            """
        
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