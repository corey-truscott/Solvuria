import hashlib
import json
import random
import secrets
import sys
import time
from datetime import datetime
from getpass import getpass

import requests

# imports msvcrt for windows, or getch for linux
# and sets the correct enter keycode for each os
enterKeyCode = 13
try:
    from msvcrt import getch
except ImportError:
    from getch import getch

    enterKeyCode = 10

VERSION = 140

UserIdentifier = None
UserAgent = None
AuthToken = None
UserData = None

random.seed(secrets.randbelow(1 << 64))


def GetPasswordInput():
    # Taken and modified from the pwinput python library
    # https://github.com/asweigart/pwinput

    enteredPassword = []
    sys.stdout.write("[>] Enter your password: ")
    sys.stdout.flush()
    while True:
        key = ord(getch())
        if key == enterKeyCode:
            sys.stdout.write("\n")
            return "".join(enteredPassword)
        elif key in (8, 127):
            if len(enteredPassword) > 0:
                sys.stdout.write("\b \b")
                sys.stdout.flush()
                enteredPassword = enteredPassword[:-1]
        elif 0 <= key <= 31:
            pass
        else:
            char = chr(key)
            sys.stdout.write("*")
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
        return [secrets.choice(answers), "Incorrect"]  # Return incorrect answer
    for answer in answers:
        if AnswerCorrect(answer):
            return [answer, "Correct"]  # Return correct answer

    # Answer should have been returned by now; line below is added as a failsafe
    return [secrets.choice(answers), "Incorrect"]


def GenerateContentIdentifier(answer_id: str, question_id: str):
    return hashlib.sha256(
        (question_id + answer_id + UserIdentifier).encode()
    ).hexdigest()


def GetUserAgent():
    return secrets.choice(
        [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; rv:124.0) Gecko/20100101 Firefox/124.0",
        ]
    )


def Authenticate(email: str, password: str):
    try:
        global UserData, AuthToken, UserIdentifier
        Response = requests.post(
            "https://kolin.tassomai.com/api/user/login/",
            headers={
                "accept": "application/json; version=1.18",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "content-type": "application/json",
                "priority": "u=1, i",
                "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "origin": "https://app.tassomai.com/",
                "referer": "https://app.tassomai.com/",
                "User-Agent": UserAgent,
            },
            data=json.dumps(
                {
                    "capabilities": {
                        "cordovaPlatform": None,
                        "image": True,
                        "isMobile": False,
                        "mathjax": True,
                        "wondeReady": True,
                    },
                    "email": email,
                    "password": password,
                }
            ),
        ).json()

        UserData = Response["user"]
        AuthToken = "Bearer " + Response["token"]
        UserIdentifier = str(UserData["id"])

        return True
    except Exception as ex:
        return False


################################################################################################################################################################


def GetQuizzes(SubjectId: str):
    return requests.get(
        "https://kolin.tassomai.com/api/quiz/next/"
        + SubjectId
        + "/?capabilities=%7B%22image%22:true,%22mathjax%22:true,%22isMobile%22:false,%22cordovaPlatform%22:null,%22wondeReady%22:true%7D",
        headers={
            "accept": "application/json; version=1.18",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": AuthToken,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "origin": "https://app.tassomai.com/",
            "referer": "https://app.tassomai.com/",
            "User-Agent": UserAgent,
        },
    ).json()["quizzes"]


def FetchQuizData(courseId: str, playlistId: str):
    return requests.post(
        "https://kolin.tassomai.com/api/quiz/",
        headers={
            "accept": "application/json; version=1.18",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": AuthToken,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "origin": "https://app.tassomai.com/",
            "referer": "https://app.tassomai.com/",
            "User-Agent": UserAgent,
        },
        data=json.dumps(
            {
                "capabilities": {
                    "cordovaPlatform": None,
                    "image": True,
                    "isMobile": False,
                    "mathjax": True,
                    "wondeReady": True,
                },
                "course": courseId,
                "playlist": playlistId,
                "requestTime": int(time.time_ns() / 1000000),
                "was_recommended": True,
            }
        ),
    ).json()


def AnswerQuestion(answerId: str, askingId: str):
    r = requests.post(
        "https://kolin.tassomai.com/api/answer/" + str(asking_id) + "/",
        headers={
            "accept": "application/json; version=1.18",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": AuthToken,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "origin": "https://app.tassomai.com/",
            "referer": "https://app.tassomai.com/",
            "User-Agent": UserAgent,
        },
        data=json.dumps(
            {
                "answer_id": answerId,
                "content_id": GenerateContentIdentifier(answerId, askingId),
                "requestTime": int(time.time_ns() / 1000000),
            }
        ),
    )

    return r.status_code == 200


def GetSubjectList():
    return requests.get(
        "https://kolin.tassomai.com/api/user/extra/",
        headers={
            "accept": "application/json; version=1.18",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": AuthToken,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "origin": "https://app.tassomai.com/",
            "referer": "https://app.tassomai.com/",
            "User-Agent": UserAgent,
        },
    ).json()["extra"]["currentDisciplines"]


def CaptchaBypass(quiz_data: dict):
    if quiz_data["turnstile_mode"] == None:
        return [False, quiz_data]

    return [
        True,
        requests.post(
            "https://kolin.tassomai.com/api/quiz/fetch/" + str(quiz_data["quiz_id"]),
            headers={
                "accept": "application/json; version=1.18",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "authorization": AuthToken,
                "content-type": "application/json",
                "priority": "u=1, i",
                "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "origin": "https://app.tassomai.com/",
                "referer": "https://app.tassomai.com/",
                "User-Agent": UserAgent,
            },
        ).json(),
    ]


def UpdateLastLogin():
    currentTime = datetime.now().isoformat()
    payload = {"lastLogin": currentTime}
    response = requests.post(
        "https://kolin.tassomai.com/api/user/extra/",
        headers={
            "accept": "application/json; version=1.18",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "authorization": AuthToken,
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not(A:Brand";v="24", "Chromium";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "origin": "https://app.tassomai.com/",
            "referer": "https://app.tassomai.com/",
            "User-Agent": UserAgent,
        },
        data=json.dumps(payload),
    )

    if response.status_code == 405:
        return True, currentTime
    else:
        return False, None


################################################################################################################################################################

UserAgent = GetUserAgent()

print("[>] Solvuria - Enhance your learning experience")

latest = requests.get(
    "https://api.github.com/repos/corey-truscott/Solvuria/releases/latest"
).json()
versionName = latest["tag_name"]
if int(versionName.replace(".", "").replace("v", "")) > VERSION:
    print(
        "[+] Newer release of solvuria is available on github: "
        + versionName
        + " > v"
        + ".".join(list(str(VERSION)))
    )

print("[~] https://github.com/corey-truscott/Solvuria \n    " + ("-" * 42 + "\n"))

email = input("[>] Enter your email for signing into tassomai: ")
passw = GetPasswordInput()

if not Authenticate(email, passw):
    print(
        "[-] Failed to sign into tassomai, please rerun the program and check your credentials are valid!"
    )
    time.sleep(5)
    sys.exit()

lastLogin, currentTime = UpdateLastLogin()
if not lastLogin:
    print(f"[!] Failed to update lastLogin")
    time.sleep(5)
    sys.exit()

print(f"[+] Updated lastLogin: {currentTime}")

print('[@] Logged in as "' + UserData["firstName"] + " " + UserData["lastName"] + '"\n')
subjectId = ""

subjectList = GetSubjectList()
if len(subjectList) == 1:
    subjectId = subjectList[0]["id"]
    print(
        "[>] Selected "
        + subjectList[0]["name"].lower()
        + " as it is the only available subject!"
    )
else:
    i = 0
    for subject in subjectList:
        i += 1
        print("[" + str(i) + "] Found subject with name: " + subject["name"])
    choice = (
        int(
            input(
                "[>] Enter the number next to the subject which you would like to do: "
            )
        )
        - 1
    )
    subjectId = subjectList[choice]["id"]
    print("[>] Selected " + subjectList[choice]["name"].lower() + "!")

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
            maxDelayBetweenQuizzes = j["maximum_delay_between_quizzes"] / 3
            minDelayBetweenQuizzes = j["minimum_delay_between_quizzes"] / 3
            percentageCorrect = j["percentage_to_answer_correctly"]
            stopAfterTime = j["stop_after_time"] * 60
            print("\n[+] Loaded settings from preset.json file")
            getpass("[>] Press enter to start: ")
        else:
            raise Exception("NoPreset")
except:
    maxDelayBetweenQuestions = float(
        input("\n[>] Maximum delay between questions (seconds): ")
    )
    minDelayBetweenQuestions = float(
        input("[>] Minimum delay between questions (seconds): ")
    )
    maxDelayBetweenQuizzes = (
        float(input("[>] Maximum delay between quizzes (seconds): ")) / 3
    )  # These are divided by 3 because they are split into multiple different sleeps
    minDelayBetweenQuizzes = (
        float(input("[>] Minimum delay between quizzes (seconds): ")) / 3
    )  # The sleeps happen between fetching the quiz and answering the first question
    percentageCorrect = int(input("[>] Percentage of questions to answer correctly: "))
    stopAfterTime = int(input("[>] Stop after N minutes (0 for infinite): ")) * 60


if percentageCorrect > 100 or percentageCorrect < 0:
    percentageCorrect = 80 + secrets.randbelow(6)
if stopAfterTime:
    stopAfterTime += secrets.randbelow(20)

firstTimeMeasure = time.time()

while True:
    quizzes = GetQuizzes(subjectId)
    quiz = False
    for q in quizzes:
        if q["type"] == "normal":
            quiz = q
    if quiz == False:
        print("[-] Could not find any quizzes to complete!")
        print(
            "[-] If you have a class task active, you must complete it manually before using this tool"
        )
        time.sleep(60)
        sys.exit()

    time.sleep(random.uniform(minDelayBetweenQuizzes, maxDelayBetweenQuizzes))
    courseId, playlistId = quiz["courseId"], quiz["playlistId"]
    q = time.time()
    print(
        '\n[>] Completing quiz on "'
        + quiz["playlistName"]
        + '" ('
        + str(courseId)
        + "-"
        + str(playlistId)
        + ")"
    )
    quizData = FetchQuizData(courseId, playlistId)
    time.sleep(random.uniform(minDelayBetweenQuizzes, maxDelayBetweenQuizzes))
    quizData = CaptchaBypass(quizData)
    if quizData[0]:
        print(
            "[+] Successfully bypassed captcha for quiz " + str(quizData[1]["quiz_id"])
        )
    questions = quizData[1]["questions"]
    time.sleep(random.uniform(minDelayBetweenQuizzes, maxDelayBetweenQuizzes))
    print("[>] Solving questions...\n")

    for question in questions:
        asking_id = question["asking_id"]
        answer_ids = [ans["id"] for ans in question["answers"]]
        answer = GetAnswer(answer_ids, percentageCorrect)
        time.sleep(random.uniform(minDelayBetweenQuestions, maxDelayBetweenQuestions))

        if AnswerQuestion(answer[0], str(asking_id)):
            print(
                "[+] Answered question "
                + answer[1].lower()
                + 'ly, selected answer is "'
                + answer[0]
                + '"'
            )
        else:
            print("[-] Failed to answer question, sleeping 20 seconds!")
            time.sleep(20)

    if stopAfterTime:
        if time.time() - firstTimeMeasure > stopAfterTime:
            print(
                "[!] The program will now close as "
                + str(int(stopAfterTime / 60))
                + " minute(s) have passed!"
            )
            break
    print("[+] Completed quiz in " + str(int(time.time() - q)) + " seconds!")

time.sleep(60)
sys.exit()
