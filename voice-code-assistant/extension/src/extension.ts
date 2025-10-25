import * as vscode from 'vscode';
import * as path from 'path';
import fetch from 'node-fetch';
import * as fs from 'fs';

export function activate(context: vscode.ExtensionContext) {
  let disposable = vscode.commands.registerCommand('voiceAssist.start', async () => {
    const panel = vscode.window.createWebviewPanel(
      'voiceAssist',
      'Voice Code Assistant',
      vscode.ViewColumn.Beside,
      { enableScripts: true }
    );

    const htmlPath = path.join(context.extensionPath, 'src', 'webview.html');
    let html = fs.readFileSync(htmlPath, 'utf8');
    panel.webview.html = html;

    panel.webview.onDidReceiveMessage(async message => {
      if (message.type === 'interpret') {
        const editor = vscode.window.activeTextEditor;
        if (!editor) { vscode.window.showErrorMessage('Open a Python file to edit.'); return; }

        try {
          const resp = await fetch('http://localhost:3000/interpret', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: message.text,
              filePath: editor.document.uri.fsPath,
              fileContent: editor.document.getText(),
              language: 'python'
            })
          });
          const data = await resp.json();
          if (data.intent === 'ask_clarification') {
            vscode.window.showInformationMessage('Assistant: ' + data.message);
            return;
          }
          if (data.edits && data.edits.length) {
            // present a short preview (first edit only small snippet)
            const preview = data.edits.map((e:any, idx:number) => {
              const snippet = (e.newText || '').slice(0, 200).replace(/\n/g,'⏎');
              return `Edit ${idx+1}: replace [${e.start.line},${e.start.character}] -> snippet: ${snippet}`;
            }).join('\n');
            const apply = await vscode.window.showInformationMessage(
              'Assistant generated edits:\n' + preview + '\nApply?', 'Yes', 'No'
            );
            if (apply === 'Yes') {
              const workspaceEdit = new vscode.WorkspaceEdit();
              const uri = editor.document.uri;
              for (const e of data.edits) {
                const start = new vscode.Position(e.start.line, e.start.character);
                const end = new vscode.Position(e.end.line, e.end.character);
                const range = new vscode.Range(start, end);
                workspaceEdit.replace(uri, range, e.newText);
              }
              await vscode.workspace.applyEdit(workspaceEdit);
              vscode.window.showInformationMessage('Edits applied. Undo with Ctrl+Z');
            }
          } else {
            vscode.window.showInformationMessage('No edits returned.');
          }
        } catch (err:any) {
          vscode.window.showErrorMessage('Error contacting backend: ' + (err.message || err));
        }
      }
    });
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
