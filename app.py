import streamlit as st


def main():
    st.title("Athena - Your Research Companion")

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
        st.write("This is a tweet section")


if __name__ == "__main__":
    main()