import streamlit as st
import coral

st.set_page_config(
    page_title="Athena - Your Research Companion",
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

@st.cache_data()
def load_arxiv_paper(id: str):
    metadata, content = cohere_engine.load_arxiv_paper(id)
    return metadata, content


@st.cache_data()
def summarize(metadata: dict):
    return cohere_engine.summarize(text = metadata['Summary'])


@st.cache_data()
def extract_keywords(metadata: dict):
    return cohere_engine.extract_keywords(text = metadata['Summary'])


@st.cache_data()
def generate_tweet(metadata: dict):
    return cohere_engine.generate_tweet(summary = metadata['Summary'], 
                                        link = metadata['entry_id'])


def generate_email(metadata: dict):
    return cohere_engine.generate_email(sender ="Athena", 
                                        institution = "Latent Univeristy", 
                                        receivers = metadata['Authors'], 
                                        title = metadata['Title'], 
                                        topic = "Machine Learning")

cohere_engine = load_cohere_engine()

# -----------------------------------------------------------------------------
# Sidebar Section
# -----------------------------------------------------------------------------

with st.sidebar.expander("📚 RESEARCH", expanded=True):
    arxiv_id = st.text_input("Paper", "1706.03762", help="Paper ID")
    arxiv_mode = st.checkbox("Arxiv", value=True, key="arxiv", help="Search in Arxiv")


with st.sidebar.expander("🤖 COHERE-SETTINGS", expanded=True):
    gen_model = st.selectbox("Generation Model", [
                             "command", "command-light", "command-nightly"], key="gen-model", index=0)
    rank_model = st.selectbox("Rank Model", [
                              "rerank-multilingual-v2.0", "rerank-english-v2.0"], key="rank-model", index=0)
    temperature = st.slider('Temperature', min_value=0.0,
                            max_value=1.0, value=0.30, step=0.05)
    max_results = st.slider('Max Results', min_value=0,
                            max_value=15, value=10, step=1)
    

with st.expander("ℹ️ ABOUT-THIS-APP", expanded=False):
    st.write("""
             - Athena is a RAG-Assist protoype powered by *Cohere-AI*, *LangChain* and *Weaviate* to faciliate scientific Research. It provides:
             - **Advanced Semantic Search**: Outperforms traditional keyword searches with *Cohere's Embed-v3*.
             - **Human-AI Collaboration**: Enables faster review of research literature, highlights key findings, and augments human understanding
             - **Admin Support**: Provides assistance with tasks such as categorization of research papers, e-mail drafting, and tweets generation.
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
    st.title("🦉 Athena - Research Companion")

    # Create tabs
    tab_tldr, tab_contributions, tab_chat, tab_email, tab_citations, tab_smiliar, tab_tweet = st.tabs(["📝 TL;DR",
                                                                                                       "🙌 Contributions",
                                                                                                       "🗨️ Chat",
                                                                                                       "📬 Email Authors",
                                                                                                       "📚 Citations",
                                                                                                       "🔎 Similar Papers",
                                                                                                       "📣 Tweet"])
    with tab_tldr:
        st.subheader("TL;DR")
        st.write(summarize(metadata))

        st.subheader("Keywords")
        st.write(extract_keywords(metadata))


    with tab_contributions:
        st.header("Contributions")
        # contributions = cohere_engine.contributions_arxiv(query="1706.03762")
        # st.write(contributions)

    with tab_chat:
        st.header("Chat")
        st.write("This is a chat section")

    with tab_email:
        email = generate_email(metadata)

        st.subheader(email.subject)
        st.write(email.body)


    with tab_citations:
        st.header("Citations")
        st.write("This is a citations section")

    with tab_smiliar:
        st.header("Similar Papers")
        st.write("This is a similar papers section")

    with tab_tweet:
        st.subheader("Tweet")

        tweet = generate_tweet(metadata)
        st.write(tweet.text)


if __name__ == "__main__":
    main()