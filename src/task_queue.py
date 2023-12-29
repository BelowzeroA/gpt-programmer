import os

from sqlalchemy import Column, Integer, String, ForeignKey, Table, types, DateTime, func, MetaData, inspect, and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from file_utils import Utils

utils = Utils()
data_dir = utils.path_from_root('data')
database_path = os.path.join(data_dir, "tables.db")


class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True)
    description = Column(String)
    filename = Column(String)
    result_filename = Column(String)
    status = Column(String)
    error_message = Column(String)
    chat_id = Column(Integer)
    complete = Column(Integer, default=0)
    notification_sent = Column(Integer, default=0)
    add_time = Column(DateTime(timezone=True), server_default=func.now())
    completion_time = Column(types.DateTime)


class TaskQueue:

    def __init__(self):
        self.tasks = []
        self.engine = create_engine(f"sqlite:///{database_path}")
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()

    def add_task(self, chat_id, task_description, filename) -> int:
        task = Task()
        task.description = task_description
        task.filename = filename
        task.chat_id = chat_id
        task.status = 'queued'
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task.task_id

    def mark_as_notified(self, task: Task):
        task.notification_sent = 1
        self.session.add(task)
        self.session.commit()

    def get_completed_unnotified_tasks(self):
        return self.session.query(Task).\
            filter(and_(Task.complete == 1, Task.notification_sent == 0)).all()

    def get_uncompleted_tasks(self):
        return self.session.query(Task).\
            filter(and_(Task.complete == 0, Task.status != "error")).all()

    def get_task(self, task_id):
        task_id = int(task_id)
        task = self.session.query(Task).get(task_id)
        return task


def init_database():
    engine = create_engine(f"sqlite:///{database_path}", echo=True)
    if not inspect(engine).has_table(Task.__tablename__):
        metadata = MetaData()
        # Create a table with the appropriate Columns
        Table(Task.__tablename__, metadata,
            Column('task_id', Integer, primary_key=True),
            Column('description', String),
            Column('filename', String),
            Column('chat_id', Integer),
            Column('complete', Integer),
            Column('notification_sent', Integer),
            Column('add_time', DateTime(timezone=True), server_default=func.now()),
            Column('completion_time', types.DateTime)
        )
        metadata.create_all(engine)

    queue = TaskQueue()
    queue.add_task('123456789', 'Test task', 'test.csv')


if __name__ == "__main__":
    init_database()