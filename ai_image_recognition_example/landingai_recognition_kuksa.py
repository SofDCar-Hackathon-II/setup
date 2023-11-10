import os
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint
from landingai.pipeline.image_source import Webcam
from landingai.predict import Predictor
import cv2


import time
endpoint_id = "3348b414-37cc-46a6-b924-9e0aae07c219"
api_key = os.getenv('LANDING_AI_API_KEY')
predictor = Predictor(endpoint_id, api_key=api_key)
one = 0
three = 0
def setVSSValue(vss, value):
    client.set_current_values({
        vss: Datapoint(value)
    })  

with VSSClient('127.0.0.1', 55556) as client:
    for updates in client.subscribe_current_values([
        'Vehicle.Window.Row1.DriverSide.Sensor.Position', 
        'Vehicle.Window.Row2.DriverSide.Sensor.Position'
    ]):
        with Webcam(fps=0.25) as webcam:
            for frame in webcam:
                frame.run_predict(predictor=predictor) 
                frame.overlay_predictions()
                print(frame.predictions)
                frame.save_image("./latest-webcam-image.png", include_predictions=True) 
                detection_score = 0
                detection_label = "n/a"
                for prediction in frame.predictions:
                    if prediction.score > detection_score:
                        detection_score = prediction.score
                        detection_label = prediction.label_name
                print("label: ", detection_label, " score: ", detection_score)
                if detection_label == "one":
                    if one == 0:
                        print("hier")
                        one = 1
                        setVSSValue("Vehicle.Window.Row1.DriverSide.Action", "open")
                    else:
                        one = 0
                        setVSSValue("Vehicle.Window.Row1.DriverSide.Action", "close")
                elif detection_label == "three":
                    if three == 0:
                        three = 1
                        setVSSValue("Vehicle.Window.Row2.DriverSide.Action", "open")
                    else:
                        three = 0
                        setVSSValue("Vehicle.Window.Row2.DriverSide.Action", "close")
                image = cv2.imread("./latest-webcam-image.png")
                cv2.imshow('image', image)
                if cv2.waitKey(25) & 0xFF == ord('q'): break
print("Finished.")
