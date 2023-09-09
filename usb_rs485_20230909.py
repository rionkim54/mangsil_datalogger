import serial
import time
import os
import datetime


def log_data(data):
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a log entry with the timestamp and data
    log_entry = f"{timestamp}: {data}\n"
    
    # Specify the USB disk mount point
    usb_mount_point = "/media/zw/_______"
    
    # Check if the USB disk is mounted
    if os.path.ismount(usb_mount_point):
        # Define the log file path
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        log_file_path = os.path.join(usb_mount_point, f"data_log_{current_date}.csv")
        
        # Append the log entry to the log file
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry)
            
        print("Data logged successfully.")
    else:
        print("USB disk is not mounted.")



def main():
    # 시리얼 포트와 통신 속도 설정
    #ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=1)
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

    command_list = [
        bytes([0xCC, 0x03, 0x00, 0x03, 0x00, 0x03, 0xe5, 0xD6]), # radiation - indoor
        bytes([0xc8, 0x03, 0x00, 0x00, 0x00, 0x02, 0xd5, 0x92]), # wind - indoor
        bytes([0x66, 3, 0, 0, 0, 8, 0x4c, 0x1b]),  # temperature - indoor
        bytes([0xc9, 3, 0, 0, 0, 2, 0xd4, 0x43]),  # rainfall - indoor
        bytes([0xdc, 3, 0, 3, 0, 3, 0xe7, 0x46]),  # radiation - outdoor
        bytes([0xd8, 3, 0, 0, 0, 2, 0xD7, 0x02]),  # wind - outdoor
        bytes([0x76, 3, 0, 0, 0, 8, 0x4E, 0x8b]),  # temperature
        bytes([0xd9, 3, 0, 0, 0, 2, 0xd6, 0xd3])   # rainfall - outdoor
    ]

    try:
        while True:
            for send_data in command_list:

                print("Sent:", send_data)
                # 데이터 전송
                ser.write(send_data)

                # 데이터 수신 (응답의 길이는 19 bytes임을 가정)
                recv_data = ser.read(32)

                
                                            
                # 수신된 데이터 출력
                print("Received:", [hex(byte) for byte in recv_data])

                # 5초 대기
                time.sleep(5)

            log_data("Temperature: 25 C")

    except KeyboardInterrupt:
        print("Program terminated")

    finally:
        # 시리얼 포트 닫기
        ser.close()

if __name__ == "__main__":
	main()

