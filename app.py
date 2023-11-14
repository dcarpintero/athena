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

cohere_engine = load_cohere_engine()

def main():
    st.title("🦉 Athena - Your Research Companion")

    # Create tabs
    tab_tldr, tab_contributions, tab_chat, tab_email, tab_citations, tab_smiliar, tab_tweet = st.tabs(["📝 TL;DR",
                                                                                                       "🙌 Contributions",
                                                                                                       "🗨️ Chat",
                                                                                                       "📬 Email Authors",
                                                                                                       "📚 Citations",
                                                                                                       "🔎 Similar Papers",
                                                                                                       "📣 Tweet"])
    with tab_tldr:
        st.header("TL;DR")
        st.write("This is a TL;DR section")

    with tab_contributions:
        st.header("Contributions")
        st.write("This is a contributions section")

    with tab_chat:
        st.header("Chat")
        st.write("This is a chat section")

    with tab_email:
        st.header("Email Authors")
        st.write("This is a email authors section")

    with tab_citations:
        st.header("Citations")
        st.write("This is a citations section")

    with tab_smiliar:
        st.header("Similar Papers")
        st.write("This is a similar papers section")

    with tab_tweet:
        st.header("Tweet")
        summary = """
        The paper's main contribution is its demonstration of the effectiveness of attention mechanisms in NLP tasks. 
        Attention mechanisms allow neural networks to selectively focus on specific parts of the input sequence, 
        enabling the model to capture long-term dependencies and contextual relationships between words in a sentence. 
        This is particularly important for NLP tasks, where the meaning of a sentence is often influenced by the surrounding words and the overall context.
        """
        link = "https://arxiv.org/abs/1706.03762"
        response = cohere_engine.generate_tweet(summary, link)
        st.write(response["tweet"])


if __name__ == "__main__":
    main()