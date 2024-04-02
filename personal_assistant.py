import streamlit as st
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient
from langchain_community.llms import Ollama

llm = Ollama(model="llama2")

url = "http://localhost:6333"
collection_name = "Rahul Singh"  # Replace with your Qdrant collection name

embeddings = SentenceTransformerEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")

def chat(query):
  client = QdrantClient(url, prefer_grpc=False)
  db = Qdrant(client=client, embeddings=embeddings, collection_name=collection_name)
  retriever = db.as_retriever(search_kwargs={"k": 1})
  prompt_template = """
  Use the following pieces of information to answer the user's question. 
  Answer the question in a comprehensive and informative way, even if the answer 
  can be found directly in the knowledge base.
  Context:{context}
  Question:{question}
  """
  prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
  chain_type_kwargs = {"prompt": prompt}
  qa = RetrievalQA.from_chain_type(llm=llm, chain_type_kwargs=chain_type_kwargs, retriever=retriever, chain_type="stuff", verbose=True)
  response = qa(query)
  return response['result']

def main():
  st.title('Know about your health!')

  # Initialize chat history (stored in session state)
  if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

  query = st.text_input("Ask me anything:")
  if st.button("Ask"):
    # Build context for the prompt
    context = "\n".join([response for _, response in st.session_state['chat_history']])
    response = chat(f"{context}\nQuestion: {query}")
    st.session_state['chat_history'].append((query, response))

    # Display conversation history (limited to last 5 interactions)
    st.session_state['chat_history'] = st.session_state['chat_history'][-5:]
    st.write("**Conversation History:**")
    for i, (q, a) in enumerate(st.session_state['chat_history']):
      st.write(f"{i+1}. You: {q}")
      st.write(f"   Chatbot: {a}")

  # Display current query and response
  if st.session_state['chat_history']:
    last_query, last_response = st.session_state['chat_history'][-1]
    st.write("**Current Conversation:**")
    st.write("You:", last_query)
    st.write("Chatbot:", last_response)

  # Force UI refresh after processing the query (optional)
  # st.experimental_rerun()  # Option 1: Force refresh after processing

if __name__ == "__main__":
  main()
