import libcst as cst
import libcst.matchers as m
from libcst import CSTTransformer, Name, Attribute

def make_replace_whole_file_edit(old_content: str, new_content: str):
    # returns an edit object matching the extension's expected format
    old_lines = old_content.splitlines()
    return {
        'start': {'line': 0, 'character': 0},
        'end': {'line': len(old_lines), 'character': 0},
        'newText': new_content
    }

def insert_at_end(file_content: str, snippet: str):
    # append snippet to file content with a newline
    if not file_content.endswith('\n'):
        new_content = file_content + '\n' + snippet + '\n'
    else:
        new_content = file_content + snippet + '\n'
    return [make_replace_whole_file_edit(file_content, new_content)]

class RenameTransformer(cst.CSTTransformer):
    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name

    def leave_Name(self, original_node: Name, updated_node: Name) -> Name:
        if original_node.value == self.old_name:
            return Name(self.new_name)
        return updated_node

    def leave_Attribute(self, original_node: Attribute, updated_node: Attribute) -> Attribute:
        # rename simple attribute like obj.old_name -> obj.new_name
        attr = original_node.attr
        if isinstance(attr, Name) and attr.value == self.old_name:
            return updated_node.with_changes(attr=Name(self.new_name))
        return updated_node

def rename_identifier(file_content: str, old_name: str, new_name: str):
    try:
        module = cst.parse_module(file_content)
        transformer = RenameTransformer(old_name, new_name)
        modified = module.visit(transformer)
        new_code = modified.code
        return [make_replace_whole_file_edit(file_content, new_code)]
    except Exception as e:
        # if rewrite fails, return empty edits
        return []

