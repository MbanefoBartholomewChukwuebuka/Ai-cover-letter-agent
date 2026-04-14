import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.schema import ResumeSchema, JDSchema, MatchMap, CoverLetterDraft, ConditionState

load_dotenv ()

llm = ChatGroq (model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))
resume_llm = llm.with_structured_output (ResumeSchema)
jd_llm = llm.with_structured_output (JDSchema)
matcher_llm = llm.with_structured_output (MatchMap)
writer_llm = llm.with_structured_output (CoverLetterDraft)
condition_llm = llm.with_structured_output (ConditionState)