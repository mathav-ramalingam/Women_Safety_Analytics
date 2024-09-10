import cv2
import os
import numpy as np
from keras.models import load_model
from flask import Flask, render_template, Response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from twilio.rest import Client
import ssl

# Define a Flask app
app = Flask(__name__)

# Paths to the pre-trained models
MODEL_PATH_1 = 'C:/Users/matha/Documents/SIH/Web_App/Deployment - main/models/Gender_Classify.keras'
MODEL_PATH_2 = 'C:/Users/matha/Documents/SIH/Web_App/Deployment - main/models/harassment(N)_mobilenetv2.h5'

# Load your trained models
model_1 = load_model(MODEL_PATH_1)
model_2 = load_model(MODEL_PATH_2)

# Function to preprocess frame for prediction
def model_predict_frame(frame, model, target_size=(299, 299)):
    try:
        frame_resized = cv2.resize(frame, target_size)
        frame_resized = frame_resized.astype('float32') / 255
        x = np.expand_dims(frame_resized, axis=0)
        preds = model.predict(x)
        return preds
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None

# Load OpenCV's pre-trained Haar Cascade face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def gen_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale (for face detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # Initialize counters
        male_count = 0
        female_count = 0

        if len(faces) == 0:
            # Get frame dimensions to center the text at the bottom
            frame_height, frame_width = frame.shape[:2]
            
            # Set text position to be center-bottom
            text = "No human detected"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (frame_width - text_size[0]) // 2
            text_y = frame_height - 50
            
            # Display "No human detected" in the center-bottom
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            for (x, y, w, h) in faces:
                # Draw a rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Extract the face region for gender prediction
                face = frame[y:y + h, x:x + w]

                # First model (gender detection)
                preds = model_predict_frame(face, model_1)

                if preds is None:
                    continue

                prob = preds[0][0]

                if prob > 0.6:
                    result = "Female"
                    female_count += 1  # Increment female count
                    
                    # Second model (harassment detection)
                    second_model_preds = model_predict_frame(face, model_2, target_size=(224, 224))

                    if second_model_preds is None:
                        continue

                    harassment_label = np.argmax(second_model_preds)
                    harassment_labels = ['Harassment', 'Non-Harassment']
                    # Only append harassment detection if it is detected
                    # if harassment_labels[harassment_label] == 'Harassment':
                    #     send_sos_email()  # Send SOS email
                    #     send_twilio_alert()  # Send SMS and make a call
                    #     cv2.putText(frame, "Harassment Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Green color for text
                    # else:
                    #     # Optional: Add text for "Non-Harassment" detection
                    #     cv2.putText(frame, "Non-Harassment", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Red color for text


                else:
                    result = "Male"
                    male_count += 1  # Increment male count

                # Display "Male" or "Female" in the box (simplified, without "Gender:")
                cv2.putText(frame, result, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Green color for text

        # Display the total count of males and females at the top of the frame
        total_text = f"Male: {male_count}, Female: {female_count}"
        cv2.putText(frame, total_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)  # Black color for total count

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()


# Function to send an SOS email
def send_sos_email():
    email_sender = 'jahaganapathi1@gmail.com'
    email_password = 'bkggefxqikzpbmke'
    email_receivers = [
        'arunaananthagiri04@gmail.com',
        'mathavramalingam1608@gmail.com',
        'sreepriyanth2005@gmail.com',
        'bavyadharshinir.22cse@kongu.edu'
    ]

    url = 'https://66c62f95a65a5b61a9d3136b--coruscating-marigold-a0ceb0.netlify.app/'
    filename = 'hello.txt'

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            
            for email_receiver in email_receivers:
                msg = MIMEMultipart()
                msg['From'] = email_sender
                msg['To'] = email_receiver
                msg['Subject'] = "SOS ALERT"
                
                body = f"SOS ALERT DETECTED. Please visit the following link for more details: {url}"
                msg.attach(MIMEText(body, 'plain'))
                
                try:
                    with open(filename, 'rb') as f:
                        attachment = MIMEApplication(f.read(), _subtype='txt')
                        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(attachment)
                except FileNotFoundError:
                    print(f"Error: The file '{filename}' was not found.")
                    continue  
                
                smtp.sendmail(email_sender, email_receiver, msg.as_string())
            
        print("Emails successfully sent.")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check your email and password.")
    except smtplib.SMTPConnectError:
        print("Failed to connect to the SMTP server.")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

# Function to send SMS and make a call using Twilio
def send_twilio_alert():
    account_sid = "ACcd0d88307fcfd80e81de7e8885fe2d3f"
    auth_token = "fcac17f33fa681e4289c6871c800b005"
    
    client = Client(account_sid, auth_token)
    
    # Sending SMS
    message = client.messages.create(
        body="This is an SOS Alert",
        from_="+12562239694",
        to="+917871937373"
    )
    print("MESSAGE SENT TO MATHAV")
    
    # Making a call
    call = client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        to="+916379613654",  # JAHA
        from_="+12562239694"
    )
    print("CALL MADE TO JAHA")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)