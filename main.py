from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import APIKeyCookie
import hashlib
import os
from sqlalchemy import UniqueConstraint
from datetime import datetime

import uuid
from fastapi.responses import RedirectResponse
from typing import List
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


# Initialize FastAPI app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
# Define a default value for the database URL

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


api_key_cookie = APIKeyCookie(name="session_token")


# Define SQLAlchemy base model
Base = declarative_base()

# Define SQLAlchemy models
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String)
    password = Column(String)


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    name = Column(String)
    tagline = Column(String)
    email = Column(String)
    url = Column(String)

    event = relationship("Event", back_populates="presentations")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"))
    user_id = Column(String, ForeignKey("users.id"))
    would_use = Column(Boolean)
    would_invest = Column(Boolean)
    would_work = Column(Boolean)
    comment = Column(String)

    presentation = relationship("Presentation", back_populates="feedback")

    __table_args__ = (
        UniqueConstraint("presentation_id", "user_id", name="uq_presentation_user"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_address = Column(String, nullable=True)
    can_email = Column(Boolean, nullable=False)


# Define relationships
Event.presentations = relationship("Presentation", back_populates="event")
Presentation.feedback = relationship("Feedback", back_populates="presentation")


# Create tables in the database
Base.metadata.create_all(bind=engine)


def get_session(request: Request):
    return request.session

# TODO this should be a wrapper on the ORM object, not the object itself
def get_current_user(session: dict = Depends(get_session)) -> User |None:
    val = session.get("user")
    if val is not None:
        return User(id=val["user_id"], email_address=val["email"])
    return val

class PresentationFeedback(BaseModel):
    presentation_id: int
    event_id: int
    rating: int
    comment: str


class EventModel(BaseModel):
    id: int
    name: str
    date: str

    class Config:
        orm_mode = True


@app.get("/user/")
async def get_user(request: Request):
    orignal_referer = request.headers.get("referer")
    return templates.TemplateResponse(
        "user_template.html",
        {
            "request": request,
            "original_referer": orignal_referer,
        },
    )


@app.post("/create_user/")
async def submit_user(
        request: Request,
        email: str = Form(""),
        can_email: bool = Form(False),
        original_referer: str = Form(''),
        session = Depends(get_session)

):

    db = SessionLocal()

    user = User(email_address=email, can_email=can_email)


    db.add(user)
    db.commit()

    session["user"] = {"user_id": user.id, "email": user.email_address}


    redirect_to = original_referer if not original_referer.endswith("/user/") else "/" 
    return RedirectResponse(redirect_to, status_code=303)

@app.get("/edit_event/")
async def edit_event(
        request: Request,
        event_id: int,
        m: str,
):
    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).one()
    if m != event.password:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Invalid Token"},
            status_code=401,
        )

    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)
    presentations = [row for row in presentations] or None

    return templates.TemplateResponse(
        "update_presentations_template.html",
        {"request": request, "event": event, "presentations": presentations, "m": m},
    )



def return_error_response(request,message:str):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": message},
        status_code=401,  # Unauthorized status code
    )





@app.get("/event_unlock/")
async def event_unlock(
        request: Request,
        event_id: int,
        password: str,
):
    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()
    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)
    presentations = [row for row in presentations] or None

    hashed_password = hash_password(password)
    if hashed_password == event.password:
        return RedirectResponse(
            url=f"/edit_event/?event_id={event_id}&m={hashed_password}"
        )

    else:
        return return_error_response(request, "Incorrect password. Please try again.")

@app.get("/event_unlock/{event_id}")
async def event_unlock_get(
        request: Request,
        event_id: int,
):
    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()
    return templates.TemplateResponse(
        "password.html",
        {"request": request, "event": event},
    )


@app.get("/")
async def landing_page(request: Request):
    db = SessionLocal()
    events = [row for row in db.query(Event)]
    for event in db.query(Event):
        clean_date = event.date[:10]
        event.date = clean_date

    return templates.TemplateResponse(
        "landing_template.html",
        context={
            "request": request,
            "events": events,
        },
    )



# Deprecated
@app.get("/home")
async def home_page(request: Request, user_id: str | None = None):
    db = SessionLocal()
    event = db.query(Event).first()
    email = None
    if user_id is not None:
        email = db.query(User).filter(User.id == user_id).one().email_address

    return templates.TemplateResponse(
        "home_template.html",
        context={
            "request": request,
            "user_id": user_id,
            "event": event,
            "user_email": email,
        },
    )


@app.get("/events/{event_id}")
async def get_event(request: Request, event_id: int,
                    user = Depends(get_current_user)):

    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).one_or_none()
    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)

    presentations = None if len([r for r in presentations]) == 0 else presentations

    return templates.TemplateResponse(
        "event.html",
        {"request": request, "event": event, "presentations": presentations},
    )


@app.get("/about/")
async def make_about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request},
    )





@app.get("/create_event/")
async def make_event(request: Request):
    return templates.TemplateResponse(
        "event_template.html",
        {"request": request},
    )




@app.post("/create_event/")
async def create_event(
        request: Request, event_name: str = Form(""), password: str = Form("")
):

    db = SessionLocal()
    time = datetime.now()
    hashed = hash_password(password)
    event = Event(name=event_name, date=time, password=hashed)

    db.add(event)
    db.commit()
    event_id = event.id

    existing_presentations = db.query(Presentation).filter(
        Presentation.event_id == event_id
    )
    presentations = [row for row in existing_presentations] or None

    db.close()

    return templates.TemplateResponse(
        "update_presentations_template.html",
        {
            "request": request,
            "event": event,
            "presentations": presentations,
            "m": hashed,
        },
    )


@app.post("/create_presentations")
async def create_presentations(
        request: Request,
        event_id: int = Form(...),
        presentation_ids: List[str] = Form([]),
        names: List[str] = Form([]),
        emails: List[str] = Form([]),
        taglines: List[str] = Form([]),
        urls: List[str] = Form([]),
):
    # TODO this needs to be password protected

    parsed_presentation_ids = [safe_parse_int(id) for id in presentation_ids]
    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()

    # Ensure that the lists of data have the same length
    if len(names) != len(emails) != len(taglines) != len(urls):
        return {"error": "Invalid data"}

    # remove presentations that are no longer in the table
    existing_presentations = db.query(Presentation).filter(
        Presentation.event_id == event_id
    )

    to_delete = [
        row for row in existing_presentations if str(row.id) not in parsed_presentation_ids
    ]

    for row in to_delete:
        db.delete(row)

    # Create presentations
    new_presentations = []
    not_new_presentations = []
    for presentation_id, name, email, tagline, url in zip(
            parsed_presentation_ids, names, emails, taglines, urls
    ):
        if presentation_id is not None:
            presentation = db.query(Presentation).filter(
                Presentation.id == presentation_id
            )
            presentation.name = name
            presentation.email = email
            presentation.tagline = tagline
            presentation.url = url

            not_new_presentations.append(presentation)

        else:
            presentation = Presentation(
                name=name, email=email, tagline=tagline, url=url, event_id=event_id
            )
            new_presentations.append(presentation)

    # Add presentations to the database
    db.add_all(new_presentations)

    db.commit()
    # TODO make a general handler for messages that should pop in a banner

    return templates.TemplateResponse(
        "update_presentations_template.html",
        {
            "request": request,
            "event": event,
            "presentations": new_presentations + not_new_presentations,
            "message": "Successfully Saved",
        },
    )


@app.get("/presentations/feedback/{presentation_id}/")
async def get_presentation(request: Request, presentation_id: int, user=Depends(get_current_user)):

    db = SessionLocal()
    presentation = (
        db.query(Presentation).filter(Presentation.id == presentation_id).one_or_none()
    )
    if not presentation:
        return return_error_response(request, "Presentation does not exist.")

    if user is not None:
        user_id = user.id
        existing_feedback = (
            db.query(Feedback)
            .filter(Feedback.presentation_id == presentation_id)
            .filter(Feedback.user_id == user_id)
            .one_or_none()
        )
    else:
        return templates.TemplateResponse(
            "user_template.html",
            {
                "request": request,
                "original_referer": str(request.url),
            },
        )




    return templates.TemplateResponse(
        "feedback_form.html",
        {
            "request": request,
            "presentation" : presentation,
            "existing_feedback": existing_feedback,
        },
    )


@app.post("/presentations/{presentation_id}/feedback")
async def submit_feedback(
        request: Request,
        presentation_id: int,
        would_use: bool = Form(False),
        would_invest: bool = Form(False),
        would_work: bool = Form(False),
        comment: str = Form(""),
        user = Depends(get_current_user),
):

    if user is None:
        return return_error_response(request, "You need to be logged in to give feedback")

    user_id = user.id

    db = SessionLocal()


    event = db.query(Event).join(Presentation,Presentation.event_id ==Event.id).filter(Presentation.id == presentation_id).one()
    event_id =event.id


    existing_feedback = db.query(Feedback).filter(Feedback.user_id == user_id).filter(Feedback.presentation_id == presentation_id).one_or_none()

    if existing_feedback is not None:
        existing_feedback.would_use = would_use
        existing_feedback.would_invest = would_invest
        existing_feedback.would_work = would_work
        existing_feedback.comment = comment
    else:
        feedback = Feedback(
            presentation_id=presentation_id,
            would_use=would_use,
            user_id=user_id,
            would_invest=would_invest,
            would_work=would_work,
            comment=comment,
        )

        db.add(feedback)

    db.commit()
    db.close()

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


def hash_password(password: str):
    return hashlib.sha256(password.strip().encode()).hexdigest()


def safe_parse_int(string)->int|None:
    try:
        val= int(string)
        return val
    except Exception:
        return None
