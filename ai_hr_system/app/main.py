# -----------------------------------------

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db, SessionLocal
from app import models
from contextlib import asynccontextmanager
import os
import uuid
import shutil

from app.cv_intelligence.cv_analyzer import CVAnalyzer
from aiogram import Bot
from app.bot.notifications import BotNotificationManager
from app.cv_intelligence.schemas import CVAnalysisResult
from app.summary_engine.ai_summarizer import AISummarizer
from app.summary_engine.top_candidates import TopCandidatesRanker
from app.summary_engine.schemas import CandidateSummary, TopCandidatesResponse
from app.candidate_level.level_detector import LevelDetector
from app.candidate_level.difficulty_mapper import DifficultyMapper
from app.candidate_level.schemas import LevelDetectionResult, InterviewPlan
from app.question_engine.question_selector import QuestionSelector
from app.question_engine.schemas import QuestionSet
from app.interview_flow.session_manager import SessionManager
from app.interview_flow.schemas import InterviewSession, QuestionProgress, SessionStatus, SessionSummary
from app.answer_analysis.final_analyzer import FinalAnalyzer
from app.answer_analysis.schemas import FullIntegrityReport
from app.scoring.score_engine import ScoreEngine
from app.scoring.recommendation import RecommendationEngine
from app.scoring.confidence_level import ConfidenceAnalyzer
from app.scoring.schemas import FinalRecommendation
from app.config import settings
from typing import List, Optional
import uvicorn
import shutil
import os
import tempfile

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI (Startup and Shutdown).
    """
    global analyzer, summarizer, ranker, level_detector, difficulty_mapper, question_selector, session_manager, integrity_analyzer, score_engine, recommendation_engine, confidence_analyzer, bot, notifier
    
    # Initialize Database
    models.Base.metadata.create_all(bind=engine)
    
    # Bot Initialization
    token = "8302463815:AAEtgldpuQm0QW0jv3xJCSbmNExmuJ4yb1M"
    bot = Bot(token=token)
    notifier = BotNotificationManager(bot)
    
    analyzer = CVAnalyzer()
    summarizer = AISummarizer()
    ranker = TopCandidatesRanker()
    level_detector = LevelDetector()
    difficulty_mapper = DifficultyMapper()
    question_selector = QuestionSelector()
    session_manager = SessionManager()
    integrity_analyzer = FinalAnalyzer()
    score_engine = ScoreEngine()
    recommendation_engine = RecommendationEngine()
    confidence_analyzer = ConfidenceAnalyzer()
    yield
    # Shutdown logic
    if bot:
        await bot.session.close()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI HR System - Complete", version="6.0", lifespan=lifespan)

# CORS Middleware for local network access (Permissive/Disabled restriction)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Must be False for allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount uploads for CV access
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/admin-ui")
async def read_admin():
    return FileResponse(os.path.join(static_dir, "admin.html"))

# Global Instances
analyzer = None
summarizer = None
ranker = None
level_detector = None
difficulty_mapper = None
question_selector = None
session_manager = None
integrity_analyzer = None
score_engine = None
recommendation_engine = None
confidence_analyzer = None
bot = None
notifier = None

# The startup event is now handled by the lifespan context manager above.

@app.post("/analyze", response_model=CVAnalysisResult)
async def analyze_cv(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint to analyze a CV file (PDF or DOCX).
    """
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analyzer not initialized")
        
    # Validate file extension
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.pdf', '.docx']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .pdf or .docx")

    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Save to a permanent file to store in DB
    perm_filename = f"{uuid.uuid4()}{ext}"
    perm_path = os.path.join(uploads_dir, perm_filename)
    
    with open(perm_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        result = analyzer.analyze(perm_path)
        # Add the permanent path to result so frontend can pass it to start-interview
        result_dict = result.dict()
        result_dict["cv_path"] = f"uploads/{perm_filename}"
        return result_dict
    except ValueError as ve:
        # Expected validation error
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # We don't delete it because we want to keep it in uploads
        pass

@app.post("/summarize", response_model=CandidateSummary)
async def summarize_candidate(
    candidate_name: str = Body(...),
    cv_result: CVAnalysisResult = Body(...)
):
    """
    Generate HR-friendly and technical summary for a candidate.
    """
    if not summarizer:
        raise HTTPException(status_code=500, detail="Summarizer not initialized")
    
    try:
        hr_summary = summarizer.generate_hr_summary(cv_result)
        tech_summary = summarizer.generate_technical_summary(cv_result)
        
        # Calculate score
        from app.summary_engine.top_candidates import TopCandidatesRanker
        temp_ranker = TopCandidatesRanker()
        score = temp_ranker._calculate_score(cv_result)
        
        return CandidateSummary(
            candidate_name=candidate_name,
            summary_hr=hr_summary,
            summary_technical=tech_summary,
            skills_detected=cv_result.skills_detected,
            inferred_skills=cv_result.inferred_skills,
            experience_years=cv_result.experience_years,
            confidence=cv_result.confidence,
            total_score=score
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/top-candidates", response_model=TopCandidatesResponse)
async def rank_candidates(
    candidates: List[dict] = Body(...)
):
    """
    Rank multiple candidates and return sorted list.
    
    Expected input format:
    [
        {
            "candidate_name": "Ivan Ivanov",
            "cv_result": { ... CVAnalysisResult ... }
        },
        ...
    ]
    """
    if not ranker:
        raise HTTPException(status_code=500, detail="Ranker not initialized")
    
    try:
        result = ranker.rank_candidates(candidates)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-level", response_model=LevelDetectionResult)
async def detect_candidate_level(
    candidate_name: str = Body(...),
    cv_result: CVAnalysisResult = Body(...)
):
    """
    Detect candidate seniority level (Junior/Middle/Senior).
    """
    if not level_detector:
        raise HTTPException(status_code=500, detail="Level detector not initialized")
    
    try:
        result = level_detector.detect_level(candidate_name, cv_result)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview-plan", response_model=InterviewPlan)
async def generate_interview_plan(
    level_result: LevelDetectionResult = Body(...)
):
    """
    Generate interview plan with difficulty-mapped questions based on candidate level.
    """
    if not difficulty_mapper:
        raise HTTPException(status_code=500, detail="Difficulty mapper not initialized")
    
    try:
        plan = difficulty_mapper.generate_interview_plan(level_result)
        return plan
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-questions", response_model=QuestionSet)
async def generate_interview_questions(
    level_result: LevelDetectionResult = Body(...),
    max_questions: int = Body(5),
    lang: str = Body("en")
):
    """
    Generate interview questions based on candidate level and skills.
    Only generates questions for skills the candidate has.
    """
    if not question_selector:
        raise HTTPException(status_code=500, detail="Question selector not initialized")
    
    try:
        question_set = question_selector.select_questions(
            level_result=level_result,
            max_total_questions=max_questions,
            lang=lang
        )
        return question_set
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-interview", response_model=InterviewSession)
async def start_interview(
    candidate_id: str = Body(...),
    candidate_name: str = Body(...),
    candidate_phone: str = Body(...),
    candidate_email: str = Body(...),
    question_set: QuestionSet = Body(...),
    lang: str = Body("en"),
    cv_path: str = Body("")
):
    """
    Start a new interview session.
    Creates session and starts first question with timer.
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    try:
        session = session_manager.create_session(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            candidate_phone=candidate_phone,
            candidate_email=candidate_email,
            question_set=question_set,
            candidate_lang=lang,
            cv_path=cv_path
        )
        return session
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/current-question/{session_id}", response_model=QuestionProgress)
async def get_current_question(session_id: str):
    """
    Get current question for active session.
    Includes time remaining.
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    try:
        question = session_manager.get_current_question(session_id)
        if not question:
            raise HTTPException(status_code=404, detail="No active question")
        return question
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-answer/{session_id}")
async def submit_answer(
    session_id: str,
    answer_text: str = Body(...)
):
    """
    Submit answer for current question.
    Automatically moves to next question or finishes session.
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    try:
        answer = session_manager.submit_answer(
            session_id=session_id,
            answer_text=answer_text
        )
        return {
            "status": "success",
            "answer": answer,
            "message": "Answer submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session-status/{session_id}", response_model=InterviewSession)
async def get_session_status(session_id: str):
    """
    Get current status of interview session.
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    try:
        session = session_manager.get_session_status(session_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session-summary/{session_id}", response_model=SessionSummary)
async def get_session_summary(session_id: str):
    """
    Get summary of completed interview session.
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    try:
        summary = session_manager.get_session_summary(session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-integrity/{session_id}", response_model=FullIntegrityReport)
async def analyze_integrity(session_id: str):
    """
    Analyze the integrity and honesty of a completed interview session.
    Detects AI usage, plagiarism, and suspicious timing.
    """
    if not session_manager or not integrity_analyzer:
        raise HTTPException(status_code=500, detail="Analyzers not initialized")
    
    try:
        # 1. Get session summary
        summary = session_manager.get_session_summary(session_id)
        
        # 2. Get the session to access question data (difficulty, etc.)
        session = session_manager.get_session_status(session_id)
        
        # 3. Perform analysis
        report = integrity_analyzer.analyze_session(summary, session.questions)
        return report
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-recommendation/{session_id}", response_model=FinalRecommendation)
async def generate_recommendation(session_id: str):
    """
    Generate the absolute final HR recommendation.
    Aggregates technical score, integrity flags, and behavior.
    """
    if not all([session_manager, integrity_analyzer, score_engine, recommendation_engine, confidence_analyzer]):
        raise HTTPException(status_code=500, detail="Engines not initialized")
    
    try:
        # 1. Get session summary and technical data
        summary = session_manager.get_session_summary(session_id)
        session = session_manager.get_session_status(session_id)
        
        # 2. Get integrity report (Step 6)
        integrity_report = integrity_analyzer.analyze_session(summary, session.questions)
        
        # 3. Get CV Skills to calculate Skills Match
        cv_skills = []
        db_fetch = SessionLocal()
        try:
            db_session_fetch = db_fetch.query(models.SessionModel).filter(models.SessionModel.id == session_id).first()
            candidate_ref = db_fetch.query(models.Candidate).filter(models.Candidate.id == db_session_fetch.candidate_id).first()
            if candidate_ref and candidate_ref.cv_path:
                # Re-parse or use cached if we had it, but re-parse is safe
                cv_analysis = analyzer.analyze(candidate_ref.cv_path)
                cv_skills = cv_analysis.skills_detected + cv_analysis.inferred_skills
        except Exception as e:
            print(f"Error fetching CV skills for scoring: {e}")
        finally:
            db_fetch.close()

        # 4. Calculate Confidence early to include in score
        ans_lengths = [len(a.answer_text) for a in summary.answers]
        confidence = confidence_analyzer.calculate(
            summary.total_questions,
            summary.answered_questions,
            ans_lengths,
            integrity_report.suspicious_answers_count
        )

        # 5. Calculate Score Breakdown with real params
        breakdown = score_engine.aggregate(
            summary, 
            integrity_report, 
            session.questions,
            cv_skills,
            confidence.value
        )
        
        # 6. Calculate Final Weighted Score
        difficulty_mix = "medium"
        if all(q.get("difficulty") == "hard" for q in session.questions):
            difficulty_mix = "hard"
        elif all(q.get("difficulty") == "easy" for q in session.questions):
            difficulty_mix = "easy"
            
        final_score = score_engine.calculate_final_weighted_score(breakdown, difficulty_mix)
        
        # 7. Get HR Recommendation & Decision
        decision, reason = recommendation_engine.get_recommendation(
            final_score, breakdown, integrity_report.global_flags
        )
        # 8. HR Comment Generation
        hr_comment = recommendation_engine.generate_comment(
            decision, breakdown, integrity_report.global_flags
        )
        
        recommendation = FinalRecommendation(
            session_id=session_id,
            candidate_name=summary.candidate_name,
            final_score=final_score,
            decision=decision,
            confidence=confidence,
            hr_comment=hr_comment,
            score_breakdown=breakdown,
            flags=integrity_report.global_flags + [reason],
            metadata={
                "difficulty_mix": difficulty_mix,
                "integrity_summary": integrity_report.recommendation
            }
        )
        
        # 7. Database Persistence
        db = SessionLocal()
        try:
            db_session = db.query(models.SessionModel).filter(models.SessionModel.id == session_id).first()
            candidate = db.query(models.Candidate).filter(models.Candidate.id == db_session.candidate_id).first() if db_session else None
            
            if db_session:
                db_session.score = recommendation.final_score
                db_session.decision = recommendation.decision
                db_session.hr_comment = recommendation.hr_comment
                db_session.confidence = recommendation.confidence
                db_session.ai_summary = recommendation.metadata.get("integrity_summary", "")
                db_session.flags = recommendation.flags
                
                # Add CV URL to metadata for bot
                if candidate and candidate.cv_path:
                    cv_filename = os.path.basename(candidate.cv_path)
                    recommendation.metadata["cv_url"] = f"https://yourdomain.com/uploads/{cv_filename}" # Replace with actual domain context if available
                    # Actually, since it's local dev, maybe just the filename for now or a relative path
                    # But the bot needs an absolute URL to open it.
                    # For now, let's just pass the filename and let the bot/keyboard handle it if needed
                    recommendation.metadata["cv_filename"] = cv_filename

                db.commit()
        except Exception as e:
            db.rollback()
            print(f"DB Error while saving recommendation: {e}")
        finally:
            db.close()

        # 8. Notify HR via Telegram (Step 8 Integration)
        if notifier:
            try:
                await notifier.notify_new_candidate(recommendation)
            except Exception as e:
                print(f"Failed to trigger telegram notification: {e}")

        return recommendation
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-session-status/{session_id}")
async def update_session_status(
    session_id: str, 
    internal_status: str, 
    public_status: Optional[str] = None,
    hr_id: str = "ADMIN"
):
    """
    Manual endpoint for HR to change candidate status.
    Triggers notification if public_status is provided.
    """
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session Manager not initialized")
    
    try:
        print(f"[ADMIN_LOG] Updating session {session_id} to {internal_status}/{public_status} by {hr_id}")
        await session_manager.update_status(
            session_id=session_id,
            new_internal=internal_status,
            new_public=public_status,
            actor=hr_id
        )
        return {"status": "success", "session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/sessions")
async def list_sessions():
    """
    Endpoint for admin to see all sessions from the database.
    """
    db = SessionLocal()
    try:
        # Sort by start_time descending (newest first)
        db_sessions = db.query(models.SessionModel).order_by(models.SessionModel.start_time.desc()).all()
        
        results = []
        for session in db_sessions:
            candidate = db.query(models.Candidate).filter(models.Candidate.id == session.candidate_id).first()
            
            # Use snapshot if available, else fallback to current candidate profile
            c_name = session.candidate_name if session.candidate_name else (candidate.name if candidate else "Unknown")
            c_email = session.candidate_email if session.candidate_email else (candidate.email if candidate else "")
            c_phone = session.candidate_phone if session.candidate_phone else (candidate.phone if candidate else "")
            
            results.append({
                "session_id": session.id,
                "candidate_name": c_name,
                "candidate_email": c_email,
                "candidate_phone": c_phone,
                "candidate_lang": getattr(session, 'candidate_lang', None) or (candidate.language if candidate else "en"),
                "status_public": session.status_public,
                "status_internal": session.status_internal,
                "score": session.score,
                "decision": session.decision,
                "cv_path": candidate.cv_path if candidate else "",
                "questions": session.questions,
                "answers": session.answers,
                "hr_comment": session.hr_comment or "",
                "flags": session.flags or [],
                "start_time": session.start_time.isoformat() if session.start_time else ""
            })
        return results
    except Exception as e:
        print(f"DB Error while listing sessions: {e}")
        return []
    finally:
        db.close()

if __name__ == "__main__":
    print(f"SMTP Config Loaded: User={settings.SMTP_USER}, Server={settings.SMTP_SERVER}:{settings.SMTP_PORT}")
    if not settings.SMTP_USER:
        print("WARNING: SMTP_USER is empty! Check your .env file.")
    
    print("Starting AI HR System API...")
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
