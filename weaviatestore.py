import logging, os
import pandas as pd
import weaviate

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

class WeaviateStore:

    def __init__(self) -> None:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s [%(levelname)s] %(message)s")
        self.vars = self.__load_environment_vars()
        self.weaviate = self.__weaviate_client(self.vars["COHERE_API_KEY"],
                                               self.vars["WEAVIATE_URL"], 
                                               self.vars["WEAVIATE_API_KEY"])

        logging.info("Initialized WeaviateEngine")


    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def query_with_near_text(_w_client: weaviate.Client, query, max_results=10) -> pd.DataFrame:
        """
        Search Arxiv Documents in Weaviate with Near Text.
        Weaviate converts the input query into a vector through the inference API (Cohere) and uses that vector as the basis for a vector search.
        """

        response = (
            _w_client.query
            .get("ArxivDocument_CS_CL", ["url", "url_pdf", "title", "authors", "categories", "abstract", "updated", "published"])
            .with_near_text({"concepts": [query]})
            .with_limit(max_results)
            .do()
        )

        data = response["data"]["Get"]["ArxivDocument_CS_CL"]
        return pd.DataFrame.from_dict(data, orient='columns')


    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def query_with_bm25(_w_client: weaviate.Client, query, max_results=10) -> pd.DataFrame:
        """
        Search Arxiv Documents in Weaviate with BM25.
        Keyword (also called a sparse vector search) search that looks for objects that contain the search terms in their properties according to 
        the selected tokenization. The results are scored according to the BM25F function. It is .
        """

        response = (
            _w_client.query
            .get("ArxivDocument_CS_CL", ["url", "url_pdf", "title", "authors", "categories", "abstract", "updated", "published"])
            .with_bm25(query=query)
            .with_limit(max_results)
            .with_additional("score")
            .do()
        )

        data = response["data"]["Get"]["ArxivDocument_CS_CL"]
        return pd.DataFrame.from_dict(data, orient='columns')


    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def query_with_hybrid(_w_client: weaviate.Client, query, max_results=10) -> pd.DataFrame:
        """
        Search Arxiv Documents in Weaviate with BM25.
        Keyword (also called a sparse vector search) search that looks for objects that contain the search terms in their properties according to 
        the selected tokenization. The results are scored according to the BM25F function. It is .
        """

        response = (
            _w_client.query
            .get("ArxivDocument_CS_CL", ["url", "url_pdf", "title", "authors", "categories", "abstract", "updated", "published"])
            .with_hybrid(query=query)
            .with_limit(max_results)
            .with_additional(["score"])
            .do()
        )

        data = response["data"]["Get"]["ArxivDocument_CS_CL"]
        return pd.DataFrame.from_dict(data, orient='columns')


    def __load_environment_vars(self):
        """
        Load environment variables from .env file
        """
        logging.info("load_environment_vars (started)")

        load_dotenv()
        required_vars = ["COHERE_API_KEY", "WEAVIATE_URL", "WEAVIATE_API_KEY"]
        env_vars = {var: os.getenv(var) for var in required_vars}
        for var, value in env_vars.items():
            if not value:
                raise EnvironmentError(f"{var} environment variable not set.")
        
        logging.info("load_environment_vars (OK)")
        return env_vars
    

    @retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
    def __weaviate_client(self, cohere_api_key: str, weaviate_url: str, weaviate_api_key: str):
        """
        Initialize Weaviate client

        Parameters:
        - cohere_api_key (str): Cohere API key
        - weaviate_url (str): Weaviate URL
        - weaviate_api_key (str): Weaviate API key
        """
        logging.info(f"Initializing Weaviate Client: '{weaviate_url}'")
        client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key),
            additional_headers={"X-Cohere-Api-Key": cohere_api_key})

        return client