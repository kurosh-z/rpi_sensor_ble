# /* cSpell:disable */
import sys, os, time
import struct
import logging
from datetime import datetime

import re
import socket

import json

# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

from gatt_linux import DeviceManager, Device


# MAC = "D2:B6:AF:05:2B:18"
# MAC = "D7:E9:FA:4E:E6:E0"
MAC = "FD:F2:55:EA:E0:42"
CHARACTERISTIC = "00001923-a838-484d-92ee-a8fc2079c3a1"
DESC_UUID_WARMUP2 = "00001930-a838-484d-92ee-a8fc2079c3a1"
DESC_UUID_WARMUP1 = "00001929-a838-484d-92ee-a8fc2079c3a1"
DESC_UUID_NAME = "00001927-a838-484d-92ee-a8fc2079c3a1"
DESC_UUID_UNIT = "00001926-a838-484d-92ee-a8fc2079c3a1"
DESC_UUID_ACTIVATION = "00001924-a838-484d-92ee-a8fc2079c3a1"


class Server_Manager(object):
    addr = "212.227.175.162"
    port = 8890

    def __init__(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            print(f"Error: socket error accured!\n {e}")

    # def connect(self):
    #     try:
    #         self.socket.connect((self.addr, self.port))
    #         print(f"socket connected {self.addr}:{self.port}")
    #     except Exception as e:
    #         print(f"connection error!\n {e}")

    def send(self, data_dict):
        try:
            data_dict["LABEL"] = "DRONE_EXP"
            json_obj = json.dumps(data_dict)
            # self.socket.connect((self.addr, self.port))
            self.socket.sendto(json_obj.encode(), (self.addr, self.port))
            print(f"Success! data sent to the server {self.addr}:{self.port}")
        except e as Exception:
            print(f"data sending error!\n {e}")

    def close(self):
        self.socket.close()
        print("scoket closed!")


class BLE_Sensor:
    def __init__(self, label):
        self.label = label
        self.gatt_data = {
            "value_char": None,
            "name_descriptor": None,
            "unit_descriptor": None,
            "warmup1_descritpor": None,
            "warmup2_descriptor": None,
            "activation_descriptor": None,
        }
        self.sensor_values = {
            "raw": None,
            "float_value": None,
            "timestamp": None,
            "name": None,
            "unit": None,
            "warmup1": None,
            "warmup2": None,
            "activated": None,
        }


sensor1 = BLE_Sensor("sensor1")
sensor2 = BLE_Sensor("sensor2")

server_manager = Server_Manager()


# LOG_NAME = "measurements_log.txt"

now = datetime.now().isoformat(" ", "seconds")
log_name = now.replace(":", "-")
log_name = "Measurement " + log_name + ".txt"
LOG_NAME = log_name


def is_sensor_error(value):
    if (
        value[1] == 0xFF
        and value[2] == 0xFF
        and value[3] == 0xFF
        and value[4] == 0xFF
        and value[5] == 0xFF
        and value[6] == 0xFF
    ):
        return True
    else:
        return False


# Float aus Daten erhalten
def data_to_float(data):
    # def data_to_float(data,anz=1):
    # print("data ",data.hex())
    # start = (anz*3)+(anz-1)
    start = 3
    # print("start ",start)
    # print("data ", data[2:3].hex())
    # print("data ", data[3:7].hex())
    fl = struct.unpack("!f", data[start : start + 4])[0]

    return fl


def to_fix_percision(float_num, percision=4):
    return float(int(float_num * (10**percision))) / (10**percision)


def remove_trailing_empty_space(stringVal):
    stringVal = re.sub(r"\s+$", "", stringVal)
    return stringVal


### BLE stuff
class BLEDevice(Device):
    def __init__(self, mac_address, manager, managed=True):
        super().__init__(mac_address, manager, managed)

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print(f"[{self.mac_address}] Connection failed: {str(error)}")

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print(f"[{self.mac_address}] Disconnected! try to connect again!")
        self.connect()

    def services_resolved(self):
        super().services_resolved()
        counter = 0

        print(f"[{self.mac_address}] Resolved services")
        for service in self.services:
            print(f"[{self.mac_address}]  Service [{service.uuid}]")
            for characteristic in service.characteristics:
                print(f"[{self.mac_address}]  Characteristic [{characteristic.uuid}]")
                if characteristic.uuid == CHARACTERISTIC:
                    print(f"==================SENSOR num{counter} Descritpors==================")
                    sensor = sensor1 if counter == 0 else sensor2 if counter == 1 else None
                    if sensor:
                        sensor.gatt_data["value_char"] = characteristic
                    counter += 1
                    for descriptor in characteristic.descriptors:
                        print(f"[{self.mac_address}]\t\t\tDescriptor [{descriptor.uuid}]")
                        sensor = sensor1 if counter == 1 else sensor2 if counter == 2 else None
                        if sensor:
                            if descriptor.uuid == DESC_UUID_NAME:
                                sensor.gatt_data["name_descriptor"] = descriptor
                                try:
                                    name = descriptor.read_value()
                                    nameStr = "%s" % "".join([str(v) for v in name])
                                    nameStr = remove_trailing_empty_space(nameStr)
                                    sensor.sensor_values["name"] = nameStr
                                except Exception as e:
                                    print("read name error->", e)
                                    sensor.sensor_values["name"] = "ERROR"

                            elif descriptor.uuid == DESC_UUID_UNIT:
                                sensor.gatt_data["unit_descriptor"] = descriptor
                                try:
                                    unit = descriptor.read_value()
                                    unitStr = "%s" % "".join([str(v) for v in unit])
                                    unitStr = remove_trailing_empty_space(unitStr)
                                    # replaceing % to P becuse it could couse print problems
                                    unitStr = unitStr.replace("%", "P")
                                    sensor.sensor_values["unit"] = unitStr
                                except Exception as e:
                                    print("read unit error->", e)
                                    sensor.sensor_values["unit"] = "ERROR"

                            elif descriptor.uuid == DESC_UUID_WARMUP1:
                                sensor.gatt_data["warmup1_descriptor"] = descriptor
                                try:
                                    warmup1 = descriptor.read_value()
                                    warmup1Str = "%s" % "".join([str(v) for v in warmup1])
                                    warmup1Str = remove_trailing_empty_space(warmup1Str)
                                    sensor.sensor_values["warmup1"] = warmup1Str
                                except Exception as e:
                                    print("read warmup1 error->", e)
                                    sensor.sensor_values["warmup1"] = "ERROR"
                            elif descriptor.uuid == DESC_UUID_WARMUP2:
                                sensor.gatt_data["warmup2_descriptor"] = descriptor
                                try:
                                    warmup2 = descriptor.read_value()
                                    warmup2Str = "%s" % "".join([str(v) for v in warmup2])
                                    warmup2Str = remove_trailing_empty_space(warmup2Str)
                                    sensor.sensor_values["warmup2"] = warmup2Str
                                except Exception as e:
                                    print("read warmup2 error->", e)
                                    sensor.sensor_values["warmup2"] = "ERROR"
                            elif descriptor.uuid == DESC_UUID_ACTIVATION:
                                sensor.gatt_data["activation_descriptor"] = descriptor
                                try:
                                    activated = descriptor.read_value()
                                    sensor.sensor_values["activated"] = int(activated[0])
                                except Exception as e:
                                    print("read activated error->", e)
                                    sensor.sensor_values["activated"] = "ERROR"

            if sensor1.gatt_data["value_char"]:
                sensor1.gatt_data["value_char"].enable_notifications()

            if sensor2.gatt_data["value_char"]:
                sensor2.gatt_data["value_char"].enable_notifications()

            # print(f"""sensor name is: {value.decode("utf-8")}""")

            # if characteristic.uuid == CHARACTERISTIC:
            #     print("charactersitics discovered")
            #     characteristic.enable_notifications()

    def characteristic_enable_notifications_failed(self, characteristic, error):
        """
        Called when a characteristic notifications enable command failed.
        """
        print(f"Error enabaling the characterestic :{characteristic.uuid} failed!")

    def characteristic_enable_notifications_succeeded(self, characteristic):
        print(f"succeeded! enabaling the characterestic {characteristic.uuid}")

    def characteristic_value_updated(self, characteristic, value):
        now = datetime.now().isoformat(" ", "seconds")
        # line = f"""{now} : {value.decode("utf-8")}"""
        sensor_addr = value[0]
        ## BLE finds 2nd sensor charactrestics first so we have to assign sensor_addr 0x1 to sensor2!!!
        sensor = sensor2 if sensor_addr == 0x1 else sensor1 if sensor_addr == 0x2 else None
        if sensor is None:
            print(f"ERROR sensor addrress {value[0]} is not known! ")
            return
        # convert hex to decimal make it easier to send it via json
        sensor.sensor_values["raw"] = [int(v) for v in value]
        sensor.sensor_values["timestamp"] = time.time()

        error = is_sensor_error(value)
        if error:
            print(f"Sensor Erorr detected on addr {value[0]}")
            return

        float_val = data_to_float(value)
        float_val = to_fix_percision(float_val)
        sensor.sensor_values["float_value"] = float_val
        hex_raw = [hex(v) for v in sensor.sensor_values["raw"]]

        line = f"""{now} : gas_name: {sensor.sensor_values["name"]}, float_val: {sensor.sensor_values["float_value"]} {sensor.sensor_values["unit"]}, hex_raw: {hex_raw}"""

        server_manager.send(sensor.sensor_values)
        last_idx = line.find("%")
        if last_idx == -1:
            last_idx = len(line) - 1
        line = line[0 : last_idx + 1]
        print(line)

        # try:
        #    with open(LOG_NAME, "a") as f:
        #        f.write(line)
        #        f.write("\n")
        # except Exception as e:
        #    print("no previous log file exist! ")
        #    print("Creating new log file")
        #    with open(LOG_NAME, "w") as f:
        #        f.write(line)
        #        f.write("\n")

        # f.close()


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    try:
        # print("connecting to the server ...")
        # server_manager.connect()
        print("Connecting...")
        manager = DeviceManager(adapter_name="hci0")
        device = BLEDevice(manager=manager, mac_address=MAC)
        device.connect()
        manager.run()
    except KeyboardInterrupt:
        pass


# raw: array[9]
# float_value: 22.1
# timestamp: 1675708197.0268102
# name: "O2"
# unit: "VolP"
# warmup1: "0 Minutes"
# warmup2: "0 Minutes"
# activated: 1
# LABEL: "DRONE_EXP"
