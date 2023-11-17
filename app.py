import coral
import streamlit as st
import weaviatestore as ws

st.set_page_config(
    page_title="Athena - Research Companion",
    page_icon="🦉",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Built by @dcarpintero with Cohere and Weaviate"},
)

@st.cache_resource(show_spinner=False)
def load_cohere_engine():
    try:
        return coral.CohereEngine()
    except (OSError, EnvironmentError) as e:
        st.error(f'Cohere Engine Error {e}')
        st.stop()

@st.cache_resource(show_spinner=False)
def load_weaviate_store():
    try:
        return ws.WeaviateStore()
    except (OSError, EnvironmentError) as e:
        st.error(f'Weaviate Store Error {e}')
        st.stop()

@st.cache_data()
def load_arxiv_paper(id: str):
    metadata, content = cohere_engine.load_arxiv_paper(id)
    return metadata, content

def search_documents(topic: str, max_results=10):
    return weaviate_store.query_with_near_text(query=topic, max_results=max_results)

@st.cache_data()
def summarize(metadata: dict):
    return cohere_engine.summarize(text = metadata['Summary'])

@st.cache_data
def enrich_abstract(metadata: dict):
    return cohere_engine.enrich_abstract(text = metadata['Summary'])

@st.cache_data()
def extract_keywords(metadata: dict):
    return cohere_engine.extract_keywords(text = metadata['Summary'])

@st.cache_resource()
def generate_tweet(metadata: dict):
    return cohere_engine.generate_tweet(summary = metadata['Summary'], 
                                        link = metadata['entry_id'])

@st.cache_resource()
def generate_email(metadata: dict):
    return cohere_engine.generate_email(sender ="Athena", 
                                        institution = "Latent Univeristy", 
                                        receivers = metadata['Authors'], 
                                        title = metadata['Title'], 
                                        topic = "Machine Learning")

def query_article(article: str, query: str):
    return cohere_engine.query_llm(article = article, query = query)

cohere_engine = load_cohere_engine()
weaviate_store = load_weaviate_store()

# -----------------------------------------------------------------------------
# Sidebar Section
# -----------------------------------------------------------------------------

st.sidebar.title("🦉 Athena Research")

with st.sidebar.expander("📚 ARXIV", expanded=True):
    arxiv_id = st.text_input("Article ID", "1810.04805", help="Article Identifier in the cannonical form: YYMM.NNNNN")

with st.sidebar.expander("🤖 COHERE-SETTINGS", expanded=True):
    gen_model = st.selectbox("Generation Model", ["command"], key="gen-model", index=0, help="Command is Cohere's default generation model (https://docs.cohere.com/docs/models)")
    embed_model = st.selectbox("Embeddings Model", ["embed-english-v3.0"], key="embed-model", index=0, help="Embed-v3 is the latest and most advanced embeddings model (https://txt.cohere.com/introducing-embed-v3/)")
    rank_model = st.selectbox("Rank Model", ["rerank-multilingual-v2.0"], key="rank-model", index=0, help="Allows for re-ranking English language documents.")
    max_results = st.slider('Max Results', min_value=0, max_value=15, value=10, step=1)
    
with st.sidebar.expander("📁 WEAVIATE-SETTINGS", expanded=True):
    gen_model = st.selectbox("Cluster", ["arxiv.cs.CL.large"], key="cluster", index=0, help="Data collection of 50K arXiv articles in NLP and ML.")
    

with st.expander("ℹ️ ABOUT-THIS-APP", expanded=False):
    st.write("""
             Athena is a RAG-Assist protoype powered by [Cohere](https://cohere.com/), [LangChain](https://www.langchain.com/) and [Weaviate](https://weaviate.io/) to faciliate scientific Research. It provides:
             - *Advanced Semantic Search*: Outperforms traditional keyword searches with [Cohere Embed-v3](https://txt.cohere.com/introducing-embed-v3/) and [Cohere Rerank](https://cohere.com/rerank).
             - *Human-AI Collaboration*: Enables easier review of research literature, highlighting key topics, and augmenting human understanding.
             - *Admin Support*: Provides assistance with tasks such as categorization of research articles, e-mail drafting, and tweets generation.
             """)

with st.sidebar:
    col_gh, col_co, col_we = st.columns([1, 1, 1])
    with col_gh:
        "[![Github](https://img.shields.io/badge/Github%20Repo-gray?logo=Github)](https://github.com/dcarpintero/athena)"
    with col_co:
        "[![Cohere](https://img.shields.io/badge/Cohere%20LLMs-purple)](https://cohere.com/?ref=https://github.com/dcarpintero)"
    with col_we:
        "[![Weaviate](https://img.shields.io/badge/Weaviate-green)](https://weaviate.io/?ref=https://github.com/dcarpintero)"


metadata, content = load_arxiv_paper(arxiv_id)

# -----------------------------------------------------------------------------
def main():
    st.success(f"📚 {metadata['Title']}  |  {metadata['Authors']}  |  📅 {metadata['Published']}  |  {metadata['entry_id']}")

    # Create tabs
    tab_tldr, tab_similar, tab_finder, tab_email, tab_tweet = st.tabs(["📝 TL;DR",
                                                                       "🔎 SIMILAR-ARTICLES",
                                                                       "🗨️ FINDER",
                                                                       "📬 EMAIL-AUTHORS",
                                                                       "📣 TWEET"])

    with tab_tldr:
        st.info(f"ℹ️ Enriches Abstract w/ Wikipedia links combining [Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/) and [LangChain Expression Language](https://python.langchain.com/docs/expression_language/).")
        col1, col2 = st.columns([1, 1])

        with col1:
            try:
                st.subheader("Abstract w/ Wikipedia")
                st.write(enrich_abstract(metadata).replace("Response:", "", 1))
            except Exception as e:
                st.error(f"enrich_abstract (ERROR): {e}")
        with col2:
            try:
                st.subheader("Glossary of Keywords")
                st.write(extract_keywords(metadata))
            except Exception as e:
                st.error(f"extract_keywords (ERROR): {e}")

    with tab_similar:
        st.info(f"ℹ️ These are the most similar Articles from a self-created arXiv dataset of 50k entries in AI, ML and NLP [Powered by Cohere's Embed-v3 and Weaviate]")
        topic = f"{metadata['Title']}:{metadata['Summary']}" 
        data = search_documents(topic=topic, max_results=max_results)

        col1, col2 = st.columns([1, 1])
        with col1:
            for idx, doc in data.iterrows():
                if idx % 2 == 0:
                    arxiv_id = doc["url"].split('/')[-1].split('v')[0]
                    with st.expander(f'**{doc["title"]}**', expanded=True):
                        st.markdown(
                            f'{doc["abstract"][:800]} [...] **[{arxiv_id}]** [PDF]({doc["url_pdf"]})')
                        
        with col2:
            for idx, doc in data.iterrows():
                if idx % 2 != 0:
                    arxiv_id = doc["url"].split('/')[-1].split('v')[0]
                    with st.expander(f'**{doc["title"]}**', expanded=True):
                        st.markdown(
                            f'{doc["abstract"][:800]} [...] **[{arxiv_id}]** [PDF]({doc["url_pdf"]})')
                        
    with tab_finder:
        st.info(f"ℹ️ Find articles in your research topic from a self-created arXiv dataset of 50k entries in AI, ML and NLP [Powered by Cohere's Embed-v3 and Weaviate]")
        query = st.text_input(label="Ask any Paper", placeholder='fine-tuning pre-trained language models',
                              key="user_query_txt", label_visibility="hidden")
        
        if query:
            data = search_documents(topic=query, max_results=max_results)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                for idx, doc in data.iterrows():
                    if idx % 2 == 0:
                        arxiv_id = doc["url"].split('/')[-1].split('v')[0]
                        with st.expander(f'**{doc["title"]}**', expanded=True):
                            st.markdown(
                                f'{doc["abstract"][:800]} [...] **[{arxiv_id}]** [PDF]({doc["url_pdf"]})')
                            
            with col2:
                for idx, doc in data.iterrows():
                    if idx % 2 != 0:
                        arxiv_id = doc["url"].split('/')[-1].split('v')[0]
                        with st.expander(f'**{doc["title"]}**', expanded=True):
                            st.markdown(
                                f'{doc["abstract"][:800]} [...] **[{arxiv_id}]** [PDF]({doc["url_pdf"]})')

    with tab_email:
        st.info(f"ℹ️ This Task uses [LangChain](https://www.langchain.com/) and [Pydantic](https://docs.pydantic.dev/latest/) to format the generated e-mail in JSON format.")
        try:
            email = generate_email(metadata)
        
            st.subheader(email.subject)
            st.write(email.body)
        except Exception as e:
            st.error(f"generate_email (ERROR): {e}")

    with tab_tweet:
        st.info(f"ℹ️ This Task uses [Pydantic](https://docs.pydantic.dev/latest/) to validate that the generated Tweet includes the arXiv link. Invalid responses result in an Error.")
        try:
            tweet = generate_tweet(metadata)
            st.write(tweet.text)
        except Exception as e:
            st.error(f"generate_tweet (ERROR): {e}")


if __name__ == "__main__":
    main()