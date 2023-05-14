import io
import numpy as np
import torch
torch.set_num_threads(1)
import torchaudio
import matplotlib.pylab as plt
torchaudio.set_audio_backend("soundfile")
import pyaudio
import threading
import queue
import grpc
import time
from assets.asrt_pb2_grpc import AsrtGrpcServiceStub
from assets.asrt_pb2 import SpeechRequest, LanguageRequest, WavData

model, utils = torch.hub.load(repo_or_dir='snakers4silero-vad',
                              model='silero_vad',
                              force_reload=False,source="local")
def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound


def main():
    conn=grpc.insecure_channel('127.0.0.1:20002')
    client = AsrtGrpcServiceStub(channel=conn)

    audio_queue = queue.Queue()
    print("Main progress")
    threading.Thread(target=record, args=(audio_queue,)).start()
    try:
        while True:
            def data():
                wav_bytes = audio_queue.get()
                wav_data = WavData(samples=wav_bytes, sample_rate=16000,
                                channels=1, byte_width=2)
                yield SpeechRequest(wav_data=wav_data)
            
            status_response = client.Stream(data())
            for ret in status_response:
                if ret.status_code == 200000:
                    print(ret.text_result)
                    time.sleep(0.1)
            #print(output)
            
    except KeyboardInterrupt:
        return 0


def record(audio_queue):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SAMPLE_RATE = 16000
    CHUNK = int(SAMPLE_RATE / 10)

    audio = pyaudio.PyAudio()
    num_samples = 1536

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    
    print("Started Recording")
    data = []
    bytes_acc = bytes()
    while True:
        
        
        audio_chunk = stream.read(num_samples)
        
        # in case you want to save the audio later
        data.append(audio_chunk)
        bytes_acc  += audio_chunk
        
        audio_int16 = np.frombuffer(audio_chunk, np.int16);

        audio_float32 = int2float(audio_int16)
        
        # get the confidences and add them to the list to plot them later
        new_confidence = model(torch.from_numpy(audio_float32), 16000).item()
        if new_confidence <0.15:
            audio_queue.put_nowait(bytes_acc)
            bytes_acc = bytes()
            #print(type(audio_chunk))
        


if __name__ == "__main__":
    main()