from src.schema import StateSchema, JDSchema, MatchMap, ResumeSchema, CoverLetterDraft, ConditionState
from src.prompts import resumePrompt, jdPrompt, matcher_system_prompt, writerPrompt, feedbackPrompt
from src.utils import llm, resume_llm, jd_llm, matcher_llm, writer_llm, condition_llm
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Literal


def parseResumeNode (state: StateSchema) -> StateSchema:
    sys_msg = SystemMessage (content=resumePrompt.format(schema=ResumeSchema.model_json_schema()))
    msg = HumanMessage (content=f"Resume text:\n\n{state['resume_text']}")

    response = resume_llm.invoke ([sys_msg, msg])
    return {'parsed_resume': response}

def parseJdNode (state:StateSchema) -> StateSchema:
    sys_msg = SystemMessage (content=jdPrompt.format(schema=JDSchema.model_json_schema()))
    msg = HumanMessage (content=f"Job Description text:\n\n{state['jd_text']}")

    response = jd_llm.invoke ([sys_msg, msg])
    return {'parsed_jd':response}


def matcher_node(state: StateSchema) -> StateSchema:
    """
    Runs the matcher and adds match_map to state
    """
    sys_msg = SystemMessage (content=matcher_system_prompt.format(schema=MatchMap.model_json_schema()))
    matcher_user_prompt = """Parsed Resume:
{parsed_resume}

Parsed Job Description:
{parsed_jd}

Create the MatchMap now."""

    msg = HumanMessage (content=matcher_user_prompt.format (parsed_resume=state['parsed_resume'], parsed_jd=state['parsed_jd']))
    response = matcher_llm.invoke ([sys_msg, msg])

    return {"match_map": response}

def writer_node (state:StateSchema) -> StateSchema:
    parsed_resume = state['parsed_resume']
    parsed_jd = state ['parsed_jd']
    match_map = state['match_map']
    job_title = state['parsed_jd'].job_title

    sys_msg = SystemMessage(content=writerPrompt.format (schema=CoverLetterDraft.model_json_schema(), job_title=job_title))

    msg = HumanMessage (f"""
Parsed Resume:
{parsed_resume}

Parsed JD:
{parsed_jd}

Match Map:
{match_map}

Write the full cover letter
""")
    
    response = writer_llm.invoke (input=[sys_msg, msg])
    return {'draft_letter':response}


def check_feedback (state:StateSchema) -> StateSchema:
    feedback = state['feedback']
    sys_msg = SystemMessage(content=feedbackPrompt.format(schema=ConditionState.model_json_schema()))
    msg = HumanMessage (content=f"The uer input is: {feedback}")
    response = condition_llm.invoke (input=[sys_msg, msg])
    return {'condition':response}

def condition_loop (state:StateSchema) -> Literal['continue', 'end']:
    condition = state['condition'].stop

    if condition:
        return 'end'
    else:
        return 'continue'
    

def graph () -> CompiledStateGraph:
    builder = StateGraph (state_schema=StateSchema)
    builder.add_node ('Parse Resume', parseResumeNode)
    builder.add_node ('Parse JD', parseJdNode)
    builder.add_node ('Matcher', matcher_node)
    builder.add_node ('Feedback', check_feedback)
    builder.add_node ('Writer', writer_node)


    builder.add_edge (START, 'Parse Resume')
    builder.add_edge ('Parse Resume', 'Parse JD')
    builder.add_edge ('Parse JD', 'Matcher')
    builder.add_edge ('Matcher', 'Feedback')
    builder.add_conditional_edges ('Feedback', condition_loop, {'continue':'Writer', 'end': END})
    builder.add_edge ('Writer', END)

    memory = MemorySaver ()
    agent = builder.compile (interrupt_after=['Matcher'], checkpointer=memory)
    return agent