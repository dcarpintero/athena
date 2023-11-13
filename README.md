[![Open_inStreamlit](https://img.shields.io/badge/Open%20In-Streamlit-red?logo=Streamlit)](https://wikisearch.streamlit.app/)
[![Python](https://img.shields.io/badge/python-%203.8-blue.svg)](https://www.python.org/)
[![CodeFactor](https://www.codefactor.io/repository/github/dcarpintero/athena/badge)](https://www.codefactor.io/repository/github/dcarpintero/athena)
[![License](https://img.shields.io/badge/Apache-2.0-green.svg)](https://github.com/dcarpintero/athena/blob/main/LICENSE)

# 🦉 Athena - Research Copilot
<p align="center">
  <img src="./static/athena.png">
</p>

Athena is a RAG-Assist protoype powered by [Cohere-AI](https://cohere.com/) and [Embed-v3](https://txt.cohere.com/introducing-embed-v3/) to faciliate scientific Research and Discovery. Its key differentiating features include:
- **Advanced Semantic Search**: Outperforms traditional keyword searches with state-of-the-art embeddings, offering a more nuanced and effective data retrieval experience that understands the complex nature of scientific queries.
- **Human-AI Collaboration**: Enables faster review of research literature, highlights key findings, and augments human understanding by integrating (a demo subset of) the [Arxiv](https://arxiv.org/) and [Wikipedia](https://txt.cohere.com/embedding-archives-wikipedia/) corpus.
- **Comprehensive Admin Support**: Provides assistance with tasks such as categorization of research papers, and e-mail drafting.

## 📚 Demo

## 🚀 Quickstart

1. Clone the repository:
```
git@github.com:dcarpintero/athena.git
```

2. Create and Activate a Virtual Environment:

```
Windows:

py -m venv .venv
.venv\scripts\activate

macOS/Linux

python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Launch Web Application

```
streamlit run ./app.py
```

## 📋 How does it work?

## 🔗 References

- [Arxiv](https://arxiv.org/)
- [Embed-v3](https://txt.cohere.com/introducing-embed-v3/)
- [Langchain]()
- [The Embedding Wikipedia Archives](https://txt.cohere.com/embedding-archives-wikipedia/)
- [Weaviate Vector Search](https://weaviate.io/developers/weaviate/search/similarity/)