from flask import Flask, render_template, request, session
from random import randint
from collections import Counter
import os
import time

app = Flask(__name__)  # "dunder name".
app.secret_key = os.urandom(32)

dictdata = []
with open("/usr/share/dict/words") as lf:
    for line in lf.readlines():
        dictdata.append(line.lower().strip("\n"))

print("init data")


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/play")
def play():
    random_word = genRandomWord()
    session["tips_word"] = random_word
    print(random_word)
    tick_start = time.time()
    session["tick_start"] = tick_start
    return render_template(
        "form.html", the_title="This is a word game", tips_word=random_word
    )


@app.route("/process", methods=["POST"])
def process():
    print(session["tips_word"])

    take_time = takeTime()
    session["take_time"] = take_time

    tips_word = session["tips_word"]

    tips_letters_freqs = Counter(tips_word)

    user_words = request.form["user_input_words"]
    user_words_array = user_words.split()

    invalid_letters = checkInvalidLetters(user_words_array, tips_letters_freqs)

    array_length_errors = checkLengthOfArray(user_words_array)

    word_length_errors = checkLengthOfWord(user_words_array)

    misspelt_errors = checkMissPeltOfWord(user_words_array)

    errors = []

    if len(array_length_errors) > 0:
        errors.append(array_length_errors)

    if len(invalid_letters) > 0:
        errors.append(
            "You used these invalid letters : {invalidLetters}".format(
                invalidLetters=" ".join(invalid_letters)
            )
        )

    if len(word_length_errors) > 0:
        errors.append(
            "These words are too small: {wordLengthError}".format(
                wordLengthError=" ".join(word_length_errors)
            )
        )

    if len(misspelt_errors) > 0:
        errors.append(
            "You misspelt these words: {misspelts}".format(
                misspelts=" ".join(misspelt_errors)
            )
        )

    print("There are errors here:", errors)

    if len(errors) > 0:
        return render_template("errors.html", error_tips=errors)

    return render_template("success.html", user_words=user_words, takeTime=take_time)


@app.route("/record", methods=["POST"])
def record():
    username = request.form["username"]
    takeTime = session["take_time"]
    tips_word = session["tips_word"]

    print("take tim:", takeTime)
    time_records = {}
    word_records = {}

    entry = "{time}\t{name}\t{sourceword}".format(
        time=takeTime, name=username, sourceword=tips_word
    )
    with open("records.log", "a") as rec:
        print(entry, file=rec)

    with open("records.log") as lf:
        for recordData in lf.readlines():
            print(recordData)
            row = recordData.split("\t")
            if row[1] in time_records:
                if row[0] < time_records[row[1]]:
                    time_records[row[1]] = (int)(row[0])
                    word_records[row[1]] = row[2].strip("\n")
            else:
                time_records[row[1]] = row[0]
                word_records[row[1]] = row[2].strip("\n")
    print(time_records)
    print(word_records)

    total = len(time_records)

    list = sorted(time_records.items(), key=lambda d: float(d[1]))

    ranke = -1
    for i in range(0, len(list)):
        if username in list[i][0]:
            ranke = i
            break
    if ranke != -1:
        ranke += 1

    if len(list) >= 10:
        list = list[0:10]
    print("------")
    print(list)
    results = []

    for item in list:
        row = (item[1], item[0], word_records[item[0]])
        results.append(row)
    print(results)
    return render_template("toplist.html", toplist=results, count=total, ranke=ranke)


def takeTime():
    tick_end = time.time()

    tick_start = session["tick_start"]

    take_time = ((int)((tick_end - tick_start) * 100)) / 100

    print("tickend:", tick_end)
    print("tickstart:", tick_start)
    print("tak time:", take_time)

    return take_time


def genRandomWord():
    tips_word = ""
    while len(tips_word) < 7:
        tips_word = dictdata[randint(0, 99000)]
    print(tips_word)
    return tips_word.replace("'", "")


def checkInvalidLetters(user_words_array, tips_letters_freqs):
    invalid_letters = []
    for user_words_array_item in user_words_array:
        c = Counter(user_words_array_item)
        ch_array = list(user_words_array_item)
        for ch in ch_array:
            if c[ch] > tips_letters_freqs[ch]:
                if ch not in invalid_letters:
                    invalid_letters.append(ch)
    return invalid_letters


def checkLengthOfArray(user_words_array):
    error = ""
    if len(user_words_array) < 7:
        error = "You have an incorrect number of words: {count}, not 7.".format(
            count=len(user_words_array)
        )
    return error


def checkLengthOfWord(user_words_array):
    word_length_errors = []
    for word in user_words_array:
        if len(word) < 3:
            word_length_errors.append(word)
    return word_length_errors


def checkMissPeltOfWord(user_words_array):
    misspelt_errors = []
    # temps = []
    # founds = []
    for user_word in user_words_array:
        # temps.append(user_word)
        if user_word in dictdata:
            # founds.append(user_word)
            continue
        else:
            misspelt_errors.append(user_word)
    return misspelt_errors


app.run(debug=True)
