from flask import Flask, request, jsonify
from flask_cors import CORS
from voice_handler import listen, speak
from code_generator import generate_code

app = Flask(__name__)
CORS(app)  # Allows VS Code or frontend to access API

@app.route('/')
def home():
    return jsonify({"message": "Voice Code Assistant Backend is running."})

@app.route('/voice-to-code', methods=['GET'])
def voice_to_code():
    """Handles voice command and generates code."""
    speak("Please say your command.")
    command = listen()

    if command:
        speak("Generating your code, please wait...")
        generated_code = generate_code(command)
        speak("Here is your generated code.")

        print("\n💡 Generated Code:\n", generated_code)
        return jsonify({"command": command, "generated_code": generated_code})
    else:
        speak("Sorry, I could not understand your command.")
        return jsonify({"error": "No command detected."}), 400

@app.route('/edit-code', methods=['POST'])
def edit_code():
    """Handles real-time code editing requests from VS Code."""
    data = request.json
    command = data.get("command")
    code = data.get("code")

    if not command or not code:
        return jsonify({"error": "Missing command or code"}), 400

    # For now, simulate code improvement (you can later enhance this)
    updated_code = f"# Modified based on command: {command}\n{code}"

    return jsonify({"updated_code": updated_code})

if __name__ == '__main__':
    app.run(debug=True)
