from flask import Flask, jsonify
from voice_handler import listen, speak
from code_generator import generate_code

app = Flask(__name__)

@app.route("/voice-to-code", methods=["GET"])
def voice_to_code():
    speak("Please say your command.")
    command = listen()
    if not command:
        return jsonify({"error": "Could not understand your command"}), 400

    speak("Generating your code, please wait...")
    code = generate_code(command)
    print("\n💡 Generated Code:\n", code)
    speak("Here is your generated code.")
    return jsonify({"command": command, "code": code})

if __name__ == "__main__":
    app.run(debug=True)
