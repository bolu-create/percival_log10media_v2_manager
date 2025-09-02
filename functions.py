from db import User, KPIReportTracking



def get_staff_email_by_username(session, username: str) -> str | None:
    """Return the staff email given their username, or None if not found."""
    user = session.query(User).filter(User.username == username).first()
    return user.email if user else None



def get_manager_usernames(session) -> list[str]:
    """
    Fetches all usernames for users who are managers.
    """
    managers = session.query(User.username).filter(User.role == 'manager').all()
    # managers is a list of tuples like [('Alice',), ('Bob',)]
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





from sqlalchemy.orm import Session

def get_user_id_by_username(session: Session, username: str):
    """
    Returns the user_id for a given username, or None if not found.
    """
    user = session.query(User).filter_by(username=username).first()
    return user.id if user else None