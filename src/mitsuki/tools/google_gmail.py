from googleapiclient.discovery import build
from mitsuki.tools.google_auth import get_google_credentials

class GoogleGmailTool:
    @staticmethod
    def get_recent_emails(max_results: int = 5) -> str:
        """Fetches recent emails from the user's Gmail inbox."""
        try:
            creds = get_google_credentials()
            service = build('gmail', 'v1', credentials=creds)

            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
            messages = results.get('messages', [])

            if not messages:
                return "No recent emails found in your inbox."

            email_list = []
            for msg_info in messages:
                msg = service.users().messages().get(
                    userId='me', 
                    id=msg_info['id'], 
                    format='metadata', 
                    metadataHeaders=['Subject', 'From']
                ).execute()
                headers = msg.get('payload', {}).get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                email_list.append(f"- From: {sender} | Subject: {subject}")

            return "Recent Gmail Inbox Messages:\n" + "\n".join(email_list)
            
        except Exception as e:
            return f"Error fetching Gmail: {e}"