from flask import Flask, render_template, request, jsonify
import json

# Initialize the Flask app
app = Flask(__name__)

# Load the Thirukkural data from a JSON file
file_path = r"C:\Users\Lavanya\Downloads\thirukural_git.json"  # Adjust the path accordingly
with open(file_path, 'r', encoding='utf-8') as file:
    kural_data = json.load(file)  # Assuming this structure matches your data setup

# Assuming dispatcher and other necessary functions are defined elsewhere and imported
from dispatch import dispatcher  # Import your dispatcher function

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle chatbot responses
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input', '')
    response = dispatcher(user_input, kural_data)  # Use the dispatcher to determine the response method
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)



