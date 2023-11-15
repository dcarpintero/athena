"""
Coral is a Python library for generating structured responses using Pydantic, Langchain Expression Language, Cohere's LLM.
"""
import logging, os
import cohere, tomli

from dotenv import load_dotenv

from langchain.document_loaders import ArxivLoader
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
    """
    Pydantic Model to generate an structured Tweet with Validation
    """
    text: str = Field(description="Tweet text")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if "https://" not in v:
            logging.error("Tweet does not include a link to the paper!")
            raise ValueError("Tweet must include a link to the paper!")
        return v


class Email(BaseModel):
    """
    Pydantic Model to generate an structured Email
    """
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
        logging.info("generate_tweet (started)")

        model = Cohere(model='command', temperature=0.3, max_tokens=150)
        prompt = PromptTemplate.from_template(self.templates['tweet']['prompt'])
        parser = PydanticOutputParser(pydantic_object=Tweet)

        tweet_chain = prompt | model | parser
        tweet = tweet_chain.invoke({"summary": summary, "link": link})

        logging.debug(tweet)
        logging.info("generate_tweet (OK)")
        return tweet
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def generate_email(self, sender: str, institution: str, receivers: list, title: str, topic: str) -> Email:     
        """
        Generate an structured Email object to the authors of a research paper.
        Under the hood it uses Cohere's LLM, a custom Pydantic Email Model, and Langchain Expression Language with Templates.

        Parameters:
        - sender (str): Name of the sender
        - institution (str): Institution of the sender
        - receivers (list): Names of the receivers
        - title (str): Title of the research paper
        - topic (str): Topic of the research paper
        """
        logging.info("generate_email (started)")

        model = Cohere(model='command', temperature=0.1, max_tokens=500)
        prompt = PromptTemplate.from_template(self.templates['email']['prompt'])
        parser = PydanticOutputParser(pydantic_object=Email)

        email_chain = prompt | model | parser
        email = email_chain.invoke({"sender": sender, 
                                    "institution": institution, 
                                    "receivers": receivers, 
                                    "title": title, 
                                    "topic": topic})
        
        logging.info("generate_email (OK)")
        return email
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def summarize(self, text: str) -> str:
        logging.info("summarize (started)")

        response = self.cohere.summarize(
            text = text,
            length='auto',
            format='bullets',
            model='command',
            additional_command='',
            temperature=0.8,
        )

        logging.info("summarize (OK)")
        return response.summary
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def enrich_summary(self, text: str) -> str:
        logging.info("enrich_summary (started)")

        response = self.cohere.generate(
            model='command',
            prompt=self.templates['keywords']['prompt'].format(text=text),
            max_tokens=4096,
            temperature=0.3,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )

        logging.info("enrich_summary (OK)")
        return response.summary
    

    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def extract_keywords(self, text: str) -> str:
        logging.info("extract_keywords (started)")

        response = self.cohere.generate(
            model='command',
            prompt=self.templates['keywords']['prompt'].format(text=text),
            max_tokens=300,
            temperature=0.3,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )

        logging.info("extract_keywords (OK)")
        return response.generations[0].text
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def load_arxiv_paper(self, paper_id: str) -> (dict, str):
        docs = ArxivLoader(query=paper_id, load_max_docs=2, load_all_available_meta=True).load()
        metadata = docs[0].metadata
        content = docs[0].page_content

        return metadata, content
    

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