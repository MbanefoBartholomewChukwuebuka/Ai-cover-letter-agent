from typing import List, Optional, TypedDict, Annotated, Literal
from pydantic import BaseModel, Field

#Resume Schema
class Experience(BaseModel):
    role: str = Field(description="Job title or role")
    company: str = Field(description="Company name")
    start_date: Optional[str] = Field(default=None, description="Start date (e.g., 'Jan 2020')")
    end_date: Optional[str] = Field(default=None, description="End date (e.g., 'Present')")
    responsibilities: List[str] = Field(default_factory=list, description="List of duties or bullet points")
    achievements: List[str] = Field(default_factory=list, description="Quantifiable achievements (e.g., 'Increased revenue by 15%')")

class Education(BaseModel):
    degree: str = Field(description="Degree name (e.g., 'Bachelor of Arts')")
    institution: str = Field(description="School or university")
    start_date: Optional[str] = Field(default=None, description="Start date")
    end_date: Optional[str] = Field(default=None, description="End date or graduation year")
    details: List[str] = Field(default_factory=list, description="Relevant coursework, GPA, honors")

class SkillCategory(BaseModel):
    category: Optional[str] = Field(default=None, description="Category name of the skill (e.g., 'Soft Skills', 'Tools')")
    skills: List[str] = Field(description="List of skills under each category)")

class Project(BaseModel):
    name: str = Field(description="Project title")
    description: List[str] = Field(description="Details or achievements in the project")

class Certification(BaseModel):
    name: str = Field(description="Certification name")
    issuer: Optional[str] = Field(default=None, description="Issuing organization")
    date: Optional[str] = Field(default=None, description="Issue or expiration date")

class ResumeSchema(BaseModel):
    summary: Optional[str] = Field(default=None, description="Professional summary or objective")
    work_experience: List[Experience] = Field(default_factory=list, description="List of work experiences")
    education: List[Education] = Field(default_factory=list, description="List of educational qualifications")
    skills: List[SkillCategory] = Field(default_factory=list, description="Categorized or flat list of skills")
    achievements: List[str] = Field(default_factory=list, description="Standalone achievements")
    projects: List[Project] = Field(default_factory=list, description="List of projects")
    certifications: List[Certification] = Field(default_factory=list, description="List of certifications")
    other_sections: dict = Field(default_factory=dict, description="Any other parsed sections (e.g., {'Volunteer Work': ['details']})")
    keywords: List[str] = Field(default_factory=list, description="Extracted high-frequency keywords")


#JD Schema
class Responsibility(BaseModel):
    description: str = Field(description="Duty or task (e.g., 'Lead team meetings')")

class Requirement(BaseModel):
    description: str = Field(description="Required skill, experience, or qualification (e.g., '5+ years in marketing')")
    category: Optional[str] = Field(default=None, description="Category (e.g., 'Skills', 'Education')")

class Preferred(BaseModel):
    description: str = Field(description="Nice-to-have (e.g., 'Experience with Adobe Suite')")

class JDSchema(BaseModel):
    job_title: str = Field(description="Title of the position")
    company: Optional[str] = Field(default=None, description="Company name")
    overview: Optional[str] = Field(default=None, description="Job summary or purpose")
    responsibilities: List[Responsibility] = Field(default_factory=list, description="List of key duties")
    requirements: List[Requirement] = Field(default_factory=list, description="Must-have qualifications")
    preferred: List[Preferred] = Field(default_factory=list, description="Preferred skills or traits")
    company_values: List[str] = Field(default_factory=list, description="Extracted values (e.g., 'Innovation', 'Diversity')")
    keywords: List[str] = Field(default_factory=list, description="Key terms for matching (e.g., 'SEO', 'Leadership')")
    other_details: dict = Field(default_factory=dict, description="Any additional info (e.g., {'Location': 'Remote', 'Salary': 'Competitive'})")


#Matcher Schema
class MatchItem(BaseModel):
    jd_element: str = Field(description="Phrase or requirement from the JD (e.g. 'experience with LLMs', 'deploy models to production')")
    jd_category: Optional[str] = Field(default=None, description="Category e.g. 'Technical Skills', 'Experience', 'Soft Skills'")
    resume_evidence: str = Field(description="Relevant excerpt / achievement / bullet from resume")
    resume_section: str = Field(description="Which resume section this comes from: 'summary', 'work_experience', 'skills', 'projects', etc.")
    strength_score: float = Field(description="Match strength 0.0–1.0", ge=0.0, le=1.0)
    strong_match: bool = Field (description="True if strong match and False if not strong match")
    explanation: str = Field(description="Short reasoning why this is a good match")
    suggested_phrasing: str = Field(description="Suggested 1–2 sentence way to mention this in cover letter")

class MatchMap(BaseModel):
    overall_match_score: float = Field(description="Overall estimated fit 0–100", ge=0, le=100)
    top_matches: List[MatchItem] = Field(description="Top 4–8 strongest matches, sorted by strength descending")
    gaps: List[str] = Field(default_factory=list, description="Important JD requirements with no/weak match in resume")
    keyword_overlap: List[str] = Field(default_factory=list, description="JD keywords that appear in resume")
    keyword_missing: List[str] = Field(default_factory=list, description="Important JD keywords not found in resume")
    strong_match: bool = Field (description="True if the candidate is a strong match and False if not strong match")
    explanation: str = Field(description="Short reasoning why this candidate is a strong match for the job or not")


#Writer Schema
class CoverLetterDraft(BaseModel):
    full_letter: str = Field(description="The complete cover letter text in plain text / markdown format")
    word_count: int = Field(description="Actual word count of the full letter")
    used_keywords: List[str] = Field(default_factory=list, description="Important JD keywords incorporated")
    

class ConditionState (BaseModel):
    stop: bool = Field (description=("Condition to stop agent or continue writing. True=Stop, False=Continue"))

#State Schema
class StateSchema(TypedDict):
    resume_text: str
    jd_text: str
    parsed_resume: ResumeSchema              
    parsed_jd: JDSchema                  
    match_map: MatchMap          
    draft_letter: CoverLetterDraft
    feedback:str
    condition:ConditionState


class InputSchema (BaseModel):
    resume: str
    jd: str

class OutputSchema (BaseModel):
    msg:str

class UpdateSchema (BaseModel):
    msg: str