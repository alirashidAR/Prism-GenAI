import streamlit as st
import os
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient
from langchain_community.llms import Ollama

llm= Ollama(model="llama2")

url = "http://localhost:6333"

def save_uploaded_file(uploaded_file, save_directory=".\data"):
  """
  Saves an uploaded file to the specified directory.
  """
  if not uploaded_file or not uploaded_file.name:
    return None
  
  file_path = os.path.join(save_directory, uploaded_file.name)
  with open(file_path, "wb") as f:
    f.write(uploaded_file.getbuffer())
  return file_path

prompt_template = """
Use the following pieces of information to answer the questions of the patient.If the question can be answered without using the given context then answer it.
Context:{context}
Question:{question}
Only return the answer to the question.
"""

prompt = PromptTemplate(template=prompt_template,input_variables=["context","question"])

def chat(query,embeddings,collection_name):
    client = QdrantClient(url, prefer_grpc=False)
    db =   Qdrant(client=client,embeddings=embeddings, collection_name=collection_name)
    retriever = db.as_retriever(search_kwargs={"k":1})
    chain_type_kwargs = {"prompt":prompt}
    qa= RetrievalQA.from_chain_type(llm=llm,chain_type_kwargs=chain_type_kwargs,retriever=retriever,chain_type="stuff",verbose=True,return_source_documents=True)
    response = qa(query)
    return response['result']

def main():
  
  st.title('Research Assistant')
  st.write("Upload a PDF file to get started.")

  uploaded_file = st.file_uploader("Upload PDF", type="pdf")
  if uploaded_file is not None:
    saved_path = save_uploaded_file(uploaded_file)
    if saved_path:
        st.success(f"File '{uploaded_file.name}' uploaded and saved to '{saved_path}'")
        st.write("Processing the uploaded PDF file...")
        loader = PyPDFLoader(saved_path)
        pages = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=0, separators=["\n\n", "\n", " ", ""])
        docs = text_splitter.split_documents(pages)
        embeddings = SentenceTransformerEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")
        url = "http://localhost:6333"
        client = QdrantClient(url, prefer_grpc=False)
        Qdrant.from_documents(docs, embeddings, url=url, prefer_grpc=False, collection_name="vector_db")
        st.success("PDF file processed.")

    else:
      st.error("Error saving uploaded file.")

    query = st.text_input("Enter your question:")
    if st.button("Chat"):
        response = chat(query, embeddings, "vector_db")
        st.write("Answer:", response)


  
if __name__ == "__main__":
  main()
