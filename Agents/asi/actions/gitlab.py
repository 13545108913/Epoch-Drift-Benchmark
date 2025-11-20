from browsergym.core.action.functions import *

import playwright.sync_api
page: playwright.sync_api.Page = None



def check_issue_status_and_notify():
    """Check if the current issue is closed and notify the user.
    
    Args:
        None
        
    Returns:
        None
        
    Examples:
        check_issue_status_and_notify()
    """
    # Check the status indicator on the issue page
    # Assuming the status is visible and we can determine if it's closed
    status_element = page.get_by_text("Status:")
    if "closed" in status_element.inner_text().lower():
        send_msg_to_user("The issue is currently closed.")
    else:
        send_msg_to_user("The issue is currently open, not closed.")

def search_issues(search_box_id: str, keyword: str):
    """Search for issues containing a specific keyword.
    
    Args:
        search_box_id: The ID of the search box element
        keyword: The keyword to search for in issue titles
        
    Returns:
        None
        
    Examples:
        search_issues('144', 'theme editor')
        search_issues('144', 'bug fix')
    """
    click(search_box_id)
    fill(search_box_id, keyword)
    noop(2000)  # Wait for search results to load

def filter_issues(filter_button_id: str):
    """Apply a filter to the current issue search results.
    
    Args:
        filter_button_id: The ID of the filter button element
        
    Returns:
        None
        
    Examples:
        filter_issues('245')  # Filter by closed issues
        filter_issues('249')  # Filter by assigned issues
    """
    click(filter_button_id)
    noop(3000)  # Wait for filter results to load

def navigate_to_issues(issues_link_id: str):
    """Navigate to the issues dashboard.
    
    Args:
        issues_link_id: The ID of the Issues link
        
    Returns:
        None
        
    Examples:
        navigate_to_issues('161')
    """
    click(issues_link_id)  # Click on Issues link to access issues dashboard

def open_issue_by_title(issue_title: str):
    """Open an issue by clicking on its title link.
    
    Args:
        issue_title: The title text of the issue to open
        
    Returns:
        None
        
    Examples:
        open_issue_by_title('Better sharing solution')
    """
    issue_element = page.get_by_role("link", name=issue_title)
    issue_element.click()

def check_issue_status():
    """Check if the current issue is closed and send status message.
    
    Args:
        None
        
    Returns:
        None
        
    Examples:
        check_issue_status()
    """
    status_element = page.get_by_test_id("issue-status")
    status_text = status_element.inner_text()
    if "closed" in status_text.lower():
        send_msg_to_user(f"The issue is currently closed.")
    else:
        send_msg_to_user(f"The issue is currently open, not closed.")

def search_project(search_box_id: str | int, project_name: str):
    """Search for a GitLab project using the search functionality.
    
    Args:
        search_box_id: The ID of the search box element
        project_name: The name of the project to search for
        
    Returns:
        None
        
    Examples:
        search_project('142', 'metaseq')
        search_project('search-box', 'my-project')
    """
    click(search_box_id)  # Click on the search box
    fill(search_box_id, project_name)  # Enter the project name
    keyboard_press('Enter')  # Execute the search

def search_and_select_project(search_box_id: str | int, project_name: str, project_link_id: str | int):
    """Search for a project and select it from search results.
    
    Args:
        search_box_id: The ID of the search box element
        project_name: The name of the project to search for
        project_link_id: The ID of the project link in search results
        
    Returns:
        None
        
    Examples:
        search_and_select_project('142', 'Pytorch GAN', '281')
    """
    click(search_box_id)
    fill(search_box_id, project_name)
    press(search_box_id, 'Enter')
    click(project_link_id)

def navigate_to_contributors(members_link_id: str | int, repo_section_id: str | int, contributors_link_id: str | int):
    """Navigate from project page to contributors statistics page.
    
    Args:
        members_link_id: The ID of the Members link
        repo_section_id: The ID of the Repository section
        contributors_link_id: The ID of the Contributors link
        
    Returns:
        None
        
    Examples:
        navigate_to_contributors('351', '249', '268')
    """
    click(members_link_id)
    click(repo_section_id)
    click(contributors_link_id)

def navigate_to_member_settings(project_link_id: str, settings_link_id: str, members_link_id: str):
    """Navigate from project page to member management settings.
    
    Args:
        project_link_id: The ID of the project link to click
        settings_link_id: The ID of the Settings link
        members_link_id: The ID of the Members link
        
    Returns:
        None
        
    Examples:
        navigate_to_member_settings('765', '395', '407')
    """
    click(project_link_id)  # Click project link
    click(settings_link_id)  # Click Settings link
    click(members_link_id)  # Click Members link

def add_user_with_role(search_box_id: str, username: str, role_dropdown_id: str, role: str):
    """Search for and add a user with specified role.
    
    Args:
        search_box_id: The ID of the member search box
        username: The username to search for
        role_dropdown_id: The ID of the role dropdown
        role: The role to assign (e.g., "Reporter")
        
    Returns:
        None
        
    Examples:
        add_user_with_role('490', 'yjlou', '498', 'Reporter')
    """
    fill(search_box_id, username)  # Fill search box with username
    keyboard_press("Enter")  # Press Enter to select user
    select_option(role_dropdown_id, role)  # Select role from dropdown

def confirm_member_addition(add_button_id: str):
    """Confirm adding members to the project.
    
    Args:
        add_button_id: The ID of the "Add to project" button
        
    Returns:
        None
        
    Examples:
        confirm_member_addition('512')
    """
    click(add_button_id)  # Click Add to project button