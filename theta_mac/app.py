
import json
import time
import random
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_scores():
    try:
        with open('scores.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_scores(scores):
    with open('scores.json', 'w') as f:
        json.dump(scores, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    session['score'] = 0
    session['start_time'] = time.time()
    session['duration'] = int(request.form.get('duration', 60))
    session['operations'] = request.form.getlist('operations')
    session['min_range'] = int(request.form.get('min_range', 1))
    session['max_range'] = int(request.form.get('max_range', 10))
    session['mode'] = request.form.get('mode', 'normal')
    session['trader_sub_mode'] = request.form.get('trader_sub_mode', 'tau')
    return render_template('game.html', duration=session['duration'])

@app.route('/new_question', methods=['GET'])
def new_question():
    operations = session.get('operations', ['+', '-'])
    min_range = session.get('min_range', 1)
    max_range = session.get('max_range', 10)
    mode = session.get('mode', 'normal')
    trader_sub_mode = session.get('trader_sub_mode', 'tau')

    if mode == 'trader':
        decimal_places = 2 if trader_sub_mode == 'tau' else 1
        num1 = round(random.uniform(min_range, max_range), decimal_places)
        num2 = round(random.uniform(min_range, max_range), decimal_places)
        operator = random.choice(['+', '-'])
    else:
        num1 = random.randint(min_range, max_range)
        num2 = random.randint(min_range, max_range)
        operator = random.choice(operations)

    if operator == '-' and num1 < num2:
        num1, num2 = num2, num1
    
    if operator == '/':
        # Ensure division results in an integer for normal mode
        if mode == 'normal':
            num1 = num1 * num2

    question = f"What is {num1} {operator} {num2}?"
    session['correct_answer'] = round(eval(f"{num1}{operator}{num2}"), 2)
    
    return jsonify(question=question)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    answer = request.json.get('answer')
    try:
        answer = float(answer)
    except (ValueError, TypeError):
        return jsonify(correct=False, score=session.get('score', 0))

    if answer == session.get('correct_answer'):
        session['score'] += 1
        return jsonify(correct=True, score=session['score'])
    return jsonify(correct=False, score=session['score'])

@app.route('/end_game', methods=['POST'])
def end_game():
    scores = get_scores()
    scores.append({'date': time.strftime("%Y-%m-%d %H:%M:%S"), 'score': session.get('score', 0)})
    save_scores(scores)
    return jsonify(success=True)

@app.route('/scores')
def scores():
    scores = get_scores()
    return render_template('scores.html', scores=scores)

if __name__ == '__main__':
    app.run(debug=True)
