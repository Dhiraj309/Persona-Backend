import re
import requests
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from ..models.user_memory import UserMemory
from ..config import COLAB_URL


def normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


# ----------------------------
# LOAD OR CREATE BASE MEMORY
# ----------------------------
def load_or_create_memory(db: Session, user_id: int) -> UserMemory:
    memory = db.query(UserMemory).filter_by(user_id=user_id).first()
    if not memory:
        memory = UserMemory(user_id=user_id)
        db.add(memory)
        db.flush()
    return memory


def append_unique(lst: list, value: str):
    v = normalize(value)
    if v and v not in lst:
        lst.append(v)


# ----------------------------
# SMART MERGE LOGIC
# ----------------------------
def merge_memory(mem: dict, data: dict):

    # ============ IDENTITY ============
    identity = data.get("identity", {})

    if identity.get("name"):
        mem["identity"]["name"] = identity["name"]

    if identity.get("age"):
        mem["identity"]["age"] = identity["age"]

    for c in identity.get("cities", []):
        append_unique(mem["identity"]["cities"], c)

    for e in identity.get("education", []):
        append_unique(mem["identity"]["education"], e)

    for r in identity.get("roles", []):
        append_unique(mem["identity"]["roles"], r)

    # ============ PREFERENCES ============
    prefs = data.get("preferences", {})

    for f in prefs.get("food", []):
        append_unique(mem["preferences"]["food"], f)

    for m in prefs.get("movies", []):
        append_unique(mem["preferences"]["movies"], m)

    for a in prefs.get("activities", []):
        append_unique(mem["preferences"]["activities"], a)

    for ms in prefs.get("music", []):
        append_unique(mem["preferences"]["music"], ms)

    for h in prefs.get("hobbies", []):
        append_unique(mem["preferences"]["hobbies"], h)

    for o in prefs.get("other", []):
        append_unique(mem["preferences"]["other"], o)

    # ============ SKILLS ============
    for s in data.get("skills", []):
        append_unique(mem["skills"], s)

    # ============ EMOTIONS ============
    emos = data.get("emotions", {})

    for e in emos.get("recurring", []):
        append_unique(mem["emotions"]["recurring"], e)

    for e in emos.get("occasional", []):
        append_unique(mem["emotions"]["occasional"], e)

    # ============ PERSONALITY ============
    personality = data.get("personality", {})
    for t in personality.get("tone", []):
        append_unique(mem["personality"]["tone"], t)

    for tr in personality.get("traits", []):
        append_unique(mem["personality"]["traits"], tr)

    # ============ GOALS ============
    goals = data.get("goals", {})

    for s in goals.get("short_term", []):
        append_unique(mem["goals"]["short_term"], s)

    for l in goals.get("long_term", []):
        append_unique(mem["goals"]["long_term"], l)

    # ============ BIO SUMMARY ============
    if data.get("bio_summary"):
        mem["bio_summary"] = data["bio_summary"]

    return mem


# ----------------------------
# MAIN EXTRACTION PIPELINE
# ----------------------------
def extract_memories_from_llm(db: Session, user_id: int, last_30: list[str], timeout=90):
    if not last_30:
        return

    memory = load_or_create_memory(db, user_id)
    mem = memory.memory_json

    # ---- CALL COLAB ----
    try:
        resp = requests.post(
            f"{COLAB_URL}/memory",
            json={"messages": last_30},
            timeout=timeout
        )
    except:
        return
    
    if resp.status_code != 200:
        return

    try:
        data = resp.json()
    except:
        return

    # ---- MERGE ----
    mem = merge_memory(mem, data)
    memory.memory_json = mem

    flag_modified(memory, "memory_json")

    db.commit()
    db.refresh(memory)
