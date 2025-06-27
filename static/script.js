//  I want you to write the full content of script.js, which should:
// Fetch a scrambled word and its difficulty level from /get_word.
// Display it in a div with id scrambled-word.
// Let the user submit a guess via an input.
// On submit:
// Send the guess and original word to /check_answer.
// Show result feedback in #feedback (correct, wrong, invalid).
// Show updated #score (numeric) and #difficulty.
// If the answer is wrong or invalid, show the correct answer in feedback and 
// Wait for the user to click submit again to load the next word.
// The score increases by 1 for each correct answer and 
// decreases by 1 for each wrong or invalid guess (but never below 0).
// Use `fetch` for all requests. Make code clean and commented.
// Return full content of `static/script.js`.

let currentAnswer = "";
let waitingForNext = false;
let score = 0;

document.addEventListener("DOMContentLoaded", () => {
    fetchWord();

    const inputBox = document.getElementById("user-input");
    const submitButton = document.getElementById("submit-button");

    submitButton.addEventListener("click", () => {
        const userGuess = inputBox.value.trim();

        // If waiting, move to next word
        if (waitingForNext) {
            waitingForNext = false;
            inputBox.value = "";
            fetchWord();
            return;
        }

        if (!userGuess) return;

        fetch("/check_answer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                guess: userGuess,
                answer: currentAnswer
            })
        })
            .then(res => res.json())
            .then(data => {
                document.getElementById("feedback").textContent = data.message;
                document.getElementById("difficulty").textContent = `Difficulty: ${data.difficulty}`;

                if (data.result === "correct") {
                    score += 1;
                    inputBox.value = "";
                    fetchWord(); // get next word immediately
                } else {
                    score = Math.max(0, score - 1); // optional: reduce score
                    waitingForNext = true; // wait for second submit
                    currentAnswer = "";    // clear answer so resubmission doesn't work
                }

                document.getElementById("score").textContent = `Score: ${score}`;
            });
    });
});

function fetchWord() {
    fetch("/get_word")
        .then(res => res.json())
        .then(data => {
            currentAnswer = data.answer;
            document.getElementById("scrambled-word").textContent = data.scrambled_word;
            document.getElementById("difficulty").textContent = `Difficulty: ${data.difficulty}`;
            document.getElementById("feedback").textContent = "";
        });
}
