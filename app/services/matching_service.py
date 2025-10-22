import json
import asyncio
from sqlalchemy.orm import Session
from app.crud import crud_job, crud_user_profile, crud_job_match
from app.schemas.job_match import JobMatchCreate
from app.services.llm_client import get_llm_client
import logging

class MatchingService:
    def __init__(self, db: Session):
        self.db = db

    def run_matching_for_profile(self, profile_id: int):
        logging.info(f"Starting matching process for profile_id: {profile_id}")
        
        profile = crud_user_profile.get(self.db, id=profile_id)
        if not profile:
            logging.error(f"Profile with id {profile_id} not found.")
            return

        jobs_data = crud_job.get_multi(self.db)
        all_jobs = jobs_data.get("items", []) if jobs_data else []
        if not all_jobs:
            logging.warning("No jobs found in the database to match against.")
            return

        logging.info(f"Found {len(all_jobs)} jobs to match against profile {profile_id}.")

        llm_client = get_llm_client()
        
        for job in all_jobs:
            logging.info(f"Matching profile {profile_id} with job {job.id} ('{job.title}')")
            try:
                prompt = self._build_prompt(profile.structured_profile, job)
                
                response_text = asyncio.run(llm_client.generate(prompt))
                
                score, summary, suggestions = self._parse_response(response_text)
                
                self._save_match_result(profile_id, job.id, score, summary, suggestions)

            except Exception as e:
                logging.error(f"Failed to match job {job.id} for profile {profile_id}: {e}")

        logging.info(f"Finished matching process for profile_id: {profile_id}")

    def _build_prompt(self, profile_data: dict, job) -> str:
        # 使用更详细的岗位职责和要求字段
        job_responsibilities = job.job_responsibilities or "未提供"
        job_requirements = job.job_requirements or job.description or "未提供"

        prompt = f"""
        You are an expert technical recruiter and career coach. Your task is to perform a detailed, critical analysis of a candidate's profile against a job description. Your analysis must be realistic and strict.

        **Step 1: Analyze the Job Description**
        First, carefully read the **Key Requirements** and **Key Responsibilities**. Identify the top 3-5 most critical, non-negotiable requirements. These are the "deal-breakers".

        **Step 2: Analyze the Candidate's Profile**
        Review the candidate's skills, work experience, and education from their profile data.

        **Step 3: Perform a Gap Analysis**
        Directly compare the candidate's profile against the critical requirements you identified in Step 1. For each critical requirement, determine if the candidate meets it, partially meets it, or does not meet it. Also, note any strengths the candidate has that go beyond the requirements.

        **Step 4: Provide Score, Summary, and Suggestions**
        Based on your gap analysis, provide a JSON object with three keys: "score", "summary", and "improvement_suggestions".

        **Scoring Rubric (use this strictly):**
        - **9-10 (Excellent):** Candidate meets all critical requirements and has additional valuable experience. A perfect or near-perfect fit.
        - **7-8 (Good):** Candidate meets most (but not all) critical requirements and seems capable of learning the rest quickly. A strong, hireable candidate.
        - **5-6 (Fair):** Candidate meets some critical requirements but has significant, noticeable gaps. Might be considered if the candidate pool is weak.
        - **3-4 (Poor):** Candidate is missing most of the critical requirements. The match is a major stretch.
        - **1-2 (Very Poor):** Candidate does not meet any of the critical requirements. Fundamentally unqualified.

        **Output Instructions:**
        - All text output must be in Chinese.
        - **summary**: Justify the score by explicitly mentioning which **key requirements are met** and which are **not met**. Be honest and direct.
        - **improvement_suggestions**: Provide 2-3 concrete, actionable suggestions for the candidate to improve their profile for this specific role. Suggestions could include learning a specific technology, getting a certification, or gaining experience in a particular type of project.

        ---
        **Provided Information**

        **1. Job Details:**
        - **Title:** {job.title}
        - **Key Responsibilities:** {job_responsibilities}
        - **Key Requirements:** {job_requirements}

        **2. Candidate Profile (JSON):**
        ```json
        {json.dumps(profile_data, indent=2, ensure_ascii=False)}
        ```
        ---

        **Your JSON Output (ONLY the JSON object, no other text):**
        ```json
        {{
          "score": <score_based_on_rubric>,
          "summary": "<your_detailed_chinese_summary>",
          "improvement_suggestions": "<your_actionable_suggestions>"
        }}
        ```
        """
        return prompt

    def _parse_response(self, response: str) -> (float, str, str):
        """Parses the JSON response from the LLM."""
        try:
            # The actual response might be wrapped in markdown ```json ... ```
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            
            data = json.loads(response)
            score = float(data['score'])
            summary = data['summary']
            suggestions = data.get('improvement_suggestions', '')

            # 如果 LLM 返回的是列表，将其转换为带换行的字符串
            if isinstance(suggestions, list):
                suggestions = "\n".join(f"- {s}" for s in suggestions)

            return score, summary, suggestions
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.error(f"Failed to parse LLM response: {response}. Error: {e}")
            # Return a default/error state
            return 0.0, "Error parsing LLM response.", ""

    def _save_match_result(self, profile_id: int, job_id: int, score: float, summary: str, suggestions: str):
        """Saves the matching result to the database."""
        match_create_obj = JobMatchCreate(
            user_profile_id=profile_id,
            job_id=job_id,
            match_score=score,
            match_summary=summary,
            improvement_suggestions=suggestions
        )
        crud_job_match.create(self.db, obj_in=match_create_obj)
        logging.info(f"Successfully saved match for profile {profile_id} and job {job_id}")

matching_service = MatchingService
