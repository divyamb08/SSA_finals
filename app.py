import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import requests
import json

import uuid
import pathlib
import logging
import sys
import os
import base64
from io import BytesIO

from configparser import ConfigParser
apiendpoint = "https://sibkozko1d.execute-api.us-east-2.amazonaws.com/prod"

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text
# def get_pdf_text2(uploaded_file):
#     text = ""
#     for pdf in uploaded_file:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     return text

def get_pdf_text2(uploaded_file):
    text = ""
    for pdf in uploaded_file:
        # Convert the bytes object to a file-like object
        pdf_stream = BytesIO(pdf.read())
        pdf_reader = PdfReader(pdf_stream)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Adding fallback for pages without text
    return text

def get_dot_txt_text(downloaded_text):
    text = ""
    for txt in downloaded_text:
        text += txt.read()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# def get_text_chunks2(downloaded_text):
#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     chunks = text_splitter.split_text(downloaded_text)
#     return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

# def upload(filename, byte_data):
#     # print("enter pdf")
#     # pdfname = input()
   
#     # infile = open(pdfname, "rb")
#     # bytes = infile.read()
#     # infile.close()

#     data1 = base64.b64encode(byte_data)
#     datastr = data1.decode()

#     data = {"filename": filename, "data": datastr}
#     print(data['filename'])

#     api = '/upload'
#     url = apiendpoint + api

#     res = requests.post(url, json=data)

#     if res.status_code != 200:
#         # failed:
#         print("Failed with status code:", res.status_code)
#         print("url: " + url)
        
#         if res.status_code == 400:
#             # we'll have an error message
#             try:
#                 body = res.json()
#                 print("Error message:", body)
#             except jsons.JSONDecodeError:
#                 print("Error message is not in JSON format.")
#         return

#     # success, extract jobid:
#     body = res.json()
#     print("done")
#     return

def upload(filename, byte_data):
    data1 = base64.b64encode(byte_data)
    datastr = data1.decode()

    data = {"filename": filename, "data": datastr}
    print(data['filename'])

    api = '/upload'
    url = apiendpoint + api

    res = requests.post(url, json=data)

    # Check the status code
    if res.status_code != 200:
        print("Failed with status code:", res.status_code)
        print("url: " + url)

        # Specific handling for status code 400
        if res.status_code == 400:
            try:
                body = res.json()
                print("Error message:", body)
            except json.JSONDecodeError:
                print("Error message is not in JSON format. Response:", res.text)
        return

    # Try to decode the JSON response
    try:
        body = res.json()
        print("Response body:", body)
        print("done")
    except json.JSONDecodeError:
        print("Failed to decode JSON. Response:", res.text)

    return



# def upload():
#     # pdf_docs = st.file_uploader("Upload your PDF here:")

#     uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
#     if uploaded_file is not None:
#         byte_data = uploaded_file.getvalue()
#         # filename = uploaded_file.name
#         # upload_to_s3(filename, byte_data)
#         # st.success("File uploaded successfully!")


#     if pdf_docs is not None:
#         bytes = pdf_docs.read()

#         infile = open(pdf_docs, "rb")
#         bytes = infile.read()
#         infile.close()


#         data1 = base64.b64encode(bytes)
#         datastr = data1.decode()

#         data = {"filename": pdf_docs.name, "data": datastr}
#         st.write(data['filename'])

#         api = '/upload'
#         url = apiendpoint + api

#         res = requests.post(url, json=data)

#         if res.status_code != 200:
#             # failed:
#             st.write("Failed with status code:", res.status_code)
#             st.write("url: " + url)
            
#             if res.status_code == 400:
#                 # we'll have an error message
#                 try:
#                     body = res.json()
#                     st.write("Error message:", body)
#                 except json.JSONDecodeError:
#                     st.write("Error message is not in JSON format.")
#             return

#         # success, extract jobid:
#         body = res.json()
#         st.write("done")
#         return
def download():
    api = '/download'
    url = apiendpoint + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
    # failed:
        print("Failed with status code:", res.status_code)
        print("url: " + url)
    if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
    #
        return

    #
    # deserialize and extract results:
    #
    body = res.json()

    datastr = body
    # print(datastr)
    # base64_bytes = datastr.encode()
    with open('downloaded_file.txt', 'w') as file:
        for i in datastr:
            bytes = base64.b64decode(i)
            results = bytes.decode()
            print(results)
            file.write(results + '\n')

    print("Data has been written to downloaded_file.txt")
    return

def download2():
    api = '/download'
    url = apiendpoint + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
        # failed:
        print("Failed with status code:", res.status_code)
        print("url: " + url)
    if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
        return

    #
    # deserialize and extract results:
    #
    body = res.json()

    datastr = body
    # print(datastr)
    # base64_bytes = datastr.encode()
    text = ""
    for i in datastr:
        bytes = base64.b64decode(i)
        results = bytes.decode()
        text += results + '\n'

    print("Data has been written to downloaded_file.txt")
    return text

    

def main():
    load_dotenv()
    st.set_page_config(page_title="Interact with S3 - Powered by Spice stack engineers :P",
                       )
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # st.image("https://final-project-spicestack.s3.us-east-2.amazonaws.com/proj_logo.png", width=100)
    st.header("Converse with your S3 data  ")
    st.text("Powered by Spice stack engineers :P")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Local Data management console")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process for one time interaction with your uploaded pdf'", accept_multiple_files=True)
        if st.button("Vectorize local PDF's"):
            with st.spinner("Processing"):
                raw_text = get_pdf_text(pdf_docs)

            # get the text chunks
                text_chunks = get_text_chunks(raw_text)

            # create vector store
                vectorstore = get_vectorstore(text_chunks)

            # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                vectorstore)
        
        # uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"],accept_multiple_files=True)
        
        # if uploaded_file is not None:
        #     byte_data = uploaded_file.read()
        #     filename = uploaded_file.name
        #     upload(filename, byte_data)
        #     st.success("File uploaded successfully!")
        st.subheader("S3 management console")

        uploaded_file = st.file_uploader("Upload a PDF file to AWS S3", type=["pdf"], accept_multiple_files=True)
    
        if uploaded_file:
            for file in uploaded_file:
                byte_data = file.getvalue()  # Use getvalue() to read the content as bytes
                filename = file.name
                upload(filename, byte_data)
                st.success(f"File {filename} uploaded successfully!")
        
        if st.button("Vectorize uploaded S3 File"):
            with st.spinner("Processing"):
                raw_text = get_pdf_text2(uploaded_file)

            # get the text chunks
                text_chunks = get_text_chunks(raw_text)

            # create vector store
                vectorstore = get_vectorstore(text_chunks)

            # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                vectorstore)

        # if st.button("Interact with data on s3 "):
        #     with st.spinner("Processing"):
        #         downloaded_file=download()
        #         # raw_text = get_pdf_text2(uploaded_file)

        #     # get the text chunks
        #         text_chunks = get_text_chunks2(downloaded_file)

        #     # create vector store
        #         vectorstore = get_vectorstore(text_chunks)

        #     # create conversation chain
        #         st.session_state.conversation = get_conversation_chain(
        #         vectorstore)
        st.subheader("To interact with Data that is already on your S3 repo!")

        if st.button("Vectorize all S3 files"):
            with st.spinner("Processing"):
                downloaded_text = download2()  # Assuming this returns the text content

        # Get the text chunks
                # raw_text = get_dot_txt_text(downloaded_text)
                text_chunks = get_text_chunks(downloaded_text)

        # Create vector store
                vectorstore = get_vectorstore(text_chunks)

        # Create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)
        



        # if st.button("Upload to S3"):
        #     upload()
        # st.subheader("S3 Management Section")
        # bucket_name = st.text_input("Enter the bucket name:")
        # file_name = st.text_input("Enter the file name:")
        # st.button("Upload to S3")
        # st.button("Download from S3")
        # bucket_name = st.text_input("Enter the bucket name:")
        # file_name = st.text_input("Enter the file name:")
        # st.button("Delete file from S3")
        



if __name__ == '__main__':
    main()
