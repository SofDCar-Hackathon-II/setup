import os
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint
from landingai.pipeline.image_source import Webcam
from landingai.predict import Predictor
import cv2

endpoint_id = "3348b414-37cc-46a6-b924-9e0aae07c219"
api_key = os.getenv('LANDING_AI_API_KEY')
predictor = Predictor(endpoint_id, api_key=api_key)

# Define a function to set the value of a VSS signal
def set_vss_value(vss, value):
    client.set_current_values({
        vss: Datapoint(value)
    })

# Connect to the KUKSA server
with VSSClient('127.0.0.1', 55556) as client:

    # Subscribe to the VSS signals for the driver side windows
    updates = client.subscribe_current_values([
        'Vehicle.Window.Row1.DriverSide.Sensor.Position',
        'Vehicle.Window.Row2.DriverSide.Sensor.Position'
    ])

    # Start the webcam
    with Webcam(fps=0.25) as webcam:

        # For each frame from the webcam:
        # 1. Run the prediction on the frame
        # 2. Overlay the predictions on the frame
        # 3. Save the frame to a file
        # 4. Extract the label and score of the highest-scoring prediction
        # 5. If the label is "one" or "three", set the corresponding VSS signal
        # 6. Display the frame

        for frame in webcam:
            frame.run_predict(predictor=predictor)
            frame.overlay_predictions()
            frame.save_image("./latest-webcam-image.png", include_predictions=True)

            detection_score = 0
            detection_label = "n/a"
            for prediction in frame.predictions:
                if prediction.score > detection_score:
                    detection_score = prediction.score
                    detection_label = prediction.label_name

            if detection_label == "one":
                set_vss_value("Vehicle.Window.Row1.DriverSide.Action", "open")
            elif detection_label == "three":
                set_vss_value("Vehicle.Window.Row2.DriverSide.Action", "open")

            image = cv2.imread("./latest-webcam-image.png")
            cv2.imshow('image', image)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

print("Finished.")
