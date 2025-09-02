from sqlalchemy.orm import Session
from datetime import datetime
from db import User, KPI, LineManagerStaff, UserScores


def get_manager_overview(session, manager_email: str) -> dict:
    """
    Returns a full “department overview” for the given manager:
      - Company name
      - Departments the manager belongs to
      - Department goals
      - Staff under each department (with full user info)
      - Each staff’s KPIs, KPI breakdowns & progress entries
      - Each staff’s latest performance score & summary
    """
    # 1. Find the manager
    manager = session.query(User).filter_by(email=manager_email).first()
    if not manager:
        raise ValueError(f"No user found with email {manager_email}")

    company = manager.company
    # 2. Which departments the manager “handles”?
    #    (We assume a manager is linked to the depts via User.departments)
    depts = manager.departments

    # 3. Gather company‐level goals
    company_goals = [g.goal for g in company.goals]

    overview = {
        "manager": {
            "id": manager.id,
            "name": manager.username,
            "email": manager.email,
            "role": manager.role,
        },
        "company": {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "goals": company_goals,
        },
        "departments": []
    }

    for dept in depts:
        # Department‐level goals
        dept_goals = [g.goal for g in dept.goals]

        # All staff reporting to this manager *who are in this department*
        # (via the LineManagerStaff link)
        links = session.query(LineManagerStaff).filter_by(manager_id=manager.id).all()
        staff_in_dept = [
            link.staff for link in links
            #if dept in link.staff.departments #,,,,,,,..,.......................,,,,,,,,,,,,,
        ]

        staff_data = []
        for staff in staff_in_dept:
            # Basic user info
            user_info = {
                "id": staff.id,
                "username": staff.username,
                "email": staff.email, 
                "role": staff.role,
                "job_title": staff.job_title, 
                "job_description": staff.job_description,
                "job_level": staff.job_level, 
                "cv_url": staff.cv_url, # Not
                "departments": [d.name for d in staff.departments], # Not
            }

            # KPIs + breakdowns + progress
            kpis = []
            for kpi in staff.assigned_kpis:
                breakdowns = [
                    {
                        "id": bd.id,  # Not
                        "value": bd.breakdown_value,
                        "period": bd.breakdown_period,
                    }
                    for bd in kpi.breakdowns  
                ]
                progress = [ #I will have to get the very last progress entry here  
                    {
                        "id": p.id,
                        "date": p.date.isoformat(), #
                        "actual_value": p.actual_value, #
                        "fulfilled": p.fulfilled, #
                        "user_notes": p.user_notes,
                        "assistant_feedback": p.assistant_feedback,#
                    }
                    for p in kpi.progress_entries
                ]
                

                #This person has x {period} to reach his Kpi: {}. he has so far achieved xyz {kpi unit} 
                # I need a function to calculate how many total units the client has achieved over time till the current date
                # I want to also be able to find the period elapsed

                # Latest performance score(s)
                scores = session.query(UserScores).filter_by(kpi_id=kpi.id).all()
                score_data = [
                    {
                        "id": s.id,
                        "performance_summary": s.performance_summary, #
                        "performance_score": s.performance_score, #
                        "updated_at": s.updated_at.isoformat(), #
                        "departments": [d.name for d in s.departments],
                        "actual_value": s.actual_value,#******************************#
                        "fulfilled": s.fulfilled, #******************************#
                        "achieved_total": s.achieved_total,
                        "KPI_finally_fulfilled": s.KPI_finally_fulfilled,
                        "probability_of_KPI_completion": s.probability_of_KPI_completion,
                    }
                    for s in scores # I will need just the last performance summary on this
                ]
                
                kpis.append({
                    "id": kpi.id,
                    "name": kpi.name, #
                    "description": kpi.description, #
                    "unit": kpi.unit, #
                    "period": kpi.period, # This person is checked for kpi responses every {period}
                    "due_date": kpi.due_date.isoformat() if kpi.due_date else None, #
                    "created_at": kpi.created_at.isoformat(),# need this for later functions
                    "company_goal_for_kpi": kpi.company_goal_for_kpi, 
                    "department_goal_for_kpi": kpi.department_goal_for_kpi, # How does this client performance aid or heamper meeting company goals
                    "breakdowns": breakdowns,
                    "progress_entries": progress,
                    "scores": score_data
                })      
    
            user_info["kpis"] = kpis
            #user_info["scores"] = score_data
            staff_data.append(user_info)

        overview["departments"].append({
            "id": dept.id,
            "name": dept.name,
            "goals": dept_goals,
            "staff": staff_data
        })

    return overview

