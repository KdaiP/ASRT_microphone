# ASRT_microphone

基于[ASRT](https://github.com/nl8590687/ASRT_SpeechRecognition)的实时麦克风语音识别项目

项目基于[ASRT v1.3.0 Released](https://github.com/nl8590687/ASRT_SpeechRecognition/releases/tag/v1.3.0)制作，已内置训练好的语音识别模型，无需重新训练。

客户端请下载client文件夹，服务器端请下载server文件夹，并按requirements.txt配置环境。

## 安装

根据文件夹内部的requirements.txt进行配置。

由于ASRT的grpcio和protobuf依赖会版本冲突的原因，建议手动进行依赖的安装，先安装grpcio和grpcio-tools，再安装protobuf。虽然pip会报错，但是程序可以正常运行：

```shell
$ pip3 install grpcio==1.51.1 
$ pip3 install grpcio-tools==1.51.1 
$ pip3 install protobuf==3.19
```

## 配置

服务器端修改asrserver_grpc.py，根据IP地址和端口号修改以下两项：

```python
parser.add_argument('--listen', default='0.0.0.0', type=str, help='the network to listen')
parser.add_argument('--port', default='20002', type=str, help='the port to listen')
```

客户端修改client_grpc.py相应的选项：

```python
conn=grpc.insecure_channel('127.0.0.1:20002')
```

## 使用

服务器端运行asrserver_grpc.py，客户端运行client_grpc.py。客户端会捕获麦克风的音频信息，进行端点检测，然后将数据发送给服务端。

## 故障排除
在Linux环境下，如果无法使用pyaudio，请事先安装portaudio：

```shell
sudo apt install portaudio19-dev
```