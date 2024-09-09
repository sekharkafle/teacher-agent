# teacher-agent
Working app to demonstrate multi-agent and Human-In-the-Loop collaboration to perform a task.
In this specific case, the task is to create an AI teacher agent to generate a set of questions to test the student on a given lesson. However, the same logic can be extended to build other multi-agent human collaboration tasks.

The app uses langgraph to orchestrate the task. [langgraph](https://github.com/langchain-ai/langgraph)is a library for building stateful, multi-agent applications with LLMs, built on top of LangChain.

## overview

teach_agent.py contains the main logic and all of the langchain related code for the application. 

teach_st.py is the main program of the streamlit version and contains all the streamlit specific logic

InputAgent - Agent to read lesson text from the file.

TeacherAgent - Agent to generate test questions from AI for a given lesson.

CritiqueAgent - Reflection Agent to generate a critique to generated questions for the lesson.

HumanReviewAgent - Agent to receive Human feedback/critique.


Click the [URL] (https://teacher-agent.streamlit.app/)to use the app. You will need an OPENAI api key to use the app.

The code is based on the meeting-reporter repo available here: https://github.com/tevslin/meeting-reporter/
 
