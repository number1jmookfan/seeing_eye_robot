import cv2
import sys
import subprocess
import numpy as np

# Configuration
WIDTH = 1280
HEIGHT = 720
FPS = 35
RTMP_URL = "rtmp://your-server-ip:1935/live/stream"  # For RTMP server
# Alternative: UDP streaming
# UDP_URL = "udp://192.168.1.100:5000"

def stream_camera_to_rtmp():
    """
    Stream from webcam to RTMP server (can be received by OBS)
    """
    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    ffmpeg_path = "/home/lekiwi/miniconda3/envs/lerobot/bin/ffmpeg"
    
    # FFmpeg command for RTMP streaming
    ffmpeg_cmd = [
        ffmpeg_path,
        '-y',  # Overwrite output
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', f'{WIDTH}x{HEIGHT}',
        '-r', str(FPS),
        '-i', '-',  # Input from pipe
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-f', 'flv',
        RTMP_URL
    ]
    
    # Start FFmpeg process
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    print(f"Streaming to {RTMP_URL}")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize frame if needed
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            
            # Optional: Add processing here (text, effects, etc.)
            cv2.putText(frame, "Live Stream", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display locally (optional)
            #cv2.imshow('Streaming', frame)
            
            # Write frame to FFmpeg
            process.stdin.write(frame.tobytes())
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        #cv2.destroyAllWindows()
        process.stdin.close()
        process.wait()

def stream_to_udp(cameraIndex: int, destination: str):
    """
    Stream to UDP endpoint (can be received by OBS via Media Source)
    OBS Setup: Add Media Source -> Uncheck "Local File" -> 
    Input: udp://@:5000 (on receiving computer)
    """
    cap = cv2.VideoCapture(cameraIndex)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    
    # FFmpeg command for UDP streaming with MPEGTS
    ffmpeg_path = "/home/lekiwi/miniconda3/envs/lerobot/bin/ffmpeg"
    #low motion artifact
    # ffmpeg_cmd = [
        # ffmpeg_path,
        # '-y',
        # '-f', 'rawvideo',
        # '-vcodec', 'rawvideo',
        # '-pix_fmt', 'bgr24',
        # '-s', f'{WIDTH}x{HEIGHT}',
        # '-r', str(FPS),
        # '-i', '-',
        # '-c:v', 'libx264',
        # '-pix_fmt', 'yuv420p',
        # '-preset', 'medium',
        # '-tune', 'film',
        # '-crf', '20',
        # '-b:v', '2.5M',
        # '-maxrate', '3M',
        # '-bufsize', '6M',
        # '-refs', '4',
        # '-me_method', 'umh',
        # '-subq', '7',
        # '-bf', '3',
        # '-g', str(FPS * 2),
        # '-f', 'mpegts',
        # f'udp://{destination}'
    # ]
    #low latency
    ffmpeg_cmd = [ffmpeg_path, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{WIDTH}x{HEIGHT}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast', '-tune', 'zerolatency', '-b:v', '3M', '-maxrate', '4M', '-bufsize', '6M', '-refs', '3', '-bf', '2', '-g', str(FPS), '-f', 'mpegts', f'udp://{destination}']
    
    
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    print(f"Streaming via UDP to {destination}")
    print("In OBS: Media Source -> udp://@:[PORT_NUMBER]")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            #cv2.imshow('UDP Stream', frame)
            process.stdin.write(frame.tobytes())
            
            #if cv2.waitKey(1) & 0xFF == ord('q'):
             #   break
                
    finally:
        cap.release()
        #cv2.destroyAllWindows()
        process.stdin.close()
        process.wait()


def main():
    # Arg1: Camera Index, Arg2: Destination IP and Port
    if not sys.argv[1] or not sys.argv[2]:
        print("invalid arguments. Enter as format: python video_sender.py [CAM_INDEX] [DESTINATIONIP:PORT]")
        return
    stream_to_udp(int(sys.argv[1]), sys.argv[2])

if __name__ == "__main__":
    # Choose your streaming method:
    
    # Option 1: RTMP streaming (requires RTMP server like nginx-rtmp)
    # stream_camera_to_rtmp()
    
    # Option 2: UDP streaming (direct peer-to-peer)
    # Arg1: Camera Index, Arg2: Destination IP and Port
    stream_to_udp(sys.argv[1], sys.argv[2])
    
    # Option 3: Screen capture streaming
    # stream_screen_capture()
    
    # Option 4: Receive stream on another computer
    # receive_stream_example()
