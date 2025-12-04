from sqlalchemy.orm import Session
from ..models.user_memory import UserMemory

def build_persona(db: Session, user_id: int):
    memory = db.query(UserMemory).filter_by(user_id=user_id).first()
    if not memory:
        return "You are a friendly assistant."

    mem = memory.memory_json

    tone = mem["personality"]["tone"]
    identity = mem["identity"]
    prefs = mem["preferences"]
    emotions = mem["emotions"]["recurring"]

    # Select primary tone
    main_tone = tone[0] if tone else "friendly"

    persona = f"""
You are a {main_tone} assistant.

User identity:
- Age: {identity['age']}
- Cities: {identity['cities']}
- Education: {identity['education']}
- Roles: {identity['roles']}

User preferences: {prefs}
Recurring emotions: {emotions}
"""
    return persona.strip()
