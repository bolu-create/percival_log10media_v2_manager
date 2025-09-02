from sqlalchemy import *
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
from langchain_community.utilities.sql_database import SQLDatabase
import os
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_engine_for_mysql_db():
    """Connect to a remote MySQL database and create an engine."""
    # Get credentials from environment variables
    username = os.getenv("MY_USERNAME")
    password = os.getenv("PASSWORD")
    host = os.getenv("SQL_HOST_SERVER")
    #database = os.getenv("DB_DATABASE")
    database = "percival_db_log10media"
    
    #database = "percival_db"
    port = os.getenv("DB_PORT", 3306)  # Default MySQL port is 3306
    # MySQL connection string
    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    # Create SQLAlchemy engine
     # Create SQLAlchemy engine with connection pooling and pre-ping
    engine = create_engine(
        connection_string,
        pool_recycle=1800,  # Recycle connections every 30 minutes
        pool_pre_ping=True,  # Ensure the connection is alive before using it
        pool_size=10,  # Number of connections in the pool
        max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
        connect_args={"connect_timeout": 10}  # Timeout in seconds for connecting to the server
    )
    return engine
# Get engine for MySQL database
engine = get_engine_for_mysql_db()
# Create SQLDatabase instance for LangChain
db = SQLDatabase(engine)


Base = declarative_base()


# COMPANY
class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    industry = Column(Text)
    #overall_goal = Column(Text)  # Optional
    description = Column(Text)  # Optional longer desc
    created_at = Column(DateTime, default=datetime.utcnow)
    # ✅ Add this line to fix the mapper error
    departments = relationship("Department", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}'>"


user_departments = Table(
    'user_departments',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('department_id', Integer, ForeignKey('departments.id'), primary_key=True)
)

score_departments = Table(
    'score_departments', Base.metadata,
    Column('score_id',     Integer, ForeignKey('user_scores.id'),    primary_key=True),
    Column('department_id',Integer, ForeignKey('departments.id'),   primary_key=True),
)

# DEPARTMENT
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    #description = Column(Text, nullable=False) #***************************************************************8
    company_id = Column(Integer, ForeignKey('companies.id'))

    company = relationship("Company", back_populates="departments")
    
    # Updated relationship:
    users = relationship(
        "User",
        secondary=user_departments,
        back_populates="departments"
    )
    
    user_scores = relationship(
        "UserScores",
        secondary=score_departments,
        back_populates="departments"
    )

    
# AGENT DETAILS
class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100))  # Optional
    company_id = Column(Integer, ForeignKey('companies.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    email = Column(String(255))  # For agent comms
    
    company = relationship("Company", backref="agents")
    department = relationship("Department", backref="agent_department")
    

# COMPANY GOALS
class CompanyGoal(Base):
    __tablename__ = 'company_goals'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    goal = Column(Text)
    #due_date = Column(Date)

    company = relationship("Company", backref="goals")
    

# DEPARTMENTAL GOALS
class DepartmentGoal(Base):
    __tablename__ = 'department_goals'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    goal = Column(Text)

    company = relationship("Company", backref="department_goals")
    department = relationship("Department", backref="goals")


# USER
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(255), unique=True) #new adition for phone numbers
    username = Column(String(100), unique=True, nullable=False)
    fullname = Column(String(100))
    role = Column(Enum('manager', 'staff', name='user_roles'))
    job_title = Column(String(100))
    job_description = Column(Text)
    job_level = Column(String(50))
    cv_url = Column(String(255))
    
    country = Column(Text) #New important addition !!!!!!! Please Update!
    created_at = Column(DateTime, default=datetime.utcnow)
    password = Column(String(255), nullable=False) #New Here. Needs Important Attention !!!!!!!!

    company = relationship("Company", backref="users")
    # Updated relationship: 
    departments = relationship(
        "Department",
        secondary=user_departments,  # use the association table
        back_populates="users"
    )



class LineManagerStaff(Base):
    __tablename__ = 'line_manager_staff'
    id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    manager = relationship("User", foreign_keys=[manager_id], backref="managed_staff")
    staff = relationship("User", foreign_keys=[staff_id], backref="line_manager")



# KPI
class KPI(Base):
    __tablename__ = 'kpis'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_by_id = Column(Integer, ForeignKey('users.id'))
    company_goal_id = Column(Integer, ForeignKey('company_goals.id'), nullable=True)
    department_goal_id = Column(Integer, ForeignKey('department_goals.id'), nullable=True)
    company_goal_for_kpi = Column(Text)
    department_goal_for_kpi = Column(Text)
    
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = Column(Text)
    company_id = Column(Integer, ForeignKey('companies.id'))

    name = Column(Text)#Column(String(255))### .......................................Changes here
    #target = Column(Text)
    description = Column(Text)
    unit = Column(Text)
    period = Column(Enum('monthly', 'quarterly', 'annually', 'custom', name='kpi_periods'))
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], backref="assigned_kpis")
    created_by = relationship("User", foreign_keys=[created_by_id], backref="created_kpis")
    company_goal = relationship("CompanyGoal", backref="kpis")
    department_goal = relationship("DepartmentGoal", backref="kpis")
    

# KPI TARGET BREAKDOWN
class KPIBreakdown(Base):
    __tablename__ = 'kpi_breakdowns'
    id = Column(Integer, primary_key=True)
    kpi_id = Column(Integer, ForeignKey('kpis.id'))
    #breakdown_value = Column(Float)
    breakdown_value = Column(Text)
    breakdown_period = Column(Enum('daily', 'weekly', 'monthly', 'quarterly', 'annually', 'custom', name='kpi_breakdown_periods'))

    kpi = relationship("KPI", backref="breakdowns")



# KPI PROGRESS
class KPIProgress(Base):
    __tablename__ = 'kpi_progress'
    id = Column(Integer, primary_key=True)
    kpi_id = Column(Integer, ForeignKey('kpis.id'))
    kpi_breakdown_id = Column(Integer, ForeignKey('kpi_breakdowns.id'), nullable=True)
    date = Column(Date)
    actual_value = Column(Text)
    fulfilled = Column(Boolean)
    user_notes = Column(Text)
    assistant_feedback= Column(Text)

    kpi = relationship("KPI", backref="progress_entries")
    breakdown = relationship("KPIBreakdown", backref="progress_entries")




# Will use this to track pending requests
class KPIReportTracking(Base):
    __tablename__ = 'kpi_report_tracking'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))    
    report_request_date = Column(Date)
    report_request_details = Column(Text)
    submitted = Column(Text, default="pending")




from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
class ReminderRecord(Base):
    __tablename__ = 'reminder_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey('kpi_report_tracking.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    record_note = Column(Text)
    reminded = Column(Text)
    created_at = Column(DateTime, default=datetime.today())

    # Relationship to access the user from the reminder
    user = relationship("User", backref="reminder_records")

def add_reminder_record(session, user_id, record_id, record_note, reminded_text):
    new_record = ReminderRecord(user_id=user_id, record_id=record_id, record_note= record_note, reminded=reminded_text)
    session.add(new_record)
    session.commit()
    #return new_record

def get_all_reminder_records(session):
    return session.query(ReminderRecord).all()

def get_reminder_record_by_id(session, user_id):
    return session.query(ReminderRecord).filter_by(user_id=user_id).first()




# SURVEY RESPONSES
class SurveyResponse(Base):
    __tablename__ = 'survey_responses'
    id = Column(Integer, primary_key=True)
    respondent_id = Column(Integer, ForeignKey('users.id'))
    subject_id = Column(Integer, ForeignKey('users.id'))  # person being rated
    period = Column(Enum('monthly', 'quarterly', 'annually', name='survey_periods'))
    rating_area = Column(String(255))  # e.g., "Teamwork", "Quality of Work"
    rating_value = Column(Integer)  # 1-5 or 1-10
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    respondent = relationship("User", foreign_keys=[respondent_id], backref="given_surveys")
    subject = relationship("User", foreign_keys=[subject_id], backref="received_surveys")
    


from datetime import datetime, timezone
class UserScores(Base):
    __tablename__ = 'user_scores'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    user_id    = Column(Integer, ForeignKey('users.id'))
    kpi_id    = Column(Integer, ForeignKey('kpis.id')) 
    updated_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    performance_summary= Column(Text)
    performance_score  = Column(Integer)
    actual_value = Column(Text)#***************************************#
    fulfilled = Column(Boolean)#***************************************#
    achieved_total= Column(Integer)
    KPI_finally_fulfilled= Column(Boolean)
    probability_of_KPI_completion=Column(Text)

    company = relationship("Company", backref="user_scores")
    # drop the departments relationship entirely
    departments = relationship(
        "Department",
        secondary=score_departments,
        back_populates="user_scores"
    )


#................................................................
# LOGIC USE CASES
#................................................................
class PercivalChatHistory(Base):
    __tablename__ = "percival_chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)  # Surrogate primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Common ID
    email = Column(Text, nullable=False) # primary_key=True)
    name = Column(String(255), nullable=False)
    user_message = Column(Text, nullable=False)  # 'user' or 'assistant'
    agent_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    

# MANAGER REPORTS
class ManagerReport(Base):
    __tablename__ = "manager_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_name = Column(String(255), nullable=False)
    report_date = Column(Date, nullable=False, default=datetime.utcnow)
    report_content = Column(Text, nullable=True)

    manager = relationship("User", backref="manager_reports")


# COMPANY REPORTS
class CompanyReport(Base):
    __tablename__ = "company_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    report_date = Column(Date, nullable=False, default=datetime.utcnow)
    report_content = Column(Text, nullable=True)

    company = relationship("Company", backref="company_reports")


# Create the table in the database
#Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
# Bind sessionmaker and create session
Session = sessionmaker(bind=engine)
session = Session()






# FIRST FUNCTION
