# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4",
#     "google-api-python-client",
#     "google-auth-httplib2",
#     "google-auth-oauthlib",
#     "lxml",
#     "openai",
#     "openpyxl",
#     "pandas",
#     "tenacity",
# ]
# ///
import os.path
import base64
from tenacity import retry, stop_after_attempt, wait_exponential
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from email.message import EmailMessage
from email.parser import BytesParser
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from llm_classify_article import classify_article_relevance

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_email_service():
    """Authenticate and return Gmail service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_article(html_body):
    """Get article titles, URLs, authors and abstracts from email HTML"""
    soup = BeautifulSoup(html_body, 'html.parser')
    articles = []
    
    # Find all title elements
    title_links = soup.find_all('a', class_='gse_alrt_title')
    
    for title_link in title_links:
        try:
            # Extract title and URL first
            article_url = title_link['href']
            if 'scholar.google.com' in article_url:
                parsed = urlparse(article_url)
                article_url = parse_qs(parsed.query).get('url', [article_url])[0]

            # AUTHOR EXTRACTION
            # Navigate up to containing div then find next sibling div with author info
            article_header = title_link.find_parent(['h3', 'div'])
            author_div = article_header.find_next_sibling('div')
            
            authors = ""
            if author_div and not author_div.find('a'):  # Skip if contains links
                authors = author_div.get_text(strip=True)
                # Clean up common prefixes
                authors = authors.replace("‐ ", "").replace("…", "").strip()

            # NEW ABSTRACT EXTRACTION
            abstract_div = author_div.find_next('div', class_='gse_alrt_sni')
            abstract = abstract_div.get_text(strip=True).replace('<br>', '\n') if abstract_div else ""

            articles.append({
                'title': title_link.get_text(strip=True).replace("\n", " "),
                'url': article_url.replace('https://', ''),
                'authors': authors,
                'abstract': abstract
            })
            
        except Exception as e:
            print(f"Error processing article: {e}")
            
    return articles

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def read_unread_emails(max_results=400):
    """Read unread emails with safe batch processing"""
    service = get_email_service()
    all_articles = []
    
    try:
        page_token = None
        processed_count = 0
        batch_size = 50
        
        while processed_count < max_results:
            # Get messages batch
            results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                q="is:unread from:scholaralerts-noreply@google.com",
                maxResults=batch_size,
                pageToken=page_token
            ).execute()
            
            messages = results.get('messages', [])
            if not messages:
                break

            # Process current batch
            current_batch = []
            for msg in messages[:max_results - processed_count]:
                try:
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='raw'
                    ).execute()
                    
                    raw_email = base64.urlsafe_b64decode(message['raw'])
                    parsed_email = BytesParser().parsebytes(raw_email)
                    
                    headers = {
                        'From': parsed_email.get('From'),
                        'Subject': parsed_email.get('Subject'),
                        'Date': parsed_email.get('Date')
                    }
                    
                    html_body = ""
                    for part in parsed_email.walk():
                        if part.get_content_type() == 'text/html':
                            html_body = part.get_payload(decode=True).decode()
                            break
                            
                    if html_body:
                        articles = get_article(html_body)
                        for article in articles:
                            current_batch.append({
                                'email_date': headers['Date'],
                                'email_subject': headers['Subject'],
                                'article_url': article['url'],
                                'article_title': article['title'],
                                'article_author': article['authors'],
                                'article_abstract': article['abstract'],
                                'relevance': classify_article_relevance(article['title'], article['abstract'])
                            })
                            
                except Exception as e:
                    print(f"Error processing message {msg.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Add batch to total and save
            if current_batch:
                all_articles.extend(current_batch)
                save_progress(current_batch)
                
            processed_count += len(messages)
            page_token = results.get('nextPageToken')
            if not page_token:
                break
                
        # Final save
        if all_articles:
            save_progress(all_articles, final=True)
            
    except Exception as e:
        print(f"Critical error: {str(e)}")
        if all_articles:
            print("Saving collected articles before exiting...")
            save_progress(all_articles, final=True)
        raise

def save_progress(articles, final=False):
    """Save articles to timestamped file"""
    if not articles:
        return
        
    df = pd.DataFrame(articles)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "final" if final else "partial"
    filename = f"{prefix}_{timestamp}.xlsx"
    
    existing_columns = [c for c in df.columns if c in ['email_date', 'email_subject', 'article_url',
                     'article_title', 'article_author', 'article_abstract', 'relevance']]
    df = df[existing_columns]
    
    df.to_excel(filename, index=False)
    print(f"Saved {len(df)} articles to {filename}")

if __name__ == '__main__':
    read_unread_emails(max_results=400)
