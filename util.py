from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
MODEL='gpt-4o-mini'


def get_test_question_prompt(lesson, question_count = 5):
    sample_json = """
            {
              "title": title of the lesson,
              "questions": [list of questions]
            }
            """

    prompt = [{
            "role": "system",
            "content": "You are a school teacher. Your purpose is to build questions to test student's knowledge of the subject matter provided."
        }, {
            "role": "user",
            "content": f"Lesson: {lesson}\n"
                       f""""Your task is to create questions to evaluate a student on the lesson described in the text above by covering important concepts.
                       There should be no more than {question_count} questions and should test a wide range of topics in the lesson."""
                       f"Please return nothing but a JSON in the following format:\n"
                       f"{sample_json}\n "

    }]
    return prompt

def get_ai_response(prompt):
    lc_messages = convert_openai_messages(prompt)
    optional_params = {
        "response_format": {"type": "json_object"}
    }
    return ChatOpenAI(model=MODEL, max_retries=1, temperature=.5,model_kwargs=optional_params).invoke(lc_messages).content

def get_revised_question_prompt(teacher):
    sample_revise_json = """
            {
                "questions": [list of questions],
                "message": message to the critique
            }
            """
    prompt = [{
            "role": "system",
            "content": "You are a school teacher. Your sole purpose is to revise test questions "
                       "based on given critique\n "
        }, {
            "role": "user",
            "content": f"{str(teacher)}\n"
                        f"Your task is to revise test questions based on the critique given.\n "
                        f"Please return json format for the new questions "
                        f"and a message to the critique that explain your changes or why you didn't change anything.\n"
                        f"please return nothing but a JSON in the following format:\n"
                        f"{sample_revise_json}\n "

    }]
    return prompt

def get_critique_prompt(teacher):

    return [{
            "role": "system",
            "content": "You are a teacher critique providing feedback on test questions. Your sole purpose is to provide short feedback on test questions "
                       " so the teacher will know what to fix.\n "
        }, {
            "role": "user",
            "content": f"{str(teacher)}\n"
                       f"Your task is to provide  feedback on the test questions only if necessary.\n"
                       f"Be sure that questions cover wide range of concepts presented in the lesson. Also make sure that questions cover important concepts."
                       f"if you think the question set is good, please return only the word 'None' without the surrounding hash marks.\n"
                       f"do NOT return any text except the word 'None' without surrounding hash marks if no further work is needed onthe article."
                       f"if you noticed the field 'message' in the article, it means the teacher has revised the questions "
                       f"based on your previous critique. The teacher may have explained in message why some of your"
                       f"critique could not be accomodated. For example, something you asked for is not available information."
                       f"you can provide feedback on the revised questions or "
                       f"return only the word 'None' without surrounding hash mark if you think the question set is good."
        }] 