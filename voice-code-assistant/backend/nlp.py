import re
import os
from cst_helper import insert_at_end, rename_identifier

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
USE_OPENAI = bool(OPENAI_KEY)
if USE_OPENAI:
    import openai
    openai.api_key = OPENAI_KEY

def rule_parse(text: str):
    t = text.lower().strip()
    # rule: for loop "for loop from X to Y" or "from zero to four"
    m_for = re.search(r'for (?:a )?loop.*from (\w+) to (\w+)', t)
    if m_for:
        a = word_to_int(m_for.group(1))
        b = word_to_int(m_for.group(2))
        if a is not None and b is not None:
            snippet = f'for i in range({a}, {b+1}):\n    print(i)'
            return {'intent': 'insert', 'snippet': snippet}
    # allow "create a for loop from 0 to 4" numeric digits
    m_for2 = re.search(r'for (?:a )?loop.*from (\d+) to (\d+)', t)
    if m_for2:
        a = int(m_for2.group(1)); b = int(m_for2.group(2))
        snippet = f'for i in range({a}, {b+1}):\n    print(i)'
        return {'intent': 'insert', 'snippet': snippet}
    # print/print statement
    m_print = re.search(r'(?:add|insert|create).*(print|log|print statement).*(?:that )?(prints|show)? ?(.+)', t)
    if m_print:
        msg = m_print.group(3) or 'debug'
        msg = msg.strip().strip('"').strip("'")
        # if msg looks like a variable name (no spaces), print variable, else string
        if re.match(r'^[A-Za-z_]\w*$', msg):
            snippet = f'print({msg})'
        else:
            snippet = f"print('{msg}')"
        return {'intent':'insert', 'snippet': snippet}
    # rename variable
    m_rename = re.search(r'rename (?:variable|identifier) (\w+) to (\w+)', t)
    if m_rename:
        return {'intent':'refactor_rename', 'oldName': m_rename.group(1), 'newName': m_rename.group(2)}
    # fix syntax
    if 'fix syntax' in t or 'fix syntax error' in t or 'fix syntax errors' in t:
        return {'intent':'fix_syntax'}
    return None

def word_to_int(w: str):
    w = w.lower()
    wordmap = {
        'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10
    }
    if w.isdigit():
        return int(w)
    return wordmap.get(w)

def interpret(text: str, ctx: dict):
    """
    Returns a dict like:
    { "intent": "...", "edits": [ {start:{line,char}, end:{line,char}, newText: "..." } ] }
    or { "intent":"ask_clarification", "message":"..." }
    """
    rule = rule_parse(text)
    if rule:
        if rule['intent'] == 'insert':
            edits = insert_at_end(ctx.get('fileContent',''), rule['snippet'])
            return {'intent':'insert', 'edits': edits}
        if rule['intent'] == 'refactor_rename':
            edits = rename_identifier(ctx.get('fileContent',''), rule['oldName'], rule['newName'])
            if not edits:
                return {'intent':'ask_clarification', 'message': 'Could not find occurrences to rename.'}
            return {'intent':'refactor_rename', 'edits': edits}
        if rule['intent'] == 'fix_syntax':
            # naive: ask LLM to fix if available, else respond that not supported
            if not USE_OPENAI:
                return {'intent':'ask_clarification', 'message':'Fix syntax not available without OPENAI_API_KEY.'}
            # else fallthrough to LLM below
    # fallback to LLM if configured
    if USE_OPENAI:
        prompt = f"""You are a Python code-edit assistant.
Input: a Python file content and a user's instruction.
Output: a JSON with fields:
{{ "intent": "...", "edits":[ {{ "start": {{ "line":0,"character":0 }}, "end":{{ "line":0,"character":0 }}, "newText":"..." }} ] }}
Return only valid JSON. Use zero-based line numbers.

File content:
\"\"\"{ctx.get('fileContent','').replace('\"\"\"', '\\\"\\\"\\\"')}\"\"\"

Instruction:
\"\"\"{text}\"\"\"
"""
        try:
            resp = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=800,
                temperature=0
            )
            out = resp.choices[0].text.strip()
            import json
            parsed = json.loads(out)
            return parsed
        except Exception as e:
            return {'intent':'ask_clarification', 'message': 'LLM error: ' + str(e)}
    # if no rule and no LLM
    return {'intent':'ask_clarification', 'message':'Could not parse the command and no LLM configured.'}
