import cv2
import subprocess
import numpy as np

# Configuration
WIDTH = 1280
HEIGHT = 720
FPS = 30
RTMP_URL = "rtmp://your-server-ip:1935/live/stream"  # For RTMP server
# Alternative: UDP streaming
# UDP_URL = "udp://192.168.1.100:5000"

def receive_stream_example():
    """
    Example receiver code (run on another computer)
    This shows how to receive and display the stream
    """
    # Receive UDP stream
    cap = cv2.VideoCapture('udp://@:5000')
    
    # Or receive RTMP stream
    # cap = cv2.VideoCapture('rtmp://server-ip:1935/live/stream')
    
    print("Receiving stream... Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No frame received")
            break
            
        cv2.imshow('Received Stream', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Receive stream on another computer
    receive_stream_example()