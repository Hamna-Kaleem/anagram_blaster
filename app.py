# Create a Flask app for a web game called "Anagram Blaster".

# Requirements:

# 1. Serve `index.html` from the `templates/` folder.
# 2. Serve static files from `static/`.
# 3. Use three text files as word sources, stored in a `words/` folder:
#    - `easy.txt`
#    - `medium.txt`
#    - `hard.txt`
#    Each file contains one word per line.
# 4. The app should load these word lists once at startup.

# Define these routes:

# - `/` → returns the index page.
# - `/get_word?difficulty=easy|medium|hard` → returns a scrambled word and its original answer from the corresponding word list.
# - `/check_answer` → accepts POST with JSON:
#    ```json
#    {
#      "guess": "word_guessed",
#      "answer": "original_word"
#    }
from flask import Flask, render_template, jsonify, request
import random
import os
import requests

app = Flask(__name__)

# Load words from files
def load_words():
    base_path = os.path.join(os.path.dirname(__file__), "words")
    levels = ["easy", "medium", "hard"]
    word_dict = {}
    for level in levels:
        file_path = os.path.join(base_path, f"{level}.txt")
        with open(file_path, "r") as file:
            word_dict[level] = [line.strip() for line in file if line.strip()]
    return word_dict

words = load_words()

# Track difficulty and streaks
current_difficulty = "medium"
correct_streak = 0
wrong_streak = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_word", methods=["GET"])
def get_word():
    global current_difficulty
    word = random.choice(words[current_difficulty])
    scrambled = "".join(random.sample(word, len(word)))
    return jsonify({
        "scrambled_word": scrambled,
        "answer": word,
        "difficulty": current_difficulty
    })

@app.route("/check_answer", methods=["POST"])
def check_answer():
    global correct_streak, wrong_streak, current_difficulty
    data = request.get_json()
    guess = data.get("guess", "").lower()
    answer = data.get("answer", "").lower()

    if not guess or not answer:
        return jsonify({"result": "invalid", "message": "Missing guess or answer."}), 400

    # Validate using dictionary API
    dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{guess}"
    dict_res = requests.get(dict_url)

    if dict_res.status_code != 200:
        # Treat as wrong answer, show correct word, update difficulty
        wrong_streak += 1
        correct_streak = 0
        if wrong_streak >= 2:
            current_difficulty = "easy"
            wrong_streak = 0  # reset after demotion
        return jsonify({
            "result": "invalid",
            "message": f"'{guess}' is not a valid English word. The correct word was '{answer}'.",
            "correct_word": answer,
            "difficulty": current_difficulty
        })

    if guess == answer:
        correct_streak += 1
        wrong_streak = 0
        if correct_streak >= 3:
            current_difficulty = promote_difficulty(current_difficulty)
            correct_streak = 0  # reset after promotion
        return jsonify({
            "result": "correct",
            "message": "Correct!",
            "difficulty": current_difficulty
        })
    else:
        wrong_streak += 1
        correct_streak = 0
        if wrong_streak >= 2:
            current_difficulty = "easy"
            wrong_streak = 0  # reset after demotion
        return jsonify({
            "result": "wrong",
            "message": f"Wrong! The correct word was '{answer}'.",
            "correct_word": answer,
            "difficulty": current_difficulty
        })

@app.route("/update_difficulty", methods=["POST"])
def update_difficulty():
    return jsonify({"current_difficulty": current_difficulty})

def promote_difficulty(current):
    if current == "easy":
        return "medium"
    elif current == "medium":
        return "hard"
    return "hard"  # stay at hard

if __name__ == "__main__":
    app.run(debug=True)
