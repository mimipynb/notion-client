"""" 
Notion connection. 

""""
 
import os 
import json 
import requests 
from fastapi import HTTPException 
from typing import Optional, Literal

from notion_client import CodeBlock, NotionFormatter, CodeText

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_PAGES = {
    "inbox": "13e69bb91d8480e19debc107cf4b698a", 
    "dashboard": "135iu325u23i5sdgasdgasgasgag", 
    "projectManager": "135iu325u23i5sdgasdgasgasgag"
}

HEADERS = {
    "Notion-Version": "2022-02-22",
    "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}"
}

KEY_WIDTH = 14

def display(data, key_width=15):
    return "\n".join([f"{keys.ljust(key_width)} {vals}" if not isinstance(vals, dict) else f"{keys.ljust(key_width)}\n{display(vals)}" for keys, vals in data.items()])

def sanitize_block(**block_info):
    block = {
        'block_id': block_info.get('id', None),
        'page_id': block_info['parent']['page_id'] if block_info.get('parent', None) is not None else None, 
        'created_time': block_info.get('created_time', None),
        'last_edited_time': block_info.get('last_edited_time', None),
        'created_by': block_info['created_by']['id'] if block_info.get('created_by', None) is not None else None, 
        'last_edited_by': block_info['created_by']['id'] if block_info.get('created_by', None) is not None else None, 
        'block_type': block_info.get('type', None), 
    }
    
    if block['block_type']:
        if block['block_type'] == 'child_database':
            block['block_info'] = {
                'title': block_info['child_database']['title'] if block_info.get('child_database', None) is not None else None 
            }
        elif block['block_type'] == 'code':
            if block_info.get('code', None) is not None:
                
                if block_info['code'].get('rich_text', None) and isinstance(block_info['code']['rich_text'], list):
                    
                    block['block_info'] = {
                        'caption': block_info['code'].get('caption', None),
                        'content': block_info['code']['rich_text'][0].get('plain_text', None),
                        'format': block_info['code']['rich_text'][0].get('annotations'), 
                        'language': block_info['code'].get('language', None)
                    }
                # print('>>>>>> Mermaid block')
                # print(display(data=block_info))
        elif block['block_type'] == 'paragraph':
            if block_info.get('paragraph', None): 
                block['block_type'] = block_info['paragraph'].get("rich_text", None) 

        if 'block_type' not in block:
            block['block_info'] = 'NA'
            
    # print('\nNew added section: ----')
    # print(display(block))
    return block

def notion_query(method: str, url: str, headers: Optional[dict]=HEADERS, payload: Optional[dict] = {}):
    """
    Notion API client wrapper.
    """
    try:
        response = requests.request(method=method, url=url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

def stack_blocks(page_url: str):
    output = notion_query(method='GET', url=page_url, headers=HEADERS)
    
    if output['object'] != 'list':
        raise HTTPException(status_code=404, detail=f"Cannot configure list of objects. Returned {output['object']}")
    else:
        for block_item in output['results']:
            yield sanitize_block(**block_item) 
    
class NotionPage:
    def __init__(self, page_id: str):
        if page_id not in NOTION_PAGES:
            raise HTTPException(status_code=404, detail=f"Page ID '{page_id}' not found.")
        
        self.summary = notion_query(method='GET', url=os.path.join(NOTION_API_URL, 'pages', NOTION_PAGES[page_id]))
        self.blocks = list(stack_blocks(page_url=os.path.join(NOTION_API_URL, 'blocks', NOTION_PAGES[page_id], "children?page_size=100")))
        self.session_history = []
        
    def _search_blocks(self, block_type: Literal['code', 'paragraph', 'database']):
        return [i for i in self.blocks if i['block_type'] == block_type]
    
    @property
    def code_block(self):
        return self._search_blocks('code')

    @property 
    def paragraph_block(self):
        return self._search_blocks(block_type='paragraph')

class NotionHandler:
    @staticmethod
    def update_block(block_info, new_content):
        
        block_id = block_info['block_id']
        
        block_input = CodeBlock(text=CodeText(content=new_content), annotations=NotionFormatter(**block_info['block_info']['format']))
        inputs = block_input.model_dump_json(indent=4)
        print(json.loads(inputs))
        
        url = os.path.join(NOTION_API_URL, 'blocks', block_id)
        headers = HEADERS.copy()
        headers.update({'Content-Type': 'application/json'}) 
        result = notion_query('PATCH', url=url, headers=headers, payload=json.loads(inputs))

        print('change status: SUCCESS')
        return result 

if __name__ == "__main__":
    mermaid_sample = """graph TD
    Start --> Task1[Do Something]
    Task1 --> Decision{Is it done?}
    Decision -->|Yes| End
    Decision -->|No| Task1"""

    # 1. Enter the page you wan to view from the template
    page = NotionPage(page_id='inbox')
    
    # 2. Enter the block and update block with new code code
    result = NotionHandler.update_block(page.code_block[0], mermaid_sample)

    # 3. Appends to current Agent Session. TODO: This should be replaced with Logging
    page.session_history.append(result)
    
