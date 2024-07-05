import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables

SHEETDB_API_URL = os.getenv('SHEETDB_API_URL')  # Ensure your SheetDB API URL is correctly set in .env

def add_entry(task, start_date, end_date, priority, days_to_go):
    data = {
        "Task": task,
        "Start Date": start_date,
        "End Date": end_date,
        "Priority": priority,
        "Days to go": days_to_go,
        "Status": "Not Completed"  # Default status for new tasks
    }
    print(f"Adding entry: {data}")
    response = requests.post(SHEETDB_API_URL, json=data)
    print(f"Add entry response: {response.text}")
    return response.json()

def get_entries():
    response = requests.get(SHEETDB_API_URL)
    print(f"Get entries response: {response.text}")
    return response.json()

def get_filtered_entries(status=None):
    if status:
        search_url = f"{SHEETDB_API_URL}/search?Status={status}&casesensitive=false"
        print(f"Searching for tasks with URL: {search_url}")
        response = requests.get(search_url)
        print(f"Get filtered entries response: {response.text}")
        return response.json()
    else:
        return get_entries()

def update_entry(task, new_start_date=None, new_end_date=None, new_priority=None, new_days_to_go=None, new_status=None):
    try:
        # Construct the URL for the update operation
        update_url = f"{SHEETDB_API_URL}/Task/{task.replace(' ', '%20')}"
        print(f"Updating task with URL: {update_url}")
        
        updated_entry = {}
        if new_start_date: updated_entry["Start Date"] = new_start_date
        if new_end_date: updated_entry["End Date"] = new_end_date
        if new_priority: updated_entry["Priority"] = new_priority
        if new_days_to_go: updated_entry["Days to go"] = new_days_to_go
        if new_status: updated_entry["Status"] = new_status
        
        data = {"data": updated_entry}
        print(f"Updating entry with data: {data}")
        response = requests.patch(update_url, json=data)
        print(f"Update entry response: {response.text}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def delete_entry(task):
    try:
        # Construct the URL for the delete operation
        delete_url = f"{SHEETDB_API_URL}/Task/{task.replace(' ', '%20')}"
        print(f"Deleting task with URL: {delete_url}")
        
        response = requests.delete(delete_url)
        print(f"Delete entry response: {response.text}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}
