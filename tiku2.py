import cv2
import pyaudio
import wave
from scipy import signal
import time
import numpy as np
import random
import threading
import readchar
import tobii_research as tr
import csv
from itertools import zip_longest
import itertools

##出力されるcsvファイルの名前``
filename = 'tiku2.csv'

flag = 0
video_file1 = "/Users/apple/Desktop/M2/11月実験/mp4/deko.mp4"
video_file2 = "/Users/apple/Desktop/M2/11月実験/mp4/deko.mp4"
cap1 = cv2.VideoCapture(video_file1)
cap2 = cv2.VideoCapture(video_file2)
nini_start = 0
cap1.set(cv2.CAP_PROP_POS_FRAMES,nini_start)
cap2.set(cv2.CAP_PROP_POS_FRAMES,nini_start)

img1 = cv2.imread('1.png')
img2 = cv2.imread('2.png')

start = time.time()

alldata1 = []
alldata2 = []
alltime = []
alldata3 = [alldata1, alldata2, alltime]

cnt = 0
kb = 'a'
l = 0

def eyetrack():
    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]

    ##アイトラッカーが接続されているかの確認、接続されているものがあっているかの確認
    # print("Address: " + my_eyetracker.address)
    # print("Model: " + my_eyetracker.model)
    # print("Serial number: " + my_eyetracker.serial_number)

    #両目の位置でいい場合はこっち
    eye_x = []
    eye_y = []
    eye_dt = [eye_x, eye_y]

    ##使用するディスプレイの解像度　→　start_vid.pyでのresizeと同一にする必要あり
    # resolution_1 = 1920
    # resolution_2 = 1080
    resolution_1 = 2560
    resolution_2 = 1440

    fps = 120
    time_diff = 0
    diff = time_diff*fps


    for i in range(int(diff)):
        eye_x.append('0')
        eye_y.append('0')


    def gaze_data_callback(gaze_data):
        global  flag
        ##何秒ごとにデータを取るかをアイトラッカーに設定されているfpsを読み取って利用
        time_stamp = gaze_data.device_time_stamp
        ##左右の目の位置がどこにあるかの位置取得、キャリブレーションをする必要あり
        left_point = gaze_data.left_eye.gaze_point.position_on_display_area
        right_point = gaze_data.right_eye.gaze_point.position_on_display_area
        # print("Time:" + str(time_stamp))

        eye_point_x = (left_point[0]+right_point[0])/2*resolution_1
        eye_point_y = (left_point[1]+right_point[1])/2*resolution_2

        eye_x.append(eye_point_x)
        eye_y.append(eye_point_y)

        # print("eye_x:" + str(eye_point_x))
        # print("eye_y:" + str(eye_point_y))

        # if eye_point_x < 1920/2:
        #     flag = 0
        # if eye_point_x > 1920/2:
        #     flag = 1
        if eye_point_x < 2560/2:
            flag = 0
        if eye_point_x > 2560/2:
            flag = 1

        # print(flag)
    #アイトラッカーからのデータ取得開始
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=False)


    ##何秒データを取得するか
    # time.sleep(60)

    # ##アイトラッカーからのデータ取得解除
    if kb == 'q':
        my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

#
def audio():
    global cnt, l
    w = (1,2,3)
    A = list(itertools.product(w, repeat=2))
    AA = list(itertools.product(w, repeat=2))
    A.extend(AA)
    B = random.sample(A, len(A))

    while True:
        if kb == 's':
            start_1 = time.time()
            # チャンクサイズ(粒度)
            CHUNK_SIZE = 1024

            # a = random.randint(1,3)
            # b = random.randint(1,3)
            print(l+1)

            if l == 19:
                print("end")
                break

            a = B[l][0]
            b = B[l][1]
            l = l + 1

            if a==1:
                wf1 = wave.open('/Users/apple/Desktop/M2/11月実験/wav/sara3.wav', "r")
            if a==2:
                wf1 = wave.open('/Users/apple/Desktop/M2/11月実験/wav/zara3.wav', "r")
            if a==3:
                wf1 = wave.open('/Users/apple/Desktop/M2/11月実験/wav/deko3.wav', "r")
            if b==1:
                wf2 = wave.open('/Users/apple/Desktop/M2/11月実験/wav/sara3.wav', "r")
            if b==2:
                wf2 = wave.open('/Users/apple/Desktop/M2/11月実験/wav/zara3.wav', "r")
            if b==3:
                wf2 = wave.open('/Users/apple/Desktop/M2/11月実験/wav/deko3.wav', "r")


            # PyAudioインスタンスを作成する
            p = pyaudio.PyAudio()

            # Streamを開く。フォーマット・チャンネル・サンプリングレートをWAVファイルと
            # 合わせているが、合わせなくても再生は行える。
            # ちなみにフォーマットとはビット深度のことであり、
            # 8bitなら「p.get_format_from_width(1)」、
            # 16bitなら「p.get_format_from_width((2)」とバイト数で設定することに注意
            stream1 = p.open(format=p.get_format_from_width(wf1.getsampwidth()),
                          channels=wf1.getnchannels(),
                          # rate=wf1.getframerate(),
                          rate=48000,
                          output_device_index=0,
                          output=True
                          )

            stream2 = p.open(format=p.get_format_from_width(wf2.getsampwidth()),
                          channels=wf2.getnchannels(),
                          # rate=wf2.getframerate(),
                          rate=48000,
                          output_device_index=2,
                          output=True
                          )

            # データをチャンクサイズだけ読み込む
            data1 = wf1.readframes(CHUNK_SIZE)
            data2 = wf2.readframes(CHUNK_SIZE)

            alldata1.append(a)
            alldata2.append(b)
            # print(cnt)
            cnt = cnt + 1
            # Streamに読み取ったデータを書き込む＝再生する
            while len(data1) > 0 and len(data2) > 0 and kb == 's':
            # while kb == 's':
                  data1 = wf1.readframes(CHUNK_SIZE)
                  data2 = wf2.readframes(CHUNK_SIZE)
                  # stream1.write(data1)
                  # stream2.write(data2)
                  # Streamに書き込む
                  if flag == 0:
                      # print("L")
                      stream1.write(data1)
                      stream2.write(data1*0)

                  if flag == 1:
                      # print("R")
                      stream2.write(data2)
                      stream1.write(data2*0)

                  if kb == 'b':
                      end_time = time.time() - start_1
                      # print(end_time)
                      alltime.append(end_time)
                      break




        if kb == 'q'or l == 19:
            stream1.stop_stream()
            stream1.close()
            stream2.stop_stream()
            stream2.close()
            # PyAudioインスタンスを破棄する
            p.terminate()
            break

def wait_input():
    global kb
    while True:
        kb = readchar.readchar()
        if kb == 'q' or l == 19:
            break




if __name__ == '__main__':

    thread1 = threading.Thread(target=eyetrack)
    thread2 = threading.Thread(target=audio)
    thread3 = threading.Thread(target=wait_input)

    thread1.start()
    thread2.start()
    thread3.start()

    while True:
        # 動画の再生
        elapsed_time = (time.time() - start)*1000
        play_time = int(cap1.get(cv2.CAP_PROP_POS_MSEC))

        if elapsed_time < play_time:
            key = cv2.waitKey(1)
        else:
            ret, frame1 = cap1.read()

        elapsed_time = (time.time() - start)*1000
        play_time = int(cap2.get(cv2.CAP_PROP_POS_MSEC))

        if elapsed_time < play_time:
            key = cv2.waitKey(1)
        else:
            ret, frame2 = cap2.read()

        frame3 = cv2.hconcat([frame1, frame2]) #横に結合
        cv2.waitKey(25)
        # frame4 = cv2.resize(frame3, (1920, 540))
        cv2.imshow("PlayVideo", frame3)
        cv2.moveWindow("PlayVideo", -2560, 200)
        # cv2.moveWindow("PlayVideo", -1920, -200)
        # key = cv2.waitKey(1)
        if kb == 'b':
            cap1.set(cv2.CAP_PROP_POS_FRAMES,nini_start)
            cap2.set(cv2.CAP_PROP_POS_FRAMES,nini_start)

        if kb == 'q' or l == 19:
            break

        if flag == 0 :
            cv2.namedWindow("sample", cv2.WINDOW_NORMAL)
            cv2.imshow('sample', img1)

        if flag == 1 :
            cv2.namedWindow("sample", cv2.WINDOW_NORMAL)
            cv2.imshow('sample', img2)

        if flag == 0 :
            cv2.namedWindow("sample2", cv2.WINDOW_NORMAL)
            cv2.imshow('sample2', img2)

        if flag == 1 :
            cv2.namedWindow("sample2", cv2.WINDOW_NORMAL)
            cv2.imshow('sample2', img1)

    print("end")
    print(alldata3)

    ##CSVファイルの書き出し
    export_data = zip_longest(*alldata3, fillvalue = '')
    with open(filename, 'w', encoding="ISO-8859-1", newline='') as file:
          write = csv.writer(file)
          write.writerow(("left","right","time"))
          write.writerows(export_data)

    thread1.join()
    thread2.join()
    thread3.join()
