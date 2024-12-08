# Notion Connection

This script facilitates interaction with the Notion API, enabling users to dynamically update page sections during a user / Agent session. 
Currently only supports `code` and `paragraph` blocks. 

## Prerequisites
Set up the `NOTION_TOKEN` environment variable with Notion API token. 

**Global Constants**

- **`NOTION_API_URL`**: The base URL for Notion API requests.
- **`NOTION_PAGES`**: A dictionary mapping logical page names to their Notion page IDs.
- **`HEADERS`**: Default headers for Notion API requests, including the authorization token.
  
## How to use:
```python

# Dict storing page's id (value) with corresponding nickname (key) that is accessible by my Agent.
NOTION_PAGES = {
    "inbox": "13e69bb91d8480e19debc107cf4b698a", 
    "dashboard": "hello", 
    "programmer": "hello",
    "projectManager": "hello"
}

# Example code to update a page
mermaid_sample = """graph TD
    Start --> Task1[Do Something]
    Task1 --> Decision{Is it done?}
    Decision -->|Yes| End
    Decision -->|No| Task1"""

# 1. Enter the page you want to view from the template
page = NotionPage(page_id='inbox')

# 2. Enter the block and update block with new code
result = NotionHandler.update_block(page.code_block[0], mermaid_sample)

# 3. Appends to current Agent Session. TODO: This should be replaced with Logging
page.session_history.append(result)
```
---
## Purpose 
- A component for serving my Agent’s action space through a FastAPI interface

## Extension / TODO:

- Add logging
- Integrate with FastAPI serving my Agent’s action space.
  
