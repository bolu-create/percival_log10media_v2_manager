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


def get_kpi_report_stats_latest(session: Session, user_id: int):
    # Check latest record status
    latest_record = session.query(KPIReportTracking) \
                           .filter_by(user_id=user_id) \
                           .order_by(desc(KPIReportTracking.report_request_date)) \
                           .first()
    latest_is_submitted = (latest_record.submitted == "submitted") if latest_record else False
        
    return latest_is_submitted