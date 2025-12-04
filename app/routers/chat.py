from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
from typing import cast, List, Dict, Any
import requests
import threading

from ..database import get_db
from ..models.chat_session import ChatSession
from ..config import COLAB_URL, INFERENCE_API_KEY

from ..services.personality import build_persona
from ..services.memory import extract_memories_from_llm

router = APIRouter(prefix="/chat", tags=["chat"])


# ----------------------------------------------------
# Save message safely
# ----------------------------------------------------
def append_message(db: Session, session: ChatSession, role: str, text: str):

    msgs = session.messages or []
    msgs = cast(List[Dict[str, Any]], msgs)

    msgs.append({
        "role": role,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    })

    session.messages = msgs
    flag_modified(session, "messages")

    db.commit()
    db.refresh(session)
    return session



# ----------------------------------------------------
# POST /chat/ → Main Chat
# ----------------------------------------------------
@router.post("/")
def chat(payload: dict = Body(...), db: Session = Depends(get_db)):

    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    user_message = payload.get("message")

    if not user_id:
        raise HTTPException(400, "user_id is required")
    if not session_id:
        raise HTTPException(400, "session_id is required")
    if not user_message or not user_message.strip():
        raise HTTPException(400, "message cannot be empty")

    session = db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
    if not session:
        raise HTTPException(404, "Chat session not found")

    append_message(db, session, "user", user_message)

    persona_text = build_persona(db, user_id)
    persona_mode = payload.get("persona_mode")

    request_body = {
        "message": user_message,
        "persona": persona_text
    }

    if persona_mode:
        request_body["persona_mode"] = persona_mode


    # ----------------------------------------------------
    # STREAMING RESPONSE
    # ----------------------------------------------------
    def stream():
        ai_full = ""
        skip_mode = False
        buffer = ""

        try:
            with requests.post(
                f"{COLAB_URL}/chat/",
                headers={"Authorization": f"Bearer {INFERENCE_API_KEY}"},
                json=request_body,
                stream=True,
                timeout=600
            ) as r:

                if r.status_code != 200:
                    yield f"ERROR {r.status_code}: {r.text}"
                    return

                for chunk in r.iter_content(chunk_size=None):
                    if not chunk:
                        continue

                    token = chunk.decode("utf-8")
                    buffer += token

                    # Skip <think>
                    if "<think>" in buffer:
                        skip_mode = True
                        buffer = ""
                        yield "__THINKING_START__"
                        continue
                    if "</think>" in buffer:
                        skip_mode = False
                        buffer = ""
                        yield "__THINKING_END__"
                        continue
                    if skip_mode:
                        buffer = ""
                        continue

                    ai_full += token
                    yield token

        except Exception as e:
            yield f"Error: {str(e)}"
            return

        append_message(db, session, "assistant", ai_full)


        # ----------------------------------------------------
        # BACKGROUND MEMORY UPDATE
        # ----------------------------------------------------
        def run_memory_update():
            sessions = db.query(ChatSession).filter_by(user_id=user_id).all()
            all_msgs = []

            for s in sessions:
                if not s.messages:
                    continue
                for msg in s.messages:
                    if msg.get("role") == "user":
                        t = msg.get("text", "").strip()
                        if t:
                            all_msgs.append(t)

            last_30 = all_msgs[-30:]

            extract_memories_from_llm(db, user_id, last_30)

            try:
                db.commit()
            except:
                db.rollback()

        threading.Thread(target=run_memory_update).start()


    return StreamingResponse(stream(), media_type="text/plain")
