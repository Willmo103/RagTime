import uuid, datetime as dt, pandas as pd
from app.config import _log as log, DB_URL
from sqlalchemy import Table, create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Mapped

log = log.getLogger(__name__)


engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()
log.debug("Database engine created")

conversation_topic_association = Table(
    "conversation_topic",
    Base.metadata,
    Column("conversation_id", String, ForeignKey("conversation.id")),
    Column("topic_id", String, ForeignKey("topic.id")),
)


class SMS(Base):
    __tablename__ = "sms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender = Column(String, nullable=False)
    message = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    date = Column(String, nullable=False)
    thread_id = Column(String, ForeignKey("threads.id"))
    thread = relationship("Thread", back_populates="sms_messages")

    def __init__(
        self,
        sender: str,
        message: str,
        timestamp: dt.datetime,
        date: str,
        thread_id: str,
        thread=None,
    ) -> None:
        self.sender: str = sender
        self.message: str = message
        self.timestamp: dt.datetime = timestamp
        self.date: str = date
        self.thread_id: str = thread_id
        self.thread = thread

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp,
            "date": self.date,
            "thread_id": self.thread_id,
        }


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(String, nullable=False)
    summary = Column(String)
    topics = relationship(
        "Topic",
        secondary=conversation_topic_association,
        back_populates="conversations",
    )
    notes = Column(String)
    thread_id = Column(String, ForeignKey("threads.id"))
    thread = relationship("Thread", back_populates="conversations")
    date = Column(DateTime, nullable=False)

    def __init__(
        self, content: str, thread_id: str, thread=None, date: dt.date = None
    ) -> None:
        self.content: str = content.strip()
        self.topics: Mapped[Topic] = []
        self.summary: str = None
        self.notes: str = None
        self.thread_id: str = thread_id
        self.thread: Thread = thread
        self.date: dt.date = date

    def add_to(self, file: str) -> None:
        with open(file, "a") as f:
            f.write(self.content)

    def req_body(self, notes: str) -> str:
        return f'{{"conversation": "{self.content}", "notes": "{notes}", "topics": {self.topics}}}'

    def update(self, details: dict) -> None:
        try:
            self.summary = details["summary"]
            self.notes = details["notes"]
            o_topics = details["topics"]
            for topic in o_topics:
                if topic not in self.topics:
                    self.topics.append(Topic(topic))

        except KeyError as e:
            log.exception(e, "Conversation.update: Failed to update conversation.")
            return None


class Topic(Base):
    __tablename__ = "topic"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String, nullable=False)
    conversations = relationship(
        "Conversation",
        secondary=conversation_topic_association,
        back_populates="topics",
    )

    def __init__(self, topic: str):
        self.topic: str = topic
        with Session() as session:
            o_topic = session.query(Topic).filter(Topic.topic == self.topic).first()
            if o_topic is None:
                session.add(self)
                session.commit()
            else:
                return o_topic

    def __eq__(self, other):
        if isinstance(other, Topic):
            return self.topic == other.topic
        elif isinstance(other, str):
            return self.topic == other
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.topic)

    def __dict__(self):
        return {
            "topic": self.topic,
        }


class Thread(Base):
    __tablename__ = "threads"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    sms_messages: Mapped[SMS] = relationship(
        "SMS", back_populates="thread", collection_class=list
    )
    conversations: Mapped[Conversation] = relationship(
        "Conversation", back_populates="thread", collection_class=list
    )

    def __init__(self, name: str = None) -> None:
        self.name: str = name
        self.sms_messages: Mapped[SMS]
        self.conversations: Mapped[Conversation]


Base.metadata.create_all(engine)
log.debug("SMS database tables created")
