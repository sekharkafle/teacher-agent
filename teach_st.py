import os

import streamlit as st
import teach_agent


def process_form(teacher):    
    question_count = 4
    if not "question_count" in teacher: 
        st.session_state['newvalues']={"question_count":question_count, "chapter": 1}
        st.session_state["question_count"] = question_count
        st.rerun()    
        
    elif teacher["title"]:
        
        title = teacher["title"]
        
        st.subheader(title)
        st.write(teacher["lesson"])

        st.subheader("AI Generated Questions")
        for t in teacher["questions"]:
            st.write(t)

        st.subheader("Critique (Human in the Loop)")
        instruction_text = "You can edit or write your own critique to change AI generated questions.\n Once satisfied with the questions, clear the critique to use the questions as displayed. "
        st.write(instruction_text)
        text_input = st.text_area("", value=teacher["critique"], height=150 )

        
        # OK Button
        if st.button('OK'):
            st.session_state["newvalues"]={"critique":text_input,"button":"OK"}
        
def rerun():
    st.session_state['dm'] = None
    st.session_state['result']=None
    st.session_state["newvalues"]=None
            
# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = None
    st.session_state['dm'] = None
    st.session_state['result']=None
    st.session_state["newvalues"]=None
    st.session_state["chapter"]=1

# App title
st.title("Human-In-The-Loop Collaborative AI with Reflection Agent")

with st.sidebar:
    st.markdown("""
### How does it work?
    This application demonstrates
    how a GenAI Agent and a Human 
    (you) can collaborate on a task.
    
    The task is to create a
    question set for a Lesson.
    Provide a short lesson to 
    the AI agent ; the test 
    creator agent creates test
    questions; the critique 
    agent critiques on the 
    generated question set;
    Human (you) can edit AI
    generated critique or 
    you can provide your own
    critique (Human in the
    loop). 
    Keep providing critique 
    until you are satisfied
     with the question set.  
""")

# Sidebar for API key input

if not st.session_state.api_key:
    #with st.sidebar:
    api_key=st.text_input("Enter your ChatGPT API key to get started:", type="password")
    if api_key:
        st.session_state['api_key'] =api_key
        st.rerun()
with st.sidebar:
    st.markdown("[blog post](http://kafles.com)", unsafe_allow_html=True)    

if st.session_state['api_key'] and st.session_state["dm"] is None:
    os.environ['OPENAI_API_KEY'] = st.session_state['api_key']
    st.session_state['dm'] = teach_agent.AgentState()
    st.session_state["result"]=st.session_state['dm'].start()
    


if st.session_state["result"]:
    if "quit" not in st.session_state['result']:
        if st.session_state["newvalues"] is None:
            process_form(st.session_state['result'])
        if st.session_state["newvalues"] and "next" in st.session_state.newvalues:
            process_form(st.session_state.newvalues)
        if st.session_state["newvalues"] and not "next" in st.session_state.newvalues:
            with st.spinner("Please wait... Bots at work"):
                st.session_state["result"]=st.session_state['dm'].resume(st.session_state["newvalues"])
                st.session_state["newvalues"]=None
                st.rerun()
    if "quit" in st.session_state["result"]:
        st.subheader(st.session_state.result["title"])
        st.write(st.session_state.result["lesson"])
        st.subheader("Final Questions (AI Generated & Human Approved)")
        for t in st.session_state.result["questions"]:
            st.write(t)
        st.write("\n")
        if st.button("Next Lesson",key="rerun_n"):
            st.session_state['dm'] = None
            st.session_state['result']=None
            st.session_state["chapter"]= 1 if st.session_state["chapter"] == 6 else st.session_state["chapter"] + 1
            st.session_state['newvalues']={"question_count":st.session_state["question_count"], "chapter": st.session_state["chapter"]}
            st.rerun()


            


    


