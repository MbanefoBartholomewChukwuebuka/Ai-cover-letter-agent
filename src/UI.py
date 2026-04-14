import streamlit as st
import time
from pypdf import PdfReader
import requests

def makeRequest (url:str, payload:dict) -> str:
    response = requests.post (url=url, json=payload)
    return response.json()['msg']

st.title ("Cover Letter Writer")
baseURl = "http://127.0.0.1:8000"

if 'started' not in st.session_state:
    st.session_state.started = False

if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.header("Upload Resume (PDF)")
uploaded_file = st.sidebar.file_uploader(
    "Upload your resume",
    type=["pdf"]
)

resume_text = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    resume_text = "\n".join(
        page.extract_text() or "" for page in reader.pages
    )
    st.sidebar.success("Resume uploaded successfully")

for message in st.session_state.messages:
    m = st.chat_message(message['role'])
    m.markdown(message['content'])

if prompt := st.chat_input ("Input"):
    m = st.chat_message('user')
    m.markdown (prompt)

    st.session_state.messages.append ({'role': 'user', 'content': prompt})
    with st.spinner ("Responding..."):
        if st.session_state.started:
            url = f"{baseURl}/update"
            payload = {
                'msg': prompt
            }
            response = makeRequest (url=url, payload=payload)
            st.session_state.started = False
        else:
            url = f"{baseURl}/write"
            payload = {
                'resume':resume_text,
                'jd':prompt
            }
            response = makeRequest (url=url, payload=payload)
            st.session_state.started = True
        
        m = st.chat_message ('assistant')
        m.markdown(response)

        st.session_state.messages.append ({'role': 'assistant', 'content': response})