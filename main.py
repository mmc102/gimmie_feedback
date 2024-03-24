from fastapi import FastAPI, Request, Form, Depends
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
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    # this is probably reckless
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    private = Column(Boolean, nullable=False)
    password = Column(String, nullable=True)
    location = Column(String,nullable=False)


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"))
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
def get_current_user(session: dict = Depends(get_session)) -> User | None:
    val = session.get("user")
    if val is not None:
        return User(id=val["user_id"], email_address=val["email"])
    return val


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
        original_referer: str = Form(""),
        session=Depends(get_session),
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
        request: Request, event_id: str, message: str | None = None, session=Depends(get_session)
):

    event_token = session.get("event")
    # would happen if you did not create the event

    if event_token is None:
        return RedirectResponse(url=f"/event_unlock/?event_id={event_id}")

    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()
    if event_token != event.password:
        return RedirectResponse(url=f"/event_unlock/?event_id={event_id}")

    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)
    presentations = [row for row in presentations] or None

    return templates.TemplateResponse(
        "update_presentations_template.html",
        {
            "request": request,
            "event": event,
            "presentations": presentations,
            "message": message,
        },
    )


@app.post("/event_unlock/")
async def event_unlock(
        request: Request,
        event_id: str,
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


@app.get("/event_unlock/")
async def event_unlock_get(
        request: Request,
        event_id: str,
):
    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()
    return templates.TemplateResponse(
        "password.html",
        {"request": request, "event": event},
    )

@app.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse(
        "landing_template.html",
        context={
            "request": request,
        },
    )


@app.get("/events/{event_id}")
async def get_event(
        request: Request, event_id: str, message: str | None = None, user=Depends(get_current_user)
):

    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).one_or_none()
    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)

    presentations = None if len([r for r in presentations]) == 0 else presentations

    return templates.TemplateResponse(
        "event.html",
        {
            "request": request,
            "event": event,
            "presentations": presentations,
            "message": message,
        },
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


@app.get("/browse_events/")
async def browse_events(request: Request):

    events = get_upcomming_events()

    return templates.TemplateResponse(
        "upcoming_events.html",
        {"request": request, "events": events},
    )




@app.post("/create_event/")
async def create_event(
        request: Request,
        event_name: str = Form(""),
        password: str | None = Form(None),
        date: str = Form(...),
        time: str = Form(...),
        location: str = Form(""),
        private: bool | None = Form(None),
        session=Depends(get_session),
):

    private = bool(private)
    db = SessionLocal()
    hashed = hash_password(password)
    event = Event(name=event_name, date=date, password=hashed, location=location, time=time, private=private)

    db.add(event)
    db.commit()
    event_id = event.id

    db.close()

    session["event"] = hashed

    return RedirectResponse(url=f"/edit_event/?event_id={event_id}", status_code=303)


@app.post("/create_presentations")
async def create_presentations(
        request: Request,
        event_id: str = Form(...),
        presentation_ids: List[str] = Form([]),
        names: List[str] = Form([]),
        emails: List[str] = Form([]),
        taglines: List[str] = Form([]),
        urls: List[str] = Form([]),
        session=Depends(get_session),
):

    token = session.get("event")

    parsed_presentation_ids = [safe_parse_int(id) for id in presentation_ids]
    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()

    if token != event.password:
        return RedirectResponse(url=f"/event_unlock/?event_id={event_id}")
    # Ensure that the lists of data have the same length
    if len(names) != len(emails) != len(taglines) != len(urls):
        return {"error": "Invalid data"}

    # remove presentations that are no longer in the table
    existing_presentations = db.query(Presentation).filter(
        Presentation.event_id == event_id
    )

    to_delete = [
        row for row in existing_presentations if row.id not in parsed_presentation_ids
    ]

    for row in to_delete:
        db.delete(row)

    # Create presentations
    new_presentations = []
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

        else:
            presentation = Presentation(
                name=name, email=email, tagline=tagline, url=url, event_id=event_id
            )
            new_presentations.append(presentation)

    # Add presentations to the database
    db.add_all(new_presentations)

    db.commit()

    return RedirectResponse(
        f"/edit_event/?event_id={event.id}&message=successfully updated!",
        status_code=303,
    )


@app.get("/presentations/feedback/{presentation_id}/")
async def get_feedback_form(
        request: Request, presentation_id: int, user=Depends(get_current_user)
):

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
            "presentation": presentation,
            "existing_feedback": existing_feedback,
        },
    )


@app.post("/presentations/{presentation_id}/feedback")
async def submit_feedback_form(
        request: Request,
        presentation_id: int,
        would_use: bool = Form(False),
        would_invest: bool = Form(False),
        would_work: bool = Form(False),
        comment: str = Form(""),
        user=Depends(get_current_user),
):

    if user is None:
        return return_error_response(
            request, "You need to be logged in to give feedback"
        )

    user_id = user.id

    db = SessionLocal()

    event = (
        db.query(Event)
        .join(Presentation, Presentation.event_id == Event.id)
        .filter(Presentation.id == presentation_id)
        .one()
    )
    event_id = event.id

    existing_feedback = (
        db.query(Feedback)
        .filter(Feedback.user_id == user_id)
        .filter(Feedback.presentation_id == presentation_id)
        .one_or_none()
    )

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
    return RedirectResponse(
        url=f"/events/{event_id}?message=Thanks for your feedback!", status_code=303
    )


def hash_password(password: str | None)-> str | None:
    if password is None:
        return None
    return hashlib.sha256(password.strip().encode()).hexdigest()


def safe_parse_int(string) -> int | None:
    try:
        val = int(string)
        return val
    except Exception:
        return None


def return_error_response(request, message: str):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": message},
        status_code=401,  # Unauthorized status code
    )


def get_upcomming_events()->list[Event]:
    '''return all events that are not private today that have a date of today or in the future'''
    db = SessionLocal()
    today = datetime.now().date()
    events = [row for row in db.query(Event).filter(~Event.private)]


    # this is truly pathetic
    without_old = []
    for event in events:
        if event.date.strip() == "":
            continue
        elif event.date is None:
            continue
        elif datetime.strptime(event.date[:10], "%Y-%m-%d").date() >= today:
            without_old.append(event)

    return without_old
