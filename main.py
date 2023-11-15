import cv2
from deepface import DeepFace
import os
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint
import time
import winsound

import json
import requests
from recorder import record_audio, read_audio

#####################################################################################################

def set_vss_value(vss, value):
    client.set_current_values({
        vss: Datapoint(value)
    })


#####################################################################################################

# Load the pre-trained emotion detection model
model = DeepFace.build_model("Emotion")

# Define emotion labels
# emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'tierd', 'surprise', 'neutral']

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video
cap = cv2.VideoCapture(0)

#####################################################################################################


# Wit speech API endpoint
API_ENDPOINT = 'https://api.wit.ai/speech'
# Wit.ai api access token
wit_access_token = 'ZTOEDNR6DYLZ6F3GXOWPSWBZNO5UAXWX'
headers = {'authorization': 'Bearer ' + wit_access_token}
def RecognizeSpeech(AUDIO_FILENAME, num_seconds):

    # record audio of specified length in specified audio file
    record_audio(num_seconds, AUDIO_FILENAME)

    # reading audio
    audio = read_audio(AUDIO_FILENAME)

    # defining headers for HTTP request
    headers = {'authorization': 'Bearer ' + wit_access_token,
               'Content-Type': 'audio/wav'}
# making an HTTP post request
    resp = requests.post(API_ENDPOINT, headers = headers,
                         data = audio)

    # converting response content to JSON format
    #print(resp.content)
    byte_str = resp.content
    data = json.loads(json.dumps(byte_str.decode('utf-8')))

    # return the text
    return data

#####################################################################################################

if __name__ == "__main__":

        with VSSClient('192.168.1.99', 55556) as client:

            while True:

                text =  RecognizeSpeech('myspeech.wav', num_seconds = 5)
                #print("\nYou said: {}".format(text))

                if "wit_playmusic" in text:
                    command = "play_music"
                    time.sleep(1)
                    winsound.PlaySound('music.wav', winsound.SND_ASYNC | winsound.SND_FILENAME)
                    time.sleep(50)
                    winsound.PlaySound(None, winsound.SND_PURGE)
                    #set_vss_value("Vehicle.Door.Row1.DriverSide.Action", command)
                elif "wit_pasdooropen" in text:
                    command = "open_passenger_door"
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "open")
                    time.sleep(1)
                    set_vss_value("Vehicle.Door.Row2.DriverSide.Action", "open")
                    time.sleep(9)
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "close")
                    set_vss_value("Vehicle.Door.Row2.DriverSide.Action", "close")
                    time.sleep(5)
                    set_vss_value("Vehicle.Window.Row1.DriverSide.Action", "open")
                elif "wit_dimlight" in text:
                    command = "dim_light"
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "open")
                elif "wit_drdooropen" in text:
                    command = "open_driver_door"
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "open")
                    time.sleep(5)
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "close")

                    # set_vss_value("Vehicle.Cabin.Door.Row1.Left.IsOpen", "True")
                elif "wit_opentrunk" in text:
                    command = "open_trunk"
                    set_vss_value("Vehicle.Trunk.Action", "open")


                time.sleep(3)

                if command:
                    print(command)
                    # Capture frame-by-frame
                    ret, frame = cap.read()

                    # Convert frame to grayscale
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # Detect faces in the frame
                    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    for (x, y, w, h) in faces:
                        # Extract the face ROI (Region of Interest)
                        face_roi = gray_frame[y:y + h, x:x + w]

                        # Resize the face ROI to match the input shape of the model
                        resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)

                        # Normalize the resized face image
                        normalized_face = resized_face / 255.0

                        # Reshape the image to match the input shape of the model
                        reshaped_face = normalized_face.reshape(1, 48, 48, 1)

                        # Predict emotions using the pre-trained model
                        preds = model.predict(reshaped_face)[0]
                        emotion_idx = preds.argmax()
                        emotion = emotion_labels[emotion_idx]

                        # Draw rectangle around face and label with predicted emotion
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                        if emotion == "happy":
                            print(emotion)
                            # set_vss_value("Vehicle.Window.Row1.DriverSide.Action", "open")
                            # time.sleep(1)
                            # set_vss_value("Vehicle.Window.Row1.DriverSide.Action", "open")
                            time.sleep(3)
                            winsound.PlaySound('music.wav', winsound.SND_ASYNC | winsound.SND_FILENAME)
                            time.sleep(10)
                            winsound.PlaySound(None, winsound.SND_PURGE)



                            
                

                



