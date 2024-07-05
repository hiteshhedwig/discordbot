from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, File
import sheetdb_helper as sdh
from generate_table_image import generate_table_image
from dateutil import parser
from datetime import datetime
import re

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

def format_tasks_as_table(entries):
    headers = ["Task", "Start Date", "End Date", "Priority", "Days to go", "Status"]
    data = []
    for entry in entries:
        row = [entry.get(header, "") for header in headers]
        data.append(row)
    return data, headers

def parse_date(date_str):
    try:
        return parser.parse(date_str, fuzzy=True)
    except parser.ParserError:
        return None

def interpret_command(user_message):
    user_message = user_message.lower().strip()
    
    # Pattern for adding tasks
    if re.search(r'\badd\b.*\btask\b', user_message):
        return 'add task'
    
    # Extended pattern for getting tasks
    if re.search(r'\b(get|give|show|see|view|display|list)\b.*\b(completed|uncompleted|all)\b.*\btasks?\b', user_message):
        return 'get tasks'
    
    # Pattern for updating tasks
    if re.search(r'\bupdate\b.*\btask\b', user_message):
        return 'update task'
    
    # Pattern for marking tasks as completed
    if re.search(r'\bmark\b.*\b(task\b.*\bcompleted|task\b.*\buncompleted)\b', user_message):
        return 'mark task'
    
    # Pattern for deleting tasks
    if re.search(r'\bdelete\b.*\btask\b', user_message):
        return 'delete task'
    
    return None

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("(Message was empty because intents were not enabled)")
        return

    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message[1:]

    try:
        command = interpret_command(user_message)
        response: str = ""

        if command == 'add task':
            parts = user_message.split(',')
            if len(parts) == 4:
                task, start_date_str, end_date_str, priority = parts
                start_date = parse_date(start_date_str.strip())
                end_date = parse_date(end_date_str.strip())
                if start_date and end_date:
                    days_to_go = (end_date - start_date).days
                    sdh.add_entry(task.strip(), start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), priority.strip(), str(days_to_go))
                    response = 'Task added to Google Sheet.'
                else:
                    response = 'Invalid date format. Please provide dates in a recognizable format like "3 June" or "3June".'
            else:
                response = 'Invalid format. Use "add task task, start_date, end_date, priority"'
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)

        elif command == 'get tasks':
            status_match = re.search(r'\b(completed|uncompleted|all)\b', user_message)
            status = status_match.group(1) if status_match else None
            if status == 'all':
                entries = sdh.get_entries()
            else:
                status = "Completed" if status == "completed" else "Not Completed"
                entries = sdh.get_filtered_entries(status)
            print(f"Filtered entries: {entries}")
            data, headers = format_tasks_as_table(entries)
            if not data:
                response = "No tasks found."
                if is_private:
                    await message.author.send(response)
                else:
                    await message.channel.send(response)
            else:
                filename = generate_table_image(data, headers)
                with open(filename, 'rb') as f:
                    picture = File(f)
                    if is_private:
                        await message.author.send(file=picture)
                    else:
                        await message.channel.send(file=picture)

        elif command == 'update task':
            parts = user_message.replace('update task ', '').split(',')
            if len(parts) == 4:
                task, new_start_date_str, new_end_date_str, new_priority = parts
                new_start_date = parse_date(new_start_date_str.strip())
                new_end_date = parse_date(new_end_date_str.strip())
                if new_start_date and new_end_date:
                    new_days_to_go = (new_end_date - new_start_date).days
                    result = sdh.update_entry(task.strip(), new_start_date.strftime('%Y-%m-%d'), new_end_date.strftime('%Y-%m-%d'), new_priority.strip(), str(new_days_to_go))
                    if 'error' in result:
                        response = f"Error updating task: {result['error']}"
                    else:
                        response = 'Task updated in Google Sheet.'
                else:
                    response = 'Invalid date format. Please provide dates in a recognizable format like "3 June" or "3June".'
            else:
                response = 'Invalid format. Use "update task task, new_start_date, new_end_date, new_priority"'
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)

        elif command == 'mark task':
            task_match = re.search(r'\bmark\b.*\b(task\b.*?\bcompleted|task\b.*?\buncompleted)\b', user_message)
            if task_match:
                task_status = task_match.group(1)
                task_status_parts = task_status.split()
                task_name = task_status_parts[1].strip()
                status = "Completed" if "completed" in task_status else "Not Completed"
                result = sdh.update_entry(task_name, new_status=status)
                if 'error' in result:
                    response = f"Error marking task: {result['error']}"
                else:
                    response = f"Task marked as {status} in Google Sheet."
            else:
                response = 'Invalid format. Use "mark task [task name] completed" or "mark task [task name] uncompleted"'
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)

        elif command == 'delete task':
            task = user_message.replace('delete task ', '').strip()
            result = sdh.delete_entry(task)
            if 'error' in result:
                response = f"Error deleting task: {result['error']}"
            else:
                response = 'Task deleted from Google Sheet.'
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)

        else:
            response = 'Invalid command. Use add task, get tasks, update task, mark task, or delete task.'
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)
        
        if response:
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)

    except Exception as e:
        print(e)
        response = f'An error occurred while processing your request: {e}'
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)


@client.event
async def on_ready() -> None:
    print(f"{client.user} is now running!")

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    # Check if the bot is mentioned
    if client.user.mention in message.content:
        username: str = str(message.author)
        user_message: str = str(message.content).replace(client.user.mention, '').strip()
        channel: str = str(message.channel)

        print(f"{channel} -- {username} -- {user_message}")
        await send_message(message, user_message)

def main() -> None:
    client.run(TOKEN)

if __name__ == "__main__":
    main()
