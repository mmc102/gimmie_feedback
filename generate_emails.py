from main import SessionLocal, Event, Presentation, Feedback, User

def format_feedback_bools(feedback):
    tokens = []
    if feedback.would_use:
      tokens.append("use")
    if feedback.would_invest:
      tokens.append("invest in")
    if feedback.would_work:
      tokens.append("work on")

    match len(tokens):
      case 1:
         return tokens[0]
      case 2:
         return f'{token[0]} and {token[1]}'
      case 3:
         return f'{token[0]}, {token[1]}, and {token[2]}'




def generate_single_email(feedback, user, presentation):
    use_invest_workwith = format_feedback_bools(feedback)  
    if feedback.comment is not None and len(feedback.comment.strip()) > 0:
	    formatted_comment = f"Your feedback was \"{feedback.comment}\"" 
    else: 
       formatted_comment = ""

    template = f'''
	Hello!

	You left feedback and said you would {use_invest_workwith} {presentation.name}. I am connecting you with the presenter here! 	
	{formatted_comment}
	Letting you both take it from here if either of you have a next step :)  

	Thanks for both attending the event and using reallygreatfeedback.com!

	Matt

	linkedin.com/404
	reallygreatfeedback.com/meta <-- feel free to tell me why reallygreatfeedback.com sucks 

    '''
   


def generate_emails(event_id:int)->list:
    db = SessionLocal()

    event = db.query(Event).filter(Event.id == event_id).one()
    assert event is not None
    presentations = db.query(Presentation).filter(Presentation.event_id == event_id)
    presentation_ids = [row.id for row in presentations]

    
    feedback = db.query(Feedback).filter(Feedback.presentation_id.in_(presentation_ids))
    feedback_lookup = defaultdict(list)
    for row in feedback:
        feedback_lookup[row.id].append(row)

    users = db.query(Users)
    user_lookup = {row.id:row for row in users}


    for presentation in presentations:
      all_feedback = feedback_lookup[presentation.id]
      for feedback in all_feedback:
          user = user_lookup[feedback.user_id]
          generate_single_email(feedback, user, presentation)
      
