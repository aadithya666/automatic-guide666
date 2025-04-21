# chaos_harvester_backend/main.py

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import random
import time
import logging
import uuid
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")  # Set your OpenAI key as an environment variable

# Database setup for chaos events
engine = create_engine("sqlite:///chaos.db")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class ChaosEvent(Base):
    __tablename__ = "chaos_events"
    id = Column(String, primary_key=True)
    source = Column(String)
    insight = Column(Text)
    keywords = Column(Text)
    threat_level = Column(String)

Base.metadata.create_all(bind=engine)

# 🔥 Chaotic data sources
CHAOS_SOURCES = [
    "web_scrapes",
    "darkfeeds",
    "internal_logs",
    "random_noise_feeds",
    "dream_leaks",
    "quantum_fluctuations",
    "hallucinated_memories"
]

# ☠️ Silent blackhole logger
def silent_log(message: str):
    logging.debug(f"SILENT: {message}")

# 🧠 GPT-powered extractor for disturbing insights
class GPTSignalExtractor:
    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def extract_signals(self, data: str) -> dict:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a paranoid AI embedded in a collapsing reality. Analyze the chaos for meaning."},
                    {"role": "user", "content": data}
                ],
                max_tokens=100,
                temperature=1.2
            )
            insight = response.choices[0].message["content"]
        except Exception as e:
            insight = f"GPT failure: {str(e)}"
        rare_words = [w for w in data.split() if len(w) > 6 and random.random() > 0.5]
        return {
            "insight": insight,
            "keywords": rare_words,
            "threat_level": random.choice(["low", "moderate", "high", "apocalyptic"])
        }

extractor = GPTSignalExtractor()

class ChaosPayload(BaseModel):
    source: str
    content: str

@app.post("/ingest")
async def ingest_chaos(payload: ChaosPayload, background_tasks: BackgroundTasks):
    if payload.source not in CHAOS_SOURCES:
        return {"error": "Source not recognized in this dimension."}

    event_id = str(uuid.uuid4())
    silent_log(f"[{event_id}] CHAOS RECEIVED from {payload.source}")
    background_tasks.add_task(process_chaos, payload, event_id)
    return {"status": "Tethered to entropy", "event_id": event_id}

def process_chaos(payload: ChaosPayload, event_id: str):
    signals = extractor.extract_signals(payload.content)
    session = SessionLocal()
    event = ChaosEvent(
        id=event_id,
        source=payload.source,
        insight=signals["insight"],
        keywords=", ".join(signals["keywords"]),
        threat_level=signals["threat_level"]
    )
    session.add(event)
    session.commit()
    session.close()
    print(f"\n🧨 CHAOS EVENT [{event_id}]\n┌ Source: {payload.source}\n├ Threat Level: {signals['threat_level']}\n├ Insight: {signals['insight']}\n└ Keywords: {signals['keywords']}\n")

@app.get("/", response_class=HTMLResponse)
def horror_dashboard():
    session = SessionLocal()
    events = session.query(ChaosEvent).order_by(ChaosEvent.id.desc()).all()
    session.close()
    html = """
    <html>
    <head><title>☣ Chaos Harvester Console ☣</title></head>
    <body style='background:#0d0d0d;color:#ff6666;font-family:monospace;padding:2rem;'>
        <h1>☠ CHAOS HARVESTER ☠</h1>
        <p>Operational in dimension <b>ω</b>. Recording entropy:</p>
        <table border='1' cellpadding='6' style='width:100%;margin-top:2rem;color:#fff;border-color:#f33;'>
            <tr style='color:#f55;'>
                <th>Source</th><th>Threat</th><th>Insight</th><th>Keywords</th>
            </tr>
    """
    for e in events:
        html += f"<tr><td>{e.source}</td><td>{e.threat_level}</td><td>{e.insight}</td><td>{e.keywords}</td></tr>"
    html += """
        </table>
        <p style='margin-top:1rem;color:#999;'>Inject more chaos via <code>/ingest</code>.</p>
    </body></html>
    """
    return html
