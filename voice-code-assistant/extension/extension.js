const vscode = require("vscode");
const axios = require("axios");

function activate(context) {
  console.log("Voice Code Assistant is now active!");

  let disposable = vscode.commands.registerCommand("voiceCodeAssistant.start", async function () {
    vscode.window.showInformationMessage("🎤 Voice Code Assistant is listening...");

    try {
      const response = await axios.get("http://127.0.0.1:5000/voice-to-code");
      const code = response.data.code;

      if (code) {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
          const position = editor.selection.active;
          editor.edit(editBuilder => {
            editBuilder.insert(position, "\n" + code + "\n");
          });
          vscode.window.showInformationMessage("✅ Code inserted successfully!");
        } else {
          vscode.window.showWarningMessage("No active editor found.");
        }
      } else {
        vscode.window.showWarningMessage("No code generated. Try speaking again!");
      }
    } catch (error) {
      vscode.window.showErrorMessage("⚠️ Error connecting to backend: " + error.message);
    }
  });

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
