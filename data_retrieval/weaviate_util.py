import pandas as pd
import weaviate
import logging
import os

from dotenv import load_dotenv

ARXIV_JSON = "arxiv_cs.CL_mini.json"


def index_data(cohere_api_key: str, weaviate_url: str, weaviate_api_key: str):
    """Index Data into Weaviate"""
    logging.info(f"Loading data from '{ARXIV_JSON}'")
    df = pd.read_json(ARXIV_JSON)

    logging.info(f"Initializing Weaviate Client: '{weaviate_url}'")
    client = weaviate.Client(
        url=weaviate_url,
        auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key),
        additional_headers={"X-Cohere-Api-Key": cohere_api_key})

    logging.info(f"Deleting 'ArvixDocument' schema in Weaviate: '{weaviate_url}'")
    client.schema.delete_class("ArvixDocument")

    """
    Weaviate generates vector embeddings at the object level (rather than for individual properties).
    text2vec-* modules  generate vectors from text objects. 
    It vectorizes only properties that use the text data type (unless skipped)

    See: https://weaviate.io/developers/weaviate/config-refs/schema#vectorizer 
    """

    logging.info(f"Creating 'ArvixDocument' schema in Weaviate: '{weaviate_url}'")
    client.schema.delete_class("ArvixDocument")
    class_obj = {
        "class": "ArxivDocument",
        "description": "This class contains Arxiv Documents in the CS.CL category",
        "vectorIndexType": "hnsw",
        "vectorizer": "text2vec-cohere",
        "vectorIndexConfig": {
            "distance": "cosine" # Set to "cosine" for English models; "dot" for multilingual models
        },
        "moduleConfig": {
            "text2vec-cohere": {
                "model": "embed-english-v3.0",
                "truncate": "RIGHT",
                "vectorizeClassName": False
            }
        },
        "properties": [
            {
                "name": "url",
                "dataType": ["text"],
                "indexFilterable": False,
                "indexSearchable": False,
                "vectorizePropertyName": False
            },
                        {
                "name": "url_pdf",
                "dataType": ["text"],
                "indexFilterable": False,
                "indexSearchable": False,
                "vectorizePropertyName": False
            },
            {
                "name": "title",
                "dataType": ["text"]
            },
            {
                "name": "authors",
                "dataType": ["text"]
            },
            {
                "name": "categories",
                "dataType": ["text"]
            },
            {
                "name": "abstract",
                "dataType": ["text"]
            },
            {
                "name": "updated",
                "dataType": ["date"],
            },
            {
                "name": "published",
                "dataType": ["date"],
            },
        ]
    }
    client.schema.create_class(class_obj)

    logging.info(f"Importing data to Weaviate: '{weaviate_url}'")

    try:
        with client.batch as batch:
            batch.batch_size = 100
            for item in df.itertuples():
                properties = {
                    "url": item.id,
                    "url_pdf": item.link_pdf,
                    "title": item.title,
                    "authors": item.authors,
                    "categories": item.categories,
                    "abstract": item.summary,
                    "updated": item.updated,
                    "published": item.published,
                }

                batch.add_data_object(
                    data_object=properties,
                    class_name="ArxivDocument")
    except Exception as ex:
        logging.error(f"Unexpected Error: {ex}")
        raise


def load_environment_vars() -> dict:
    """Load required environment variables. Raise an exception if any are missing."""

    load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

    if not cohere_api_key:
        raise EnvironmentError("COHERE_API_KEY environment variable not set.")

    if not weaviate_url:
        raise EnvironmentError("WEAVIATE_URL environment variable not set.")

    if not weaviate_api_key:
        raise EnvironmentError(
            "WEAVIATE_API_KEY environment variable not set.")

    logging.info("Environment variables loaded.")
    return {"COHERE_API_KEY": cohere_api_key, "WEAVIATE_URL": weaviate_url, "WEAVIATE_API_KEY": weaviate_api_key}


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    try:
        env_vars = load_environment_vars()
        index_data(env_vars["COHERE_API_KEY"],
                   env_vars["WEAVIATE_URL"], env_vars["WEAVIATE_API_KEY"])
    except EnvironmentError as ee:
        logging.error(f"Environment Error: {ee}")
        raise
    except Exception as ex:
        logging.error(f"Unexpected Error: {ex}")
        raise

if __name__ == "__main__":
    main()
