from getpass import getpass
from msvcrt import getch
import hashlib
import requests
import secrets
import random
import json
import time
import sys
import os

UserIdentifier = None
UserAgent = None
AuthToken = None
UserData = None

random.seed(secrets.randbelow(1<<64))

def GetPasswordInput():
    # Taken and modified from the pwinput python library
    # https://github.com/asweigart/pwinput

    enteredPassword = []  
    sys.stdout.write('[>] Enter your password: ')
    sys.stdout.flush()
    while True:
        key = ord(getch())
        if key == 13:
            sys.stdout.write('\n')
            return ''.join(enteredPassword)
        elif key in (8, 127):
            if len(enteredPassword) > 0:
                sys.stdout.write('\b \b')
                sys.stdout.flush()
                enteredPassword = enteredPassword[:-1]
        elif 0 <= key <= 31:
            pass
        else:
            char = chr(key)
            sys.stdout.write('*')
            sys.stdout.flush()
            enteredPassword.append(char)

def GetAnswer(answers: list[str], percentageCorrect: int):
    def AnswerCorrect(answer: str):
        return not int(str(int(answer, 16) * 8779302863457884 % 9007199254740991)[-1])
    
    if secrets.randbelow(100) >= percentageCorrect:
        for answer in answers:
            if AnswerCorrect(answer):
                answers.remove(answer)
                break
        return [secrets.choice(answers), "Incorrect"] # Return incorrect answer
    for answer in answers:
        if AnswerCorrect(answer):
            return [answer, "Correct"] # Return correct answer
    
    # Answer should have been returned by now; line below is added as a failsafe
    return [secrets.choice(answers), "Incorrect"]

def GenerateContentIdentifier(answer_id: str, question_id: str):
    return hashlib.sha256((question_id + answer_id + UserIdentifier).encode()).hexdigest()

def GetUserAgent():
    return secrets.choice(
        [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.",
        ])

def Authenticate(email: str, password: str):
    try:
        global UserAgent, UserIdentifier
        Response = requests.post("https://kolin.tassomai.com/api/user/login/", headers={
            "accept": "application/json; version=1.18",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"24\", \"Chromium\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "origin": "https://app.tassomai.com/",
            "referer": "https://app.tassomai.com/",
            "User-Agent": UserAgent
        }, data=json.dumps({
            "capabilities": {
                "cordovaPlatform": None,
                "image": True,
                "isMobile": False,
                "mathjax": True,
                "wondeReady": True
            },
            "email": email,
            "password": password
        })).json()
        

        global UserData, AuthToken
        UserData = Response["user"]
        AuthToken = "Bearer " + Response["token"]
        UserIdentifier = str(UserData["id"])

        return True
    except Exception as ex:
        print(ex)
        return False
    
################################################################################################################################################################

def GetQuizzes():
    global UserAgent, AuthToken

    return requests.get("https://kolin.tassomai.com/api/quiz/next/1/?capabilities=%7B%22image%22:true,%22mathjax%22:true,%22isMobile%22:false,%22cordovaPlatform%22:null,%22wondeReady%22:true%7D", headers={
        "accept": "application/json; version=1.18",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authorization": AuthToken,
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"24\", \"Chromium\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "origin": "https://app.tassomai.com/",
        "referer": "https://app.tassomai.com/",
        "User-Agent": UserAgent
    }).json()["quizzes"]

def FetchQuizQuestions(courseId: str, playlistId: str):
    global UserAgent, AuthToken

    return requests.post("https://kolin.tassomai.com/api/quiz/", headers={
        "accept": "application/json; version=1.18",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authorization": AuthToken,
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"24\", \"Chromium\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "origin": "https://app.tassomai.com/",
        "referer": "https://app.tassomai.com/",
        "User-Agent": UserAgent
    }, data=json.dumps({
        "capabilities": {
            "cordovaPlatform": None,
            "image": True,
            "isMobile": False,
            "mathjax": True,
            "wondeReady": True
        },
        "course": courseId,
        "playlist": playlistId,
        "requestTime": str(int(time.time_ns() / 1000000)),
        "was_recommended": True
    })).json()["questions"]

def AnswerQuestion(answerId: str, askingId: str):
    r = requests.post("https://kolin.tassomai.com/api/answer/" + str(asking_id) + "/", headers={
        "accept": "application/json; version=1.18",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authorization": AuthToken,
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"24\", \"Chromium\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "origin": "https://app.tassomai.com/",
        "referer": "https://app.tassomai.com/",
        "User-Agent": UserAgent
    }, data=json.dumps({
        "answer_id": answerId,
        "content_id": GenerateContentIdentifier(answerId, askingId),
        "requestTime": int(time.time_ns() / 1000000)
    }))

    return r.status_code == 200

################################################################################################################################################################

UserAgent = GetUserAgent()

print("[>] Solvuria - Automated answer solver for tassomai")
print("[~] https://github.com/bp-resist/Solvuria  \n" + ("-"*51+"\n"))

email = input("[>] Enter your email for signing into tassomai: ")
passw = GetPasswordInput()

if not Authenticate(email, passw):
    print("[-] Failed to sign into tassomai, please rerun the program and check your credentials are valid!")
    time.sleep(5)
    sys.exit()

print("[@] Logged in as \"" +  UserData["firstName"] + " " + UserData["lastName"] + "\"\n")

maxDelayBetweenQuestions = None
minDelayBetweenQuestions = None
maxDelayBetweenQuizzes = None
minDelayBetweenQuizzes = None
percentageCorrect = None
stopAfterTime = None

try:
    with open("preset.json", "r") as f:
        j = json.load(f)

        if j["should_use_preset"]:
            maxDelayBetweenQuestions = j["maximum_delay_between_questions"]
            minDelayBetweenQuestions = j["minimum_delay_between_questions"]
            maxDelayBetweenQuizzes = j["maximum_delay_between_quizzes"] / 2
            minDelayBetweenQuizzes = j["minimum_delay_between_quizzes"] / 2
            percentageCorrect = j["percentage_to_answer_correctly"]
            stopAfterTime = j["stop_after_time"] * 60
            print("[+] Loaded settings from preset.json file")
            getpass("[>] Press enter to start: ")
        else:
            raise Exception("NoPreset")
except:
    maxDelayBetweenQuestions = float(input("[>] Maximum delay between questions (seconds): "))
    minDelayBetweenQuestions = float(input("[>] Minimum delay between questions (seconds): "))
    maxDelayBetweenQuizzes = float(input("[>] Maximum delay between quizzes (seconds): ")) / 2 # These are divided by 2 because they are split between the time before fetching
    minDelayBetweenQuizzes = float(input("[>] Minimum delay between quizzes (seconds): ")) / 2 # the quiz and the time before answering the first question
    percentageCorrect = int(input("[>] Percentage of questions to answer correctly: "))
    stopAfterTime = int(input("[>] Stop after N minutes (0 for infinite): ")) * 60


if percentageCorrect > 100 or percentageCorrect < 0:
    percentageCorrect = 80 + secrets.randbelow(6)
if stopAfterTime != 60:
    stopAfterTime += secrets.randbelow(20)

firstTimeMeasure = time.time()

while True:
    quiz = GetQuizzes()[0]
    time.sleep(random.uniform(minDelayBetweenQuizzes, maxDelayBetweenQuizzes))
    courseId, playlistId = quiz["courseId"], quiz["playlistId"]
    q = time.time()
    print("\n[>] Completing quiz on \"" + quiz["playlistName"] + "\" (" + str(courseId) + "-" + str(playlistId) + ")")
    questions = FetchQuizQuestions(courseId, playlistId)
    time.sleep(random.uniform(minDelayBetweenQuizzes, maxDelayBetweenQuizzes))
    print("[>] Solving questions...\n")

    for question in questions:
        asking_id = question["asking_id"]
        answer_ids = [ans["id"] for ans in question["answers"]]
        answer = GetAnswer(answer_ids, percentageCorrect)
        time.sleep(random.uniform(minDelayBetweenQuestions, maxDelayBetweenQuestions))

        if AnswerQuestion(answer[0], str(asking_id)):
            print("[+] Answered question " + answer[1].lower() + "ly, selected answer is \"" + answer[0] + "\"")
        else:
            print("[-] Failed to answer question, sleeping 20 seconds!")
            time.sleep(20)

    if stopAfterTime != 0:
        if time.time() - firstTimeMeasure > stopAfterTime:
            print("[!] The program will now close as " + str(int(stopAfterTime / 60)) + " minute(s) have passed!")
            break
    print("[+] Completed quiz in " + str(int(time.time() - q)) + " seconds!")

time.sleep(60)
sys.exit()
