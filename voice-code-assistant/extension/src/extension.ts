import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    console.log('🎤 Voice Code Assistant is now active!');

    let disposable = vscode.commands.registerCommand('voiceAssistant.start', async () => {
        vscode.window.showInformationMessage('🎧 Listening for your voice command...');

        try {
            // Call your backend Flask server to handle the voice input
            const response = await axios.get('http://127.0.0.1:5000/voice-to-code');

            const generatedCode = response.data.code || "No code was generated.";
            const activeEditor = vscode.window.activeTextEditor;

            if (activeEditor) {
                const document = activeEditor.document;
                const position = activeEditor.selection.active;

                // Insert generated code at cursor position
                activeEditor.edit(editBuilder => {
                    editBuilder.insert(position, `\n${generatedCode}\n`);
                });

                vscode.window.showInformationMessage('✅ Code inserted successfully!');
            } else {
                vscode.window.showErrorMessage('No active editor found.');
            }
        } catch (error: any) {
            console.error(error);
            vscode.window.showErrorMessage('⚠️ Failed to connect to backend or generate code.');
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
