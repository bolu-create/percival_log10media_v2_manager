from functions import get_kpi_report_stats, get_user_id_by_username


# Check if Due date is passed and if staff had fulfilled KPI by that time'
def check_fulfilled_is_due(due_date, fulfilled, staff_name, date_updated):
    
    x = ''
    if date_updated > due_date  and fulfilled==True:
        x = f"The KPI had already been achieved by {staff_name} at the time of creating this review" 
    elif date_updated < due_date  and fulfilled==True:
        x = f"The KPI had already been achieved by {staff_name} in record time at the time of creating this review" 
    elif date_updated > due_date  and fulfilled==False:
        x = f"The KPI had not been achieved by {staff_name} and the KPI is already due at the time of creating this review" 
    elif date_updated < due_date  and fulfilled==False:
        x = f"The KPI had not been achieved by {staff_name} but the KPI is not yet due at the time of creating this review" 
        
    return x





def manager_breakdown(session, overview):#,dept_name=None):
    manager_name= overview['manager']['name'] 
    manager_email= overview['manager']['email'] 
    manager_company_name= overview['company']['name'] 
    manager_company_industry= overview['company']['industry'] 
    
    managers_departments=overview['departments']
    
    
    departments_info=[]
    for department in managers_departments:
        # We can simply add an if statement to choose thedpt we want to check or get data for
        
        dept_name = department['name']
        dept_goals = department['goals']
        
        #************************************************88
        #dept_staff = managers_departments[0]['staff']
        dept_staff = department['staff'] # this is the correct one

        
        staffs_in_department_details= []#########
        
        for staff_data in dept_staff:
            staff_username = staff_data["username"]
            staff_email= staff_data["email"]
            staff_role= staff_data["role"]
            staff_job_title= staff_data["job_title"]
            staff_job_description= staff_data["job_description"]
            staff_job_level= staff_data["job_level"]
            staff_cv_url= staff_data["cv_url"]
            staff_departments= staff_data["departments"]



            #KPI Data 
            number_for_kpis_string_being_prepared = 0
            total_kpis_for_staff = len(staff_data["kpis"])
            
            # This is to store the KPI infor for each KPI belonging to this staff
            staff_KPI_metadata= []
            
            for staff_data_kpi in staff_data["kpis"]:

                number_for_kpis_string_being_prepared += 1
                
                #kpi_name= staff_data_kpi["name"]
                kpi_name = staff_data_kpi["name"]
                description = staff_data_kpi["description"]
                unit = staff_data_kpi["unit"]
                period = staff_data_kpi["period"]
                due_date = staff_data_kpi["due_date"]
                created_at = staff_data_kpi["created_at"]
                company_goal_for_kpi = staff_data_kpi["company_goal_for_kpi"]
                department_goal_for_kpi = staff_data_kpi["department_goal_for_kpi"]
                staff_kpi_breakdown_info = staff_data_kpi["breakdowns"][0] # A Dict of data # 0 can be replaced with i if the need be
                kpi_breakdown_value = staff_kpi_breakdown_info["value"]
                kpi_breakdown_period = staff_kpi_breakdown_info["period"]
                
    
                #Scores
                staff_data_scores_list= staff_data_kpi["scores"]
                #staff_data_scores_stories=[]

                if staff_data_scores_list:
                    
                    #for staff_data_scores in staff_data_scores_list:
                    staff_data_scores= staff_data_scores_list[-1] #Getting the most recent performance summary report *** This is where this code is different from the first version
                        
                    staff_performance_summary = staff_data_scores["performance_summary"]
                    staff_performance_score = staff_data_scores["performance_score"]
                    staff_score_updated_at = staff_data_scores["updated_at"]
                    staff_departments = staff_data_scores["departments"]
                    staff_actual_value_gotten = staff_data_scores["actual_value"]
                    staff_fulfilled_kpi = staff_data_scores["fulfilled"]
                    staff_achieved_total = staff_data_scores["achieved_total"]
                    staff_KPI_finally_fulfilled = staff_data_scores["KPI_finally_fulfilled"]
                    probability_of_KPI_completion = staff_data_scores["probability_of_KPI_completion"]
                                
                    
                    #Now we want to get the statement illustrating if the person had already fulfilled the kpi
                    update_check = check_fulfilled_is_due(due_date, staff_fulfilled_kpi, staff_username, staff_score_updated_at)
                    user_id = get_user_id_by_username(session, staff_username)
                    total_reports, submitted_count, not_submitted_count, reminded_not_submitted_count, did_not_submit_count, latest_is_submitted = get_kpi_report_stats(session, user_id)
                    #total_reports, submitted_count, not_submitted_count, reminded_not_submitted_count, did_not_submit_count, latest_is_submitted
                    
                    # The Kpi delivery date had already passed by the time this data was recorded. 
                    """
                    KPI ASESSMENT OVER OVERALL PERIOD
                        - The Staff has only fulfilled {staff_achieved_total} {unit} so far.
                        - {kpi_name} is what is expected of the staff to achieve over a {period} period.
                        - Has Staff hit the Kpi target? : {staff_KPI_finally_fulfilled}
                    """
                    
                    
                    my_string = f"""{staff_score_updated_at} PERFORMANCE REPORT AND REVIEW FOR: {staff_username}
                        
                    Below is {staff_username}'s performance summary for kpi '{kpi_name}', with a kpi breakdown value of '{kpi_breakdown_value}' to be fulfilled {kpi_breakdown_period}
                    
                    PERFORMANCE SUMMARY: {staff_performance_summary}
                    
                    PERFORMANCE SCORE: {staff_performance_score}/100 
                    
                    KPI ASESSMENT OVER BREAKDOWN PERIOD
                        - The ACTUAL KPI value achieved by {staff_username} in the breakdown period is: {staff_actual_value_gotten}. 
                        - The EXPECTED KPI value to be achieved in the breakdown period is: {kpi_breakdown_value}.
                    
                    KPI ASESSMENT OVER OVERALL PERIOD
                        - The Staff has only fulfilled {staff_achieved_total} so far.
                        - {kpi_name} is what is expected of the staff to achieve over a {period} period.
                        - Has Staff hit the Kpi target? : {staff_KPI_finally_fulfilled}
                    
                    ASSESSMENT ON STAFF'S LIKELIHOOD TO REACH KPI GOALS BY {due_date}
                        - {probability_of_KPI_completion}
                    
                    Note: {update_check}
                    
                    
                    KPI SUBMISSION DATA
                    This section desribes the consistency of the staff in addressing the KPI report requests i.e sending in their necessary weekly feedbacks
                    upon request. Use this information to inform the manager of wether the staff replied to the most recent round of emails to send their KPI
                    progress feedback. 
                    
                    The total report requests sent so far: {total_reports}
                    The total number of reports responded to by {staff_username} out of the {total_reports} total reports requests: {submitted_count}
                    The total number of unsubmitted reports responded to: {not_submitted_count}
                    
                    ****
                    But note the most important of this is noting if the most recent report request has been submitted. So please note that "{staff_username} {latest_is_submitted}" 
                    ****
                    
                    All of the above must be shown to the manager also and a rating or verdict should be given by you on how well the user responds to KPI report requests.
                    
                    if {staff_username} has not submitted in the above update. You need to clearly inform the manager about this as a topmost priority, so the manager can address it.
                    """  
                    
                    # Cooking The Sentence Per Staff
                    staff_KPI_story = f"""KPI No {number_for_kpis_string_being_prepared}            
                    KPI Name: {kpi_name}
                    Description: {description}
                    Unit: {unit}
                    Period: {period}
                    Due Date: {due_date}
                    Created at: {created_at}
                    Company Goal for KPI: {company_goal_for_kpi}
                    Department Goal for KPI: {department_goal_for_kpi}
                    
                    KPI Breakdown Value: {kpi_breakdown_value}
                    KPI Breakdown Period: {kpi_breakdown_period}
                    
                    Staff Performance Summary:
                    
                    {my_string}
                    """
                    # staff details are added to create list of their details
                    # staff_data_scores_stories.append(staff_KPI_story)

                else:
                    my_string_for_empty= f"There are no Performance Summary Information available just yet for the KPI {kpi_name} for {staff_username}"
                    
                    staff_KPI_story = f"""KPI No {number_for_kpis_string_being_prepared}
                    KPI Name: {kpi_name}
                    Description: {description}
                    Unit: {unit}
                    Period: {period}
                    Due Date: {due_date}
                    Created at: {created_at}
                    Company Goal for KPI: {company_goal_for_kpi}
                    Department Goal for KPI: {department_goal_for_kpi}
                    
                    KPI Breakdown Value: {kpi_breakdown_value}
                    KPI Breakdown Period: {kpi_breakdown_period}
                              
                    {my_string_for_empty}
                    """
                    
                    #staff_data_scores_stories.append(staff_KPI_story) 
                    #staffs_in_department_details.append(staff_story_no_performance_summary)
                
                # This helps reset the KPI counter 
                if number_for_kpis_string_being_prepared == total_kpis_for_staff:
                    number_for_kpis_string_being_prepared = 0
                else:
                    pass
                
                # Add KPI Metadata information for the ffg KPI to the table
                staff_KPI_metadata.append(staff_KPI_story)
                
            
            # We then want to add staff KPI metadata to the staff story (i.e his/her details) to compile it for the final staff report
            staff_story = f"""Staff Name: {staff_username}
            Staff Email: {staff_email}
            Staff Role: {staff_role}
            Staff Job Title: {staff_job_title}
            Staff Job Description: {staff_job_description}
            Staff Job Level: {staff_job_level}
            Staff cv url: {staff_cv_url}"""
            
       
            # This is to store the KPI infor for each KPI belonging to this staff
            staff_KPI_metadata_sentence= "\n\n".join(staff_KPI_metadata)      
            
            # Compile final report for staff and add them the staff_information_report
            staff_final_report= staff_story + staff_KPI_metadata_sentence
            staffs_in_department_details.append(staff_final_report) #So now we have the staff report for this stafff added to out list
            
        
        
        
            
            
        #.................................................................................
        # SWITCHING TO DEPARTMENTS
        #.................................................................................
        department_details = f"""Department name: {dept_name}
        Department Goals: {dept_goals}
        """
        #Join staff info to dept info
        department_with_staff_info = department_details + "\n\n\n" + "\n\n\nSTAFFS DETAILS\n\n\n".join(staffs_in_department_details)        
        departments_info.append(department_with_staff_info)
        
    #.................................................................................
    # SWITCHING TO MANAGER DETAILS
    #.................................................................................
    
    manager_info=f"""Managers Name: {manager_name} 
    Managers Email: {manager_email}
    Manager Company Name: {manager_company_name}
    Manager Company Industry: {manager_company_industry}
    """
    
    #.................................................................................
    # COLLECTING TOTAL INFORMATION
    #.................................................................................
    total_information= manager_info + "\n\n" + "\nDEPARTMENT DETAILS\n\n".join(departments_info)
    
    return total_information
    
    


        
    

