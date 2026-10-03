from googleapiclient.discovery import build
from mitsuki.tools.google_auth import get_google_credentials

class GoogleTasksTool:
    @staticmethod
    def get_pending_tasks(max_results: int = 10) -> str:
        """Fetches pending tasks from the user's default Google Tasks list."""
        try:
            creds = get_google_credentials()
            service = build('tasks', 'v1', credentials=creds)

            # Get the user's default task list
            tasklists = service.tasklists().list(maxResults=1).execute()
            lists = tasklists.get('items', [])
            
            if not lists:
                return "No Google Task lists found."

            task_list_id = lists[0]['id']
            task_list_title = lists[0]['title']

            results = service.tasks().list(
                tasklist=task_list_id,
                showCompleted=False,
                maxResults=max_results
            ).execute()
            
            tasks = results.get('items', [])

            if not tasks:
                return f"No pending tasks found in your '{task_list_title}' list."

            task_items = []
            for task in tasks:
                title = task.get('title', 'Untitled Task')
                due = task.get('due', None)
                due_str = f" (Due: {due[:10]})" if due else ""
                task_items.append(f"- {title}{due_str}")

            return f"Google Tasks ({task_list_title}):\n" + "\n".join(task_items)
            
        except Exception as e:
            return f"Error fetching Google Tasks: {e}"

    @staticmethod
    def create_task(task_title: str) -> str:
        """Adds a new task to the user's default Google Tasks list."""
        try:
            creds = get_google_credentials()
            service = build('tasks', 'v1', credentials=creds)

            # Get the user's default task list
            tasklists = service.tasklists().list(maxResults=1).execute()
            lists = tasklists.get('items', [])
            
            if not lists:
                return "No Google Task lists found."

            task_list_id = lists[0]['id']
            task_list_title = lists[0]['title']

            task_body = {
                'title': task_title
            }

            result = service.tasks().insert(
                tasklist=task_list_id,
                body=task_body
            ).execute()

            return f"Successfully added '{result.get('title')}' to your '{task_list_title}' task list!"
            
        except Exception as e:
            import traceback
            traceback.print_exc()  # This will dump the full red stack trace to your terminal!
            print(f"DEBUG TASK ERROR: {e}") # This prints it right where you ran python
            return f"Error adding Google Task: {e}"