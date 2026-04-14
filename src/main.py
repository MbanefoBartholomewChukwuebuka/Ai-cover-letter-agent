from fastapi import FastAPI
from src.agent import graph
from src.schema import InputSchema, OutputSchema, UpdateSchema

agent = graph ()

app = FastAPI()

@app.post ("/write", response_model=OutputSchema)
async def write_cover_letter (data:InputSchema):
    query = {
        'resume_text': data.resume,
        'jd_text': data.jd
    }

    config = {'configurable': {'thread_id': '1234'}}
    response = agent.invoke (input=query, config=config)   

    if response['match_map'].strong_match:
        response_text = f"You are a strong match with score {response['match_map'].overall_match_score}\n{response['match_map'].explanation}"
    else:
        response_text = f"You are not a strong match with score {response['match_map'].overall_match_score}\n{response['match_map'].explanation}" 

    return {'msg': response_text}

@app.post ("/update", response_model=OutputSchema)
async def update_graph (data: UpdateSchema):
    config = {'configurable': {'thread_id': '1234'}}
    feedback = data.msg
    agent.update_state (config=config, values={'feedback':feedback}, as_node='Matcher')
    response = agent.invoke (input=None, config=config)

    print (response['condition'])
    if response['condition'].stop:
        coverLetter = "No cover letter was generated"

    else:
        coverLetter = response['draft_letter'].full_letter

    return {'msg': coverLetter}