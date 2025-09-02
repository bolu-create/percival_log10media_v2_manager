# FOR THE EMAILER THAT NOTIFIES THE USER
"""
def get_kpi_report_stats_latest(session: Session, user_id: int):
    # Check latest record status
    latest_record = session.query(KPIReportTracking) \
                           .filter_by(user_id=user_id) \
                           .order_by(desc(KPIReportTracking.report_request_date)) \
                           .first()
    latest_is_submitted = (latest_record.submitted == "submitted") if latest_record else False
        
    return latest_is_submitted
"""
from db import User, KPIReportTracking
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from db import User, Company, LineManagerStaff, ManagerReport, CompanyReport
from sqlalchemy.orm import Session
from sqlalchemy import func, desc


def get_kpi_report_stats_latest(session: Session, user_id: int):
    # Check latest record status
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
    #return [s.fullname or s.username for s in staff_members]
    return [s.username for s in staff_members]
    
