from db import User, KPIReportTracking
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime


def get_staff_email_by_username(session, username: str) -> str | None:
    """Return the staff email given their username, or None if not found."""
    user = session.query(User).filter(User.username == username).first()
    return user.email if user else None


"""
def get_manager_usernames(session) -> list[str]:
    "#""
    Fetches all usernames for users who are managers.
    "#""
    managers = session.query(User.username).filter(User.role == 'manager').all()
    # managers is a list of tuples like [('Alice',), ('Bob',)]
    return [username for (username,) in managers]
"""
def get_manager_usernames(session) -> list[str]:
    """
    Fetch usernames of all users who act as managers in the LineManagerStaff map.
    This now includes administrators (who can manage managers), managers,
    and staff who are themselves mapped as managers of others.
    """
    from sqlalchemy.orm import aliased

    # Aliases for clarity
    Manager = aliased(User)
    Staff = aliased(User)

    managers = (
        session.query(Manager.username)
        .join(LineManagerStaff, LineManagerStaff.manager_id == Manager.id)
        .join(Staff, LineManagerStaff.staff_id == Staff.id)
        .filter(Manager.role.in_(["administrator", "manager", "staff"]))
        .distinct()
        .all()
    )

    # flatten results from [('Alice',), ('Bob',)] → ['Alice', 'Bob']
    return [username for (username,) in managers]










from sqlalchemy.orm import Session
from datetime import datetime
from db import User, Company, LineManagerStaff, ManagerReport, CompanyReport


def add_manager_report(session, manager_name, report_content, report_date=None):
    """
    Add a manager report by manager name.
    """
    manager = session.query(User).filter(User.username == manager_name).first()
    if not manager:
        raise ValueError(f"No manager found with name '{manager_name}'")

    if report_date is None:
        report_date = datetime.today()

    new_report = ManagerReport(
        manager_id=manager.id,
        manager_name=manager.username,
        report_date=report_date,
        report_content=report_content
    )
    session.add(new_report)
    session.commit()
    return new_report


def add_company_report(session, company_name, report_content, report_date=None):
    """
    Add a company-wide report by company name.
    """
    company = session.query(Company).filter(Company.name == company_name).first()
    if not company:
        raise ValueError(f"No company found with name '{company_name}'")

    if report_date is None:
        report_date = datetime.today()

    new_report = CompanyReport(
        company_id=company.id,
        company_name=company.name,
        report_date=report_date,
        report_content=report_content
    )
    session.add(new_report)
    session.commit()
    return new_report





from sqlalchemy.orm import Session
from sqlalchemy import func, desc

def get_kpi_report_stats(session: Session, user_id: int):
    """
    Returns tuple:
      (total_reports, submitted_count, not_submitted_count,
       reminded_not_submitted_count, did_not_submit_count,
       latest_is_submitted)
    """

    # 1. Total reports
    total_reports = session.query(func.count(KPIReportTracking.id)) \
                           .filter_by(user_id=user_id).scalar()

    # 2. Submitted reports
    submitted_count = session.query(func.count(KPIReportTracking.id)) \
                             .filter_by(user_id=user_id, submitted="submitted").scalar()

    # 3. Not submitted (anything not "submitted")
    not_submitted_count = session.query(func.count(KPIReportTracking.id)) \
                                 .filter(KPIReportTracking.user_id == user_id,
                                         KPIReportTracking.submitted != "submitted").scalar()

    # 4a. Reminded but not submitted
    reminded_not_submitted_count = session.query(func.count(KPIReportTracking.id)) \
                                          .filter_by(user_id=user_id, submitted="reminded but did not submit").scalar()

    # 4b. Did not submit
    did_not_submit_count = session.query(func.count(KPIReportTracking.id)) \
                                  .filter_by(user_id=user_id, submitted="did not submit").scalar()

    # 5. Check latest record status
    latest_record = session.query(KPIReportTracking) \
                           .filter_by(user_id=user_id) \
                           .order_by(desc(KPIReportTracking.report_request_date)) \
                           .first()
    latest_is_submitted = (latest_record.submitted == "submitted") if latest_record else False

    latest_is_submitted_str = ""
    if latest_is_submitted == True:
        latest_is_submitted_str = "has submitted the most recent report request"
    else:
        latest_is_submitted_str = "has not submitted the most recent report request"
        
    return (total_reports,
            submitted_count,
            not_submitted_count,
            reminded_not_submitted_count,
            did_not_submit_count,
            latest_is_submitted_str)






def get_kpi_report_stats_late(session: Session, user_id: int) -> Tuple[bool, Optional[datetime]]:
    """
    Returns:
        - A boolean indicating if the latest report was submitted.
        - The date of the latest KPI report (or None if no record exists).
    """
    latest_record = (
        session.query(KPIReportTracking)
        .filter_by(user_id=user_id)
        .order_by(desc(KPIReportTracking.report_request_date))
        .first()
    )

    if latest_record:
        latest_is_submitted = (latest_record.submitted == "submitted")
        latest_date = latest_record.report_request_date
    else:
        latest_is_submitted = False
        latest_date = None

    return latest_is_submitted, latest_date






from sqlalchemy.orm import Session

def get_user_id_by_username(session: Session, username: str):
    """
    Returns the user_id for a given username, or None if not found.
    """
    user = session.query(User).filter_by(username=username).first()
    return user.id if user else None






def get_staff_under_manager(session, manager_username: str):
    """
    Given a manager's username, confirm the user is a manager
    and return a list of staff names managed by them.
    """
    # Find the manager by username
    manager = session.query(User).filter_by(username=manager_username).first()
    
    if not manager:
        return f"❌ No user found with username '{manager_username}'."
    
    if manager.role != "manager":
        return f"⚠️ User '{manager_username}' exists but is not a manager (role = {manager.role})."
    
    # Get staff linked to this manager
    staff_members = (
        session.query(User)
        .join(LineManagerStaff, LineManagerStaff.staff_id == User.id)
        .filter(LineManagerStaff.manager_id == manager.id)
        .all()
    )
    
    if not staff_members:
        return f"ℹ️ Manager '{manager_username}' has no staff assigned."
    
    # Return list of staff names (prefer fullname, fallback to username)
    return [s.fullname or s.username for s in staff_members]
