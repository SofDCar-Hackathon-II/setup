import json
import requests
from recorder import record_audio, read_audio
from ast import literal_eval
from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint
import winsound
import time

def set_vss_value(vss, value):
    client.set_current_values({
        vss: Datapoint(value)
    })


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

    #json_formatted_str = json.dumps(data, indent=2)

    #print(json_formatted_str)
# get text from data


    # return the text
    return data

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
                    set_vss_value("Vehicle.Door.Row2.DriverSide.Action", "open")
                    time.sleep(8)
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "close")
                    set_vss_value("Vehicle.Door.Row2.DriverSide.Action", "close")
                elif "wit_dimlight" in text:
                    command = "dim_light"
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "open")
                elif "wit_drdooropen" in text:
                    command = "open_driver_door"
                    set_vss_value("Vehicle.Door.Row1.DriverSide.Action", "open")
                    # set_vss_value("Vehicle.Cabin.Door.Row1.Left.IsOpen", "True")
                elif "wit_opentrunk" in text:
                    command = "open_trunk"
                    set_vss_value("Vehicle.Trunk.Action", "open")

                print(command)

                
        




    # resp=requests.get('https://api.wit.ai/message?&q=(%s)' % text, headers = headers)
    # #print(resp.content)
    # #data = json.loads(resp.content)
    # my_bytes_value = resp.content
    # data = json.loads(my_bytes_value.decode().replace("'", '"'))
    #
    # print(data)
