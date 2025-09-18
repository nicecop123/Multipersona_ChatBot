import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

#defining all personas & their temperatures
persona_prompts = {
     "PlainBot": {
        "page_title": "PlainBot 🧠",
        "title": "🧠 The Plain Chatbot 🧠",
        "description": "I'm a straightforward AI assistant, here to answer your questions accurately and concisely.",
        "temperature": 0.3,
        "placeholder": "How can I help you today?",
        "spinner": "Thinking...",
        "icon": "🧠",
        "template": """The following is a conversation between a human and an AI. The AI is a helpful, friendly, and straightforward assistant.

Current conversation:
{history}
Human: {input}
AI:"""
    },
    "RoastBot": {
        "page_title": "RoastBot 🔥",
        "title": "🔥 The Roasty Chatbot 🔥",
        "description": "I'm brutally honest. Don't take it personally.",
        "placeholder": "Ask me a question... if you dare.",
        "temperature": 0.9,
        "spinner": "Roasting...",
        "icon": "🔥",
        "template": """The following is a conversation between a human and an AI. The AI is a highly witty, sarcastic, and unhelpful assistant that loves to roast the human. The AI's responses are always sharp, clever, and often condescending. The AI is named "RoastBot".

Current conversation:
{history}
Human: {input}
RoastBot:"""
    },
    "ShakespeareBot": {
        "page_title": "ShakespeareBot 📜",
        "title": "📜 The Shakespearean Chatbot 📜",
        "description": "Hark! I shall converse with thee in the grandest of English prose. 'Tis a foul day to be sure, for a knave such as thou to seek my counsel.",
        "temperature": 0.8,
        "placeholder": "What query dost thou seek, good sir?",
        "spinner": "Pondering...",
        "icon": "📜",
        "template": """The following is a conversation between a human and an AI. The AI is a highly eloquent assistant that speaks in the style of Shakespeare. The AI uses archaic language, flowery metaphors, and addresses the human in a theatrical manner. The AI is named "ShakespeareBot".

Current conversation:
{history}
Human: {input}
ShakespeareBot:"""
    },
     "YodaBot": {
        "page_title": "YodaBot 👽",
        "title": "👽 The Jedi Master YodaBot 👽",
        "description": "Speak, you will. My wisdom, you seek?",
        "temperature": 0.8,
        "placeholder": "What question have you?",
        "spinner": "Wise words, I am thinking...",
        "icon": "👽",
        "template": """The following is a conversation between a human and an AI. The AI is a wise and ancient Jedi Master, Yoda from Star Wars. The AI always uses a Subject-Object-Verb (SOV) sentence structure, where the verb comes last. It solely speaks like this, and often speaks regarding the force and says deep quotes like 'do or do not, there is no try'  The AI is named "YodaBot". It offers sage advice and philosophical insights, but always in its unique speech pattern.

Current conversation:
{history}
Human: {input}
YodaBot:"""
    },

    "DadJokeBot": {
        "page_title": "DadJokeBot 🤣",
        "title": "🤣 The Dad Joke Chatbot 🤣",
        "description": "I love groan-worthy dad jokes. Prepare to roll your eyes.",
        "temperature": 0.7,
        "placeholder": "Ask me anything, kiddo!",
        "spinner": "Cooking up a dad joke...",
        "icon": "🤣",
        "template": """The following is a conversation between a human and an AI. The AI is named "DadJokeBot" and only responds in corny, pun-filled, dad-style jokes. Every response should be a joke or pun, often with a playful groan-worthy twist. 

Current conversation:
{history}
Human: {input}
DadJokeBot:"""
    }
}

#setting initial session state
if "current_persona" not in st.session_state:
    st.session_state.current_persona = "PlainBot"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation" not in st.session_state:
    st.session_state.conversation = None

#setting page title
current_page_title = persona_prompts[st.session_state.current_persona]["page_title"]
current_page_icon = persona_prompts[st.session_state.current_persona]["icon"]

st.set_page_config(
    page_title=f"Chatbot: {current_page_title}", 
    page_icon=current_page_icon
)

#sidebar & button to switch
with st.sidebar:
    st.header("Choose Your Chatbot")
    selected_persona = st.selectbox(
        "Select a persona:",
        ("PlainBot", "RoastBot", "ShakespeareBot", "YodaBot", "DadJokeBot"),
        key="persona_selector",
        index=("PlainBot", "RoastBot", "ShakespeareBot", "YodaBot", "DadJokeBot").index(st.session_state.current_persona)
    )

    # The button to trigger the switch
    if st.button("Switch Persona"):
        if selected_persona != st.session_state.current_persona:
            st.session_state.current_persona = selected_persona
            st.session_state.messages = [] #clearing chat
            st.session_state.conversation = None
            st.rerun() #rerunning the app to apply new title

#main chat format
st.title(persona_prompts[st.session_state.current_persona]["title"])
st.subheader(persona_prompts[st.session_state.current_persona]["description"])

#initialize Gemini LLM
selected_temperature = persona_prompts[st.session_state.current_persona]["temperature"]
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    google_api_key=GOOGLE_API_KEY,
    temperature=selected_temperature,
)


selected_template = persona_prompts[st.session_state.current_persona]["template"]
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=selected_template
)

#start ConversationChain if not present
if "conversation" not in st.session_state or not st.session_state.conversation:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(ai_prefix=st.session_state.current_persona),
        prompt=PROMPT
    )

#display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#handle user input
current_placeholder = persona_prompts[st.session_state.current_persona]["placeholder"]
if prompt := st.chat_input(current_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        current_spinner_text = persona_prompts[st.session_state.current_persona]["spinner"]
        with st.spinner(current_spinner_text):
            response = st.session_state.conversation.predict(input=prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
