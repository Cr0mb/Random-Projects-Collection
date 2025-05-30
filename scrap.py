# This script fetches the webpage at the given URL, parses its HTML to extract all chapters marked by `<h3>` or `<h4>` tags, then collects the visible text content between those chapter headers by traversing sibling elements until the next chapter heading, returning a dictionary of chapter titles mapped to their text content.


import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

def tag_visible(element):
    """Filter function to exclude non-visible elements like script, style, and comments."""
    if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def get_full_visible_text_from_url(url):
    """Retrieve and clean the full visible text from the webpage."""
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a successful response

    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove unwanted tags like <script> or <style>
    for tag in soup(['script', 'style']):
        tag.decompose()

    # Look for elements that represent chapters and their content
    # For example, assuming chapter titles are in <h3> or <h4>, and content in <p> or <div>
    chapters = soup.find_all(['h3', 'h4'])  # Find all chapter titles
    
    chapter_contents = {}
    for chapter in chapters:
        # Find the next sibling element or nested elements that contain the content of this chapter
        content = ""
        next_element = chapter.find_next_sibling()
        
        while next_element and next_element.name not in ['h3', 'h4']:  # Check if next element is a chapter title
            if next_element.string:  # If the element has text
                content += next_element.get_text() + "\n"
            next_element = next_element.find_next_sibling()
        
        chapter_contents[chapter.get_text()] = content.strip()

    return chapter_contents

# URL of the full-text page
url = 'https://quod.lib.umich.edu/e/eebo/A30615.0001.001?rgn=main;view=fulltext'

# Get the full visible text
full_chapter_content = get_full_visible_text_from_url(url)

# Print the full chapter content
for chapter_title, content in full_chapter_content.items():
    print(f"Chapter: {chapter_title}\nContent:\n{content}\n")
