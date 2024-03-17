from fastapi import FastAPI, HTTPException, Request, Form, Depends
import os
from sqlalchemy import UniqueConstraint
from datetime import datetime
from typing import Optional

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

# Define a default value for the database URL

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
print(f"database url {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define SQLAlchemy base model
Base = declarative_base()


# Define SQLAlchemy models
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String)


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
    dont_care = Column(Boolean)
    would_invest = Column(Boolean)
    would_work = Column(Boolean)
    comment = Column(String)

    presentation = relationship("Presentation", back_populates="feedback")


    __table_args__ = (
        UniqueConstraint('presentation_id', 'user_id', name='uq_presentation_user'),
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
    db = SessionLocal()
    return templates.TemplateResponse(
        "user_template.html",
        {
            "request": request,
        },
    )


@app.post("/user/")
async def submit_user(
        request: Request,
        email: str = Form(""),
        can_email: bool = Form(False),
):

    db = SessionLocal()

    user = User(email_address=email, can_email=can_email)

    db.add(user)
    db.commit()

    user_id = user.id
    db.close()

    return RedirectResponse(url="/home?user_id={}".format(user_id), status_code=303)




@app.get("/")
async def landing_page(request: Request):

    return templates.TemplateResponse(
        "landing_template.html",
        context={"request": request},
    )



@app.get("/home")
async def home_page(request: Request, user_id: str|None = None):
    db = SessionLocal()
    event = db.query(Event).first()
    email = None
    if user_id is not None:
        email = db.query(User).filter(User.id == user_id).one().email_address

    return templates.TemplateResponse(
        "home_template.html",
        context={"request": request, "user_id": user_id, "event": event, "user_email": email},
    )


@app.get("/events/{event_id}")
async def get_event(request: Request, event_id: int):

    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).one_or_none()
    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)

    presentations = None if len([r for r in presentations]) == 0 else presentations

    return templates.TemplateResponse(
        "generate_presentations_template.html",
        {"request": request, "event":event, "presentations":presentations},
    )


@app.get("/create_event/")
async def make_event(request: Request):
    return templates.TemplateResponse(
        "event_template.html",
        {"request": request},
    )

@app.post("/create_event/")
async def create_event(request: Request, event_name:str = Form("")):

    db = SessionLocal()
    time = datetime.now()
    event = Event(name=event_name, date=time)

    db.add(event)
    db.commit()
    event_id = event.id

    existing_presentations = db.query(Presentation).filter(Presentation.event_id == event_id)
    db.close()


    return templates.TemplateResponse(
        "generate_presentations_template.html",
        {"request": request, "event":event, "presentations": existing_presentations},
    )




@app.post("/create_presentations")
async def create_presentations(request: Request, 
                               event_id: int = Form(...), 
                               presentation_ids: list = Form(...),
                               names: list = Form(...), 
                               emails: list = Form(...), 
                               taglines: list = Form(...), 
                               urls: list = Form(...), 
                               ):

    db = SessionLocal()

    # Ensure that the lists of data have the same length
    if len(names) != len(emails) != len(taglines) != len(urls):
        return {"error": "Invalid data"}

    # remove presentations that are no longer in the table
    existing_presentations = db.query(Presentation).filter(Presentation.event_id == event_id)

    to_delete = [row for row in existing_presentations if str(row.id) not in presentation_ids]

    for row in to_delete:
        db.delete(row)




    # Create presentations
    presentations = []
    for presentation_id ,name, email, tagline, url in zip(presentation_ids, names, emails, taglines, urls):
        presentation_id = None if presentation_id == "" else presentation_id
        print(presentation_id)
        if presentation_id is not None:
            presentation = db.query(Presentation).filter(Presentation.id == presentation_id)
            presentation.name = name
            presentation.email = email
            presentation.tagline = tagline
            presentation.url = url

        else:
            presentation = Presentation(name=name, email=email, tagline=tagline, url=url, event_id=event_id)
            presentations.append(presentation)

    # Add presentations to the database
    db.add_all(presentations)
    db.commit()
    db.close()


    return RedirectResponse(url="/events/{}".format(event_id), status_code=303)



# @app.get("/events_overview/{event_id}")
# async def event_overview(request: Request, event_id:int):

#     db = SessionLocal()
#     event = db.query(Event).filter(Event.id == event_id).one()

#     presentations = db.query(Presentation).filter(Presentation.event_id == event_id)


#     # Render the event overview template with the scheduled events
#     return templates.TemplateResponse(
#         "event_overview_template.html",
#         {"request": request, "scheduled_event": event, "presentations":presentations},
#     )




@app.get("/presentations/{presentation_id}/{user_id}")
async def get_presentation(request: Request, presentation_id: int, user_id: str):

    db = SessionLocal()
    presentation = (
        db.query(Presentation).filter(Presentation.id == presentation_id).one_or_none()
    )

    existing_feedback = (
        db.query(Feedback)
        .filter(Feedback.presentation_id == presentation_id)
        .filter(Feedback.user_id == user_id).first()
    )
    if not presentation:
        print("idk bad thing")


    return templates.TemplateResponse(
        "presentation_template.html",
        {
            "request": request,
            "presentation_title": presentation.title,
            "presentation_description": presentation.description,
            "presentation_id": presentation_id,
            "user_id": user_id,
            "existing_feedback": existing_feedback,
        },
    )


@app.post("/presentations/{presentation_id}/feedback")
async def submit_feedback(
        request: Request,
        presentation_id: int,
        would_use: bool = Form(False),
        dont_care: bool = Form(False),
        would_invest: bool = Form(False),
        would_work: bool = Form(False),
        comment: str = Form(""),
        user_id: str = Form(""),
        feedback_id: Optional[int] = Form(None), 
):
    db = SessionLocal()

    
    if feedback_id is not None:
        existing_feedback = db.query(Feedback).get(feedback_id)
        if existing_feedback is None:
            return HTTPException(status_code=404, detail="Feedback not found")

        existing_feedback.would_use = would_use
        existing_feedback.dont_care = dont_care
        existing_feedback.would_invest = would_invest
        existing_feedback.would_work = would_work
        existing_feedback.comment = comment
    else:
        feedback = Feedback(
            presentation_id=presentation_id,
            would_use=would_use,
            dont_care=dont_care,
            user_id=user_id,
            would_invest=would_invest,
            would_work=would_work,
            comment=comment,
        )

        db.add(feedback)



    db.commit()
    db.close()

    return RedirectResponse(url="/home?user_id={}".format(user_id), status_code=303)

