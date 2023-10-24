import serial
import time
import os
import datetime
import csv

command_list = {
	# bytes([0x07, 0x03, 0x00, 0x00, 0x00, 0x07]),	# T&H #1
	bytes([0x08, 0x03, 0x00, 0x00, 0x00, 0x07]),	# T&H #2
	#bytes([0x08, 0x03, 0x01, 0xF4, 0x00, 0x02]), # , 0x84, 0x9C]),
	bytes([0x08, 0x03, 0x01, 0xFA, 0x00, 0x02]), # , 0x84, 0x9C]),

	# bytes([0x66, 3, 0, 0, 0, 2]), #, 0x4c, 0x1b]), # "temperature": humidity
	# bytes([0x76, 3, 0, 0, 0, 2]), #, , 0x4E, 0x8b]), # "temperature": humidity

	# bytes([0xCC, 0x03, 0x00, 0x00, 0x00, 0x01]), #, , 0xe5, 0xD6]), # "radiation": 
	# bytes([0xDC, 0x03, 0x00, 0x00, 0x00, 0x01]), #, , 0xe5, 0xD6]), # "radiation": 

	bytes([0xc8, 0x03, 0x00, 0x00, 0x00, 0x01]), #, , 0xd5, 0x92]), # "wind": 

	bytes([0xd9, 3, 0, 0, 0, 2]), #, , 0xd6, 0xd3]), # "rainfall": 
	bytes([0xc9, 3, 0, 0, 0, 2]), #, , 0xd6, 0xd3]), # "rainfall": 
}
usb_mount_point = "/media/zw/_______"

radiation_value = 0
wind_value = 0
temperature = 0
moisture_value = 0
rain_fall = 0

def calculate_modbus_crc(data):
    crc_table = (
        0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
        0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
        0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
        0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
        0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
        0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
        0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
        0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
        0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
        0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
        0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
        0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
        0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
        0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
        0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
        0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
        0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
        0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
        0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
        0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
        0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
        0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
        0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
        0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
        0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
        0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
        0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
        0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
        0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
        0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
        0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
        0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040,
    )
    
    crc = 0xFFFF
    for byte in data:
        index = (crc ^ byte) & 0xFF
        crc = (crc >> 8) ^ crc_table[index]
    return crc & 0xFFFF

def irradiance_to_lux(irradiance_watt_per_m2):
    """Convert irradiance (in W/m^2) to illuminance (in lux) for sunlight.
    
    Note: This is a rough conversion for sunlight and may not be accurate under all conditions.
    
    Parameters:
    - irradiance_watt_per_m2: The irradiance in W/m^2.
    
    Returns:
    - illuminance in lux.
    """
    return irradiance_watt_per_m2 * 100000 / 1000  # Convert kW/m^2 to lux

def lux_to_irradiance(lux):
    """Convert illuminance (in lux) to irradiance (in W/m^2) for sunlight.
    
    Note: This is a rough conversion for sunlight and may not be accurate under all conditions.
    
    Parameters:
    - lux: The illuminance in lux.
    
    Returns:
    - irradiance in W/m^2.
    """
    return lux * 1000 / 100000  # Convert lux to kW/m^2

def check_modbus_crc(data):

    # 원래 데이터의 마지막 2바이트 (CRC 값)
    original_crc = int.from_bytes(data[-2:], byteorder='big')
    
    # CRC 계산
    crc = 0xFFFF
    for byte in data[:-2]:  # 마지막 2바이트 제외
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    
    # 계산된 CRC 바이트 순서 변경 (Little-endian)
    calculated_crc = ((crc & 0xFF) << 8) | ((crc & 0xFF00) >> 8)
    
    # 원래의 CRC와 계산된 CRC가 같은지 비교
    return original_crc == calculated_crc

def next_row(ser):
    
	global radiation_value
	global wind_value
	global temperature
	global moisture_value
	global rain_fall

	# timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	# result_line = timestamp.split()[0:2]

	# print("command_list", len(command_list))

	for send_data in command_list:

		crc = calculate_modbus_crc(send_data)

		# Add CRC to the data
		data_with_crc = send_data + bytes([crc & 0xFF, (crc >> 8) & 0xFF])
		print(data_with_crc)
		ser.write(data_with_crc)

		time.sleep(1)
		
        # 데이터 수신 (응답의 길이는 19 bytes 임을 가정)
		recv_data = ser.read(32)
		if (check_modbus_crc(recv_data)) :
			print("recv_data=", recv_data)
			data_list = list(bytearray(recv_data))
			print("data_list=", data_list)
			
			
			if (recv_data[0] == 0xCC) :
				if(recv_data[2] == 2) :
					radiation_value = recv_data[3] * 0x100 + recv_data[4]
					print("radiation_value", radiation_value)

				if(recv_data[2] == 6) :
					radiation_value = recv_data[7] * 0x100 + recv_data[8]
					print("radiation_value", radiation_value)

			if (recv_data[0] == 0xDC) :
				if(recv_data[2] == 2) :
					radiation_value = recv_data[3] * 0x100 + recv_data[4]
					print("radiation_value[DC]", radiation_value)

				if(recv_data[2] == 6) :
					radiation_value = recv_data[7] * 0x100 + recv_data[8]
					print("radiation_value[DC]", radiation_value)					

			# if (recv_data[0] == 0xDC) :
			# 	radiation_value = recv_data[3] * 0x100 + recv_data[4]
			# 	print("radiation_value", radiation_value)

			if (recv_data[0] == 0xC8) :
				wind_value = int(recv_data[3] * 0x100 + recv_data[4]) / 10
				print("wind_value", wind_value)

			if (recv_data[0] == 0x08) :
				if (recv_data[2] == 14) :
					if recv_data[3] & 0b10000000 == 0:  # 2's complement
						temperature = int(recv_data[5] * 0x100 + recv_data[6]) / 10
					else:
						temperature = int(recv_data[5] * 0x100 + recv_data[6]) / -10
				
					moisture_value = int(recv_data[3] * 0x100 + recv_data[4]) / 10

					print(recv_data[0], "temperature", temperature, "moisture_value", moisture_value)

				if(recv_data[2] == 4) :
					radiation_value = lux_to_irradiance(recv_data[5] * 0x100 + recv_data[6])
					print("radiation_value", radiation_value)		


			# if (recv_data[0] == 0x09) :
			# 	if recv_data[3] & 0b10000000 == 0:  # 2's complement
			# 		temperature = int(recv_data[5] * 0x100 + recv_data[6]) / 10
			# 	else:
			# 		temperature = int(recv_data[5] * 0x100 + recv_data[6]) / -10
			
			# 	moisture_value = int(recv_data[3] * 0x100 + recv_data[4]) / 10

			# 	print(recv_data[0], "temperature", temperature, "moisture_value", moisture_value)

			if (recv_data[0] == 0x66) :
				if recv_data[3] & 0b10000000 == 0:  # 2's complement
					temperature = int(recv_data[3] * 0x100 + recv_data[4]) / 100
				else:
					temperature = int(recv_data[3] * 0x100 + recv_data[4]) / -100
			
				moisture_value = int(recv_data[5] * 0x100 + recv_data[6]) / 100
				
				print(recv_data[0], "temperature", temperature, "moisture_value", moisture_value)
				
			if (recv_data[0] == 0x76) :
				if recv_data[3] & 0b10000000 == 0:  # 2's complement
					temperature = int(recv_data[3] * 0x100 + recv_data[4]) / 100
				else:
					temperature = int(recv_data[3] * 0x100 + recv_data[4]) / -100
			
				moisture_value = int(recv_data[5] * 0x100 + recv_data[6]) / 100
				
				print(recv_data[0], "temperature", temperature, "moisture_value", moisture_value)

			if (recv_data[0] == 0xC9) :
				rain_fall = int(recv_data[3] * 0x100 + recv_data[4]) / 10
				print("rain_fall", rain_fall)

				
			if (recv_data[0] == 0xD9) :
				rain_fall = int(recv_data[3] * 0x100 + recv_data[4]) / 10
				print("rain_fall", rain_fall)
		
		# if cmd.find("radiation") != -1:
		# 	radiation_value = data_list[3] * 0x100 + data_list[4]
		# 	result_line.append(radiation_value)
		# elif cmd.find("wind") != -1:
		# 	wind_value = int(data_list[3] * 0x100 + data_list[4]) / 10
		# 	result_line.append(wind_value)  # wind speed라 가정. wind direction일 경우 result_value 를 넣음
		# elif cmd.find("temperature") != -1:  # RS-ECTH-N01-A type이라 가정. RS-ECTH-N01-B이면 순서 바꿔야함...
		# 	if data_list[3] & 0b10000000 == 0:  # 2's complement
		# 		temperature = int(data_list[3] * 0x100 + data_list[4]) / 100
		# 	else:
		# 		temperature = int(data_list[3] * 0x100 + data_list[4]) / -100
		# 	result_line.append(temperature)
		# 	moisture_value = int(data_list[5] * 0x100 + data_list[6]) / 100
		# 	result_line.append(moisture_value)
		# 	conductivity = data_list[7] * 0x100 + data_list[8]
		# 	result_line.append(conductivity)
		# 	salinity = data_list[7] * 0x100 + data_list[8]
		# 	result_line.append(salinity)
		# 	dissolved_solid = data_list[9] * 0x100 + data_list[10]
		# 	result_line.append(dissolved_solid)
		# 	dielectric_value = data_list[11] * 0x100 + data_list[12]
		# 	result_line.append(dielectric_value)
		# elif cmd.find("rainfall") != -1:
		# 	rain_value = data_list[3] * 0x100 + data_list[4]  # 이거는 자료가 없어서 그냥 이거로 함..
		# 	result_line.append(rain_value)
		# raw_data_file = "rawdata.txt"
		# with open(raw_data_file, 'w') as raw_file:
		# 	raw_file.writelines(f"Sent: {send_data}\n")
		# 	raw_file.writelines(f"Received: {data_list}\n")
			
	# csv_writer.writerow(result_line)


#	with open(log_file_path, 'a', newline='') as f:
#		csv_writer = csv.writer(f)
#		csv_writer.writerow(result_line)


def first_row(csv_writer):
	first_writing_row_list = ['date', 'time', 'temperature', 'moisture', 'radiation', "rainfall", "wind" ]
	csv_writer.writerow(first_writing_row_list)

def add_row(csv_writer):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	result_line = timestamp.split()[0:2]

	result_line.append(temperature)
	result_line.append(moisture_value)
	result_line.append(radiation_value)
	result_line.append(rain_fall)
	result_line.append(wind_value)
	csv_writer.writerow(result_line)

	print("add_row", result_line)

# with open(log_file_path, 'a', newline='') as f:
# 	csv_writer = csv.writer(f)
# 	first_writing_row_list = ['date', 'time']
# 	for key in command_list:
# 		if key.find(">") == -1:
# 			first_writing_row_list.append(key)
# 		else:
# 			first_writing_row_list += key.split(">")
# 	csv_writer.writerow(first_writing_row_list)
# csv_writer.writerow(['date', 'time', 'radiation-indoor [W/m^2]', 'wind-indoor [m/s]', 'temperature-indoor [C]', 'rainfall-indoor', 'radiation-outdoor [W/m^2]',
#					 'wind-outdoor [m/s]', 'temperature-outdoor [C]', 'rainfall-outdoor'])


def create_csv_file(ser):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	first_current_date = timestamp.split()[0]
	log_file_path = os.path.join(usb_mount_point, f"data_log_{first_current_date}.csv")
	csv_file = open(log_file_path, 'a', newline='')
	csv_writer = csv.writer(csv_file)
	first_row(csv_writer)
	csv_file.close()

	loop = 0
	try:
		while True:
			timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			current_date = timestamp.split()[0]
			if first_current_date != current_date:
				break

			next_row(ser)
			
			# 5초 대기
			time.sleep(5)
			loop += 1

			if(loop % 12 == 0) :
				csv_file = open(log_file_path, 'a', newline='')
				csv_writer = csv.writer(csv_file)
				add_row(csv_writer)
				csv_file.close()

	except KeyboardInterrupt:
		print("Program terminated")
		exit(0)
	except Exception as e:
		error_file = open(f"error_{first_current_date}.txt", "w")
		error_file.writelines(str(e))
		error_file.close()
		csv_file.close()


def main():
	# 시리얼 포트와 통신 속도 설정
	# ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=1)
	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
	if os.path.ismount(usb_mount_point):
		print("Data logged successfully.")
		try:
			while True:
				create_csv_file(ser)
		except KeyboardInterrupt:
			print("Program terminated")
			exit(0)
		finally:
			# 시리얼 포트 닫기
			ser.close()
	else:
		print("USB disk is not mounted.")


if __name__ == "__main__":
	main()
