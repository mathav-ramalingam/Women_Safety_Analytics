import pyttsx3
import datetime
import speech_recognition as sr
import smtplib
import ssl
import sys
from twilio.rest import Client
from email.message import EmailMessage
import os


def email_sos():
    email_sender = 'jahaganapathi1@gmail.com'
    email_password = 'bkggefxqikzpbmke'  
    email_receiver = 'jahaganapathi861@gmail.com'

    subject = 'SOS ALERT!'
    body = """We have received an SOS alert from you. We are currently reviewing the situation and will get back to you as soon as possible."""

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls(context=context) 
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("Email successfully sent.")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")



def call_sos():
    account_sid = 'AC627962a7fb0539aac961e9020c6d619b'
  
    auth_token = 'a63c3ec7a784b9b6652c546a6ed2ab15'
  
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        to="+916379613654",  
        from_="+15593963446"  
    )
    print("Call alert sent successfully.")


def sms_alert():
    account_sid = 'AC627962a7fb0539aac961e9020c6d619b'  
    auth_token = 'a63c3ec7a784b9b6652c546a6ed2ab15'  

    client = Client(account_sid, auth_token)

    phone_numbers = [
        "+916382293288",
        "+916379613654",
        "+917871937373"
    ]

    for number in phone_numbers:
        message = client.messages.create(
            body="This is SOS Alert",
            from_="+15593963446",  
            to=number
        )
    print("SMS alerts sent successfully.")



sys.stdout.reconfigure(encoding='utf-8')
engine = pyttsx3.init("sapi5")
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)



def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")

    speak("I am Clara, your personal desktop assistant. How can I help you?")


def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except sr.UnknownValueError:
            print("Say that again, please...")
            return "None"
    return query



if __name__ == "__main__":
    wish()
    while True:
        query = takecommand().lower()

        if "sos" in query:
            speak("SOS action detected.")
            speak("Sending SOS alert email.")
            email_sos()
            speak("Email sent successfully.")
            speak("Making SOS alert call.")
            call_sos()
            speak("Call alert sent successfully.")
            sms_alert()
            speak("SMS alert sent successfully.")
