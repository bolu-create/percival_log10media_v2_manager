from db import *
from get_manager_1_overview import get_manager_overview
from get_manager_2_data_prep import manager_breakdown
from get_manager_3_final_report import department_report
from f1_generate_pdf import clean_markdown_html_block, format_as_html_email_with_ai
from f2_send_email import send_email_to_staff, generate_pdf_from_html
from functions import get_manager_usernames, add_company_report, add_manager_report, get_staff_email_by_username, get_user_id_by_username#, get_staff_under_manager
from f3_email_manager_on_staff import send_email_to_staff_for_no_response

from functions2 import get_kpi_report_stats_latest, get_staff_under_manager # These weren't importing from "functions" Don't know why




def run_code(session, manager_name):

    # Create the table in the database
    Base.metadata.create_all(engine)
    # Bind sessionmaker and create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get users email
    to= get_staff_email_by_username(session, manager_name)
    
    #get_manager_overview
    overview = get_manager_overview(session, to)
    
    #manager_breakdown
    #breakdown = manager_breakdown(overview)
    breakdown = manager_breakdown(session, overview)
    
    #department_report
    report = department_report(breakdown)
    
    # Save report to db
    add_manager_report(session, manager_name, report)
    
    # Make appropriate format type for email
    html_report = clean_markdown_html_block(format_as_html_email_with_ai(report))
    
    # Generate PDF and save it in a temporary file. Will have to replace with an S3 bucket later in the future
    pdf_path = generate_pdf_from_html(html_report, filename="output.pdf")
    
    # convert to pdf and send as email attachment
    body = f"Hello {manager_name}, please find attached a report on the performance of your staffs"
    subject = f"Percival Weekly Update for {manager_name}"
    
    # Next I NEED A FUNCITON THAT CAN GET THE USER EMAIL
    
    if manager_name:  #!= "Boluwatife M":
        send_email_to_staff(to, subject, body, pdf_path)
        
    session.close()
    
    





if __name__ == "__main__":
    # Code to run when file is executed directly
    now = datetime.today()
    day = now.strftime("%A")  # e.g., 'Friday', 'Saturday', etc.
    hour = now.hour  # UTC hour
    
    # SEND REMINDER
    #if day:
    if day == "Saturday" and hour == 7:
        managers= get_manager_usernames(session)
        print(managers)
        for manager in managers:
            
            if manager:
            #if manager == "Boluwatife M":                
                # After run_code has done its own thing, lets check for those who didn't submit
                staffs = get_staff_under_manager(session, manager)
                non_submitters = []
                date_of_report = ""
                
                # Block 
                if isinstance(staffs, list):
                    for staff in staffs:
                        user_id= get_user_id_by_username(session, staff)
                        
                        submitted, date_of_report = get_kpi_report_stats_latest(session, user_id)
                        if submitted:
                            pass
                        else:
                            non_submitters.append(staff)         
                else:
                    pass
                
                # Block 
                if non_submitters:
                    # send email bla bla
                    #body = f"The names of those who didn't respond to the KPI progress emails for the date {date_of_report}, are as follows: {", ".join(non_submitters)}"
                    body = f"""The names of those who didn't respond to the KPI progress emails are as follows: {", ".join(non_submitters)}. 
                    
                    The name of their manager is {manager}. Please use this info to personalize the message you want to send"""
                    
                    to = get_staff_email_by_username(session, manager)
                    subject = f"Pending Submissions for This Week" #{date_of_report}"
                    
                    send_email_to_staff_for_no_response(to, subject, body)
                else:
                    pass
                    
        print("DONE with all Managers")
        
        
        
    # GENERATE REPORT
    if day == "Monday" and hour == 6:
        managers= get_manager_usernames(session)
        print(managers)
        for manager in managers:
            
            if manager:
            #if manager == "Boluwatife M":
            #if manager == "Chuks":                                       
                run_code(session, manager)
                print(f"DONE with Manager {manager}")
                
        print("DONE with all Managers")
    

#deploy string

