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


def generate_tweet(metadata: dict):
    return cohere_engine.generate_tweet(summary = metadata['Summary'], 
                                        link = metadata['entry_id'])


def generate_email(metadata: dict):
    return cohere_engine.generate_email(sender ="Athena", 
                                        institution = "Latent Univeristy", 
                                        receivers = metadata['Authors'], 
                                        title = metadata['Title'], 
                                        topic = "Machine Learning")

def query_llm(query: str):
    return "A random response"

cohere_engine = load_cohere_engine()
weaviate_store = load_weaviate_store()

# -----------------------------------------------------------------------------
# Sidebar Section
# -----------------------------------------------------------------------------

st.sidebar.title("🦉 Athena Research")

with st.sidebar.expander("📚 ARXIV", expanded=True):
    arxiv_id = st.text_input("Article ID", "1706.03762", help="Article Identifier in the cannonical form: YYMM.NNNNN")

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
    tab_similar, tab_assist, tab_tldr, tab_email, tab_tweet = st.tabs(["🔎 SIMILAR-ARTICLES",
                                                                       "🗨️ ASSIST",
                                                                       "📝 TL;DR",
                                                                       "📬 EMAIL-AUTHORS",
                                                                       "📣 TWEET"])
    
    with tab_similar:
        st.info(f"This demo works with a limited dataset of 50K arXiv articles in AI, ML and NLP")
        topic = f"{metadata['Title']}:{metadata['Summary']}" 
        max_results = 10
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
                        
    with tab_assist:
        query = st.text_input(label="Ask your Paper", placeholder='Ask your question here...',
                              key="user_query_txt", label_visibility="hidden")
        
        if query:
            data = query_llm(query)
            st.success(f"🪄 {data}")

    with tab_tldr:
        col1, col2 = st.columns([1, 1])

        with col1:
            try:
                st.subheader("Abstract enriched with Knowledge-Base")
                st.write(enrich_abstract(metadata).replace("Response:", "", 1))
            except Exception as e:
                st.error(f"enrich_abstract (ERROR): {e}")
        with col2:
            try:
                st.subheader("Glossary of Keywords")
                st.write(extract_keywords(metadata))
            except Exception as e:
                st.error(f"extract_keywords (ERROR): {e}")

    with tab_email:
        try:
            email = generate_email(metadata)

            st.subheader(email.subject)
            st.write(email.body)
        except Exception as e:
            st.error(f"generate_email (ERROR): {e}")

    with tab_tweet:
        st.subheader("Tweet")
        try:
            tweet = generate_tweet(metadata)
            st.write(tweet.text)
        except Exception as e:
            st.error(f"generate_tweet (ERROR): {e}")


if __name__ == "__main__":
    main()