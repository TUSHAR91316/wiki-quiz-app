import requests
from bs4 import BeautifulSoup
import re
import concurrent.futures

def scrape_url(url: str):
    """Scrapes a single Wikipedia URL and returns its data."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        title_tag = soup.find('h1', class_='firstHeading') or soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else "Unknown Title"
        
        # Get content
        content_div = soup.find('div', id='mw-content-text')
        paragraphs = content_div.find_all('p') if content_div else []
        
        # Extract text from paragraphs
        text_content_list = []
        summary = ""
        
        for i, p in enumerate(paragraphs):
            text = p.get_text().strip()
            if text:
                text_content_list.append(text)
                if not summary and len(text) > 50:
                    summary = text 
        
        full_text = "\n\n".join(text_content_list)
        full_text = re.sub(r'\[\d+\]', '', full_text)
        summary = re.sub(r'\[\d+\]', '', summary)
        
        return {
            "title": title,
            "summary": summary,
            "full_text": full_text
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_wikipedia(urls: list[str]):
    """
    Scrapes multiple Wikipedia articles concurrently.
    Returns a combined dictionary with consolidated text.
    """
    results = []
    # Deduplicate URLs
    unique_urls = list(set(urls))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(scrape_url, url): url for url in unique_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception as e:
                print(f"Error in thread: {e}")
    
    if not results:
        # Instead of raising error immediately, return None so caller handles it
        return None

    # Combine results
    combined_title = " & ".join([r['title'] for r in results])
    combined_summary = "\n\n".join([f"**{r['title']}**: {r['summary']}" for r in results])
    combined_text = "\n\n".join([f"--- ARTICLE: {r['title']} ---\n{r['full_text']}" for r in results])
    
    return {
        "title": combined_title,
        "summary": combined_summary,
        "text": combined_text,
        "original_urls": unique_urls
    }

if __name__ == "__main__":
    # Test the scraper
    data = scrape_wikipedia(["https://en.wikipedia.org/wiki/Alan_Turing"])
    if data:
        print(f"Title: {data['title']}")
        print(f"Summary: {data['summary'][:100]}...")
