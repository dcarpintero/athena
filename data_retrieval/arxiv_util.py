import requests
import json
import xml.etree.ElementTree as ET
import time
import logging
import random
from tenacity import retry, stop_after_attempt, wait_random_exponential


CATEGORY = "cs.CL"
BASE_URL = "https://export.arxiv.org/api/query?"
MAX_RESULTS_PER_BATCH = 200
TOTAL_RESULTS_TO_RETRIEVE = 50000
NS = {'atom': 'http://www.w3.org/2005/Atom'}
JSON_FILE = "arxiv_papers.json"


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

def config_query_params(start, max_results):
    return {
        "search_query": f"cat:{CATEGORY}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": start,
        "max_results": max_results,
    }

@retry(wait=wait_random_exponential(min=5, max=15), stop=stop_after_attempt(3))
def retrieve_batch_metadata(start, max_results):
    """
    Retrieve a batch of papers metadata from arXiv API.
    """
    params = config_query_params(start, max_results)
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    return response.text

def parse_xml(xml_data):
    """
    Parse XML data and return a list of dictionaries containing the metadata.
    """
    root = ET.fromstring(xml_data)
    entries = []
    for entry in root.findall('.//atom:entry', namespaces=NS):
        categories = [category.attrib.get("term") for category in entry.findall(".//atom:category", namespaces=NS)]
        authors = [author.find('.//atom:name', namespaces=NS).text for author in entry.findall('.//atom:author', namespaces=NS)]

        entry_dict = {
            'id': entry.find('.//atom:id', namespaces=NS).text,
            'title' : entry.find('.//atom:title', namespaces=NS).text.replace('\n', '').strip(),
            'authors': ', '.join(authors),
            'categories': ', '.join(categories),
            'summary': entry.find('.//atom:summary', namespaces=NS).text.strip(),
            'link_pdf': entry.find('.//atom:link[@title="pdf"]', namespaces=NS).attrib.get("href"),
            'updated': entry.find('.//atom:updated', namespaces=NS).text,
            'published': entry.find('.//atom:published', namespaces=NS).text,
        }
        entries.append(entry_dict)
    return entries

def save_to_json(data, filename):
    """"
    Save list of papers' metadata to a JSON file.
    """
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def main():
    start_index = 0
    total_retrieved = 0
    all_paper_metadata = []

    while total_retrieved < TOTAL_RESULTS_TO_RETRIEVE:
        try:
            batch_metadata = retrieve_batch_metadata(start_index, MAX_RESULTS_PER_BATCH)
            entries = parse_xml(batch_metadata)
            all_paper_metadata.extend(entries)

            batch_retrieved = len(entries)
            total_retrieved += batch_retrieved
            logging.info(f"Retrieved {batch_retrieved} papers. Total: {total_retrieved}")

            start_index += batch_retrieved
            time.sleep(random.randint(5, 25))
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

    save_to_json(all_paper_metadata, JSON_FILE)
    logging.info(f"Total {total_retrieved} papers in the '{CATEGORY}' category retrieved and saved to '{JSON_FILE}'.")


if __name__ == "__main__":
    main()
