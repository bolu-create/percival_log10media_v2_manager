from db import *
from get_manager_1_overview import get_manager_overview
from get_manager_2_data_prep import manager_breakdown
from get_manager_3_final_report import department_report
from f1_generate_pdf import clean_markdown_html_block, format_as_html_email_with_ai
from f2_send_email import send_email_to_staff, generate_pdf_from_html
from functions import get_manager_usernames, add_company_report, add_manager_report, get_staff_email_by_username



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
    
    if manager_name == "Boluwatife M":
        send_email_to_staff(to, subject, body, pdf_path)
        
    session.close()
    
    
    

if __name__ == "__main__":
    # Code to run when file is executed directly
    managers= get_manager_usernames(session)

    print(managers)
    for manager in managers:
        #if manager:
        if manager == "Boluwatife M":
            run_code(session, manager)
            print(f"DONE with Manager {manager}")
            
    print("DONE with all Managers")
    

#deploy string

