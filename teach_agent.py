from datetime import datetime
import json5 as json

from langgraph.graph import Graph

from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI

from util import get_test_question_prompt, get_critique_prompt, get_revised_question_prompt, get_ai_response

MODEL='gpt-4o-mini'

class TeacherAgent:

    def set_test(self, lesson:str, question_count):
        response = get_ai_response(get_test_question_prompt(lesson, question_count))
        return json.loads(response)

    def revise_test(self, teacher: dict):
        response = get_ai_response(get_revised_question_prompt(teacher))
        return json.loads(response)
        
    def run(self, teacher: dict):
        critique = teacher.get("critique")
        if critique is not None:
            teacher.update(self.revise_test(teacher))
        else:
            teacher.update(self.set_test( teacher["lesson"],question_count=teacher['question_count']))
        return teacher

class CritiqueAgent:

    def critique(self, teacher: dict):
        teacher_copy=teacher.copy()
        del teacher_copy['lesson']
        prompt = get_critique_prompt(teacher_copy)

        lc_messages = convert_openai_messages(prompt)
        response = ChatOpenAI(model="gpt-4",temperature=1.0, max_retries=1).invoke(lc_messages).content
        if response == 'None':
            return {'critique': None}
        else:
            return {'critique': response, 'message': None}

    def run(self, teacher: dict):
        teacher.update(self.critique(teacher))
        return teacher


class InputAgent:
       
    def run(self,teacher:dict):
        from text_reader import read_chapter
        
        if "chapter" in teacher:
            lesson=read_chapter(teacher["chapter"])
            teacher["lesson"]=lesson
        else:
            lesson=read_chapter()
            teacher["lesson"]=lesson
        return teacher
            
class OutputAgent:
    def run(self,teacher:dict):
        print(f"{str(teacher)}")
        return teacher
      
class HumanReviewAgent:
    def run(self,teacher:dict):
        if teacher["button"]=='OK':
            if not teacher["critique"]:
                teacher["critique"]=None
                teacher["quit"]="yes"
        else:
            assert False,"Canceled by reviewer"
        return teacher
    
class StartAgent:
    name='start'
    def run(self,dummy):
        return {"name":self.name}
          
            
        
class AgentState:
    def __init__(self,api_key=None):
        import os
        from langgraph.checkpoint.sqlite import SqliteSaver
        import sqlite3
        
        def from_conn_stringx(cls, conn_string: str,) -> "SqliteSaver":
            return SqliteSaver(conn=sqlite3.connect(conn_string, check_same_thread=False))
        SqliteSaver.from_conn_stringx=classmethod(from_conn_stringx)

        if api_key:
            os.environ['OPENAI_API_KEY']=api_key
        else:
            from dotenv import load_dotenv
            load_dotenv()
        self.memory = SqliteSaver.from_conn_stringx(":memory:")

        start_agent=StartAgent()
        input_agent=InputAgent()
        teacher_agent = TeacherAgent()
        critique_agent = CritiqueAgent()
        output_agent=OutputAgent()
        human_review=HumanReviewAgent()

        workflow = Graph()

        workflow.add_node(start_agent.name,start_agent.run)
        workflow.add_node("input",input_agent.run)
        workflow.add_node("create_test", teacher_agent.run)
        workflow.add_node("critique", critique_agent.run)
        workflow.add_node("output",output_agent.run)
        workflow.add_node("human_review",human_review.run)
 
        #workflow.add_edge(start_agent.name,"input")
        workflow.add_edge("input","create_test")

        workflow.add_edge('create_test', 'critique')
        workflow.add_edge('critique','human_review')
        workflow.add_edge(start_agent.name,"input")
        workflow.add_conditional_edges(start_key='human_review',
                                       condition=lambda x: "accept" if x['critique'] is None else "revise",
                                       conditional_edge_mapping={"accept": "output", "revise": "create_test"})
                                       
        
        # set up start and end nodes
        workflow.set_entry_point(start_agent.name)
        workflow.set_finish_point("output")
        
        self.thread={"configurable": {"thread_id": "2"}}
        self.chain=workflow.compile(checkpointer=self.memory,interrupt_after=[start_agent.name,"critique"])
    def start(self):
        result=self.chain.invoke("",self.thread)
        if result is None:
            values=self.chain.get_state(self.thread).values
            last_state=next(iter(values))
            return values[last_state]
        return result
        
    def resume(self,new_values:dict):
        values=self.chain.get_state(self.thread).values
        last_state=next(iter(values))
        values[last_state].update(new_values)
        self.chain.update_state(self.thread,values[last_state])
        result=self.chain.invoke(None,self.thread,output_keys=last_state)
        if result is None:
            values=self.chain.get_state(self.thread).values
            last_state=next(iter(values))
            return self.chain.get_state(self.thread).values[last_state]
        return result       
      
