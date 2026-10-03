from datetime import datetime, timezone, timedelta
from typing import Optional
from googleapiclient.discovery import build
from mitsuki.tools.google_auth import get_google_credentials

class GoogleCalendarTool:
    @staticmethod
    def get_upcoming_events(max_results: int = 5) -> str:
        """Fetches upcoming events from the user's primary Google Calendar."""
        try:
            creds = get_google_credentials()
            service = build('calendar', 'v3', credentials=creds)

            now = datetime.now(timezone.utc).isoformat()
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])

            if not events:
                return "No upcoming events found on your calendar."

            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'Untitled Event')
                event_list.append(f"- {summary} at {start}")

            return "Upcoming Calendar Events:\n" + "\n".join(event_list)
            
        except Exception as e:
            return f"Error fetching Google Calendar: {e}"

    @staticmethod
    def create_event(summary: str, start_time: str, end_time: Optional[str] = None, description: Optional[str] = None) -> str:
        """Creates an event on the user's primary Google Calendar."""
        try:
            creds = get_google_credentials()
            service = build('calendar', 'v3', credentials=creds)

            # Ensure proper ISO format with timezone if missing
            if 'T' not in start_time:
                start_time = f"{datetime.now().strftime('%Y-%m-%d')}T10:00:00"
            
            if len(start_time) == 19:
                start_time += "+02:00"

            if not end_time:
                try:
                    dt = datetime.fromisoformat(start_time)
                    end_dt = dt + timedelta(hours=1) # Default to 1 hour duration
                    end_time = end_dt.isoformat()
                except Exception:
                    end_time = start_time
            elif len(end_time) == 19:
                end_time += "+02:00"

            event = {
                'summary': summary.strip(),
                'description': description if description else '',
                'start': {'dateTime': start_time},
                'end': {'dateTime': end_time},
            }

            created_event = service.events().insert(calendarId='primary', body=event).execute()
            return f"Successfully scheduled event: {created_event.get('summary')} for {start_time}"
        except Exception as e:
            return f"Error adding Google Calendar event: {e}"