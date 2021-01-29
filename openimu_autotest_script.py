"""
Aceinna OpenIMU auto test tool
Based on PySerial https://github.com/pyserial/pyserial
Created on 2020-10-10
@author: YiFan.Li
"""

import time
import sys
import os
import csv
import json
import serial
import serial.tools.list_ports
from openimu import OpenIMU
from commands import OpenIMU_CLI
import pandas as pd

atimu = OpenIMU(ws=False)

# go throuth the checklist before release to customer
class AutoTest:
    def __init__(self):
        self.command = "  "
        self.input_string = []        # define input_string

        os.chdir(os.path.split(os.path.realpath(__file__))[0])
        with open('setting_config.json') as json_data:
        # Load the auto_checklist.json on each request to support dynamic debugging
                    self.checklist_handler = json.load(json_data) 
        # file_path = os.path.dirname(os.getcwd())
        if not os.path.exists("auto_test_log"):
                    print("Create auto test log file/ ")
                    os.makedirs("auto_test_log")
                    self.outputFile = open('auto_test_log/output.csv', 'w', newline='')
        else:
            self.outputFile = open('auto_test_log/output.csv', 'w', newline='')  
        self.outputWriter = csv.writer(self.outputFile)
        # check report format
        self.outputWriter.writerow(['check items','reference value','check value','result'])
        self.item_properties = self.checklist_handler['CheckItem']
        self.firmware_bin_name = self.checklist_handler['Firmware_name']["new_release_bin"]
        
        
    def check_module_name(self):
        data = atimu.openimu_get_device_id()
        data = data.split(' ')[0]
        refv = self.item_properties[0]['reference value']
        reff = self.item_properties[0]['function']
        rslt = 'pass' if refv in data else 'fail'

        return (reff,refv,data,rslt)

    def check_part_number(self):
        data = str(atimu.openimu_get_device_id())
        data = data.split(' ')[1]
        refv = self.item_properties[1]['reference value']
        reff = self.item_properties[1]['function']
        rslt = 'pass' if  refv in data else 'fail'
        return (reff,refv,data,rslt)

    def check_fw_version(self):
        data = str(atimu.openimu_get_device_id())
        data = data.split(' ')[2]
        refv = self.item_properties[2]['reference value']
        reff = self.item_properties[2]['function']
        rslt = 'pass' if refv in data else 'fail'

        return (reff,refv,data,rslt)

    def check_SN_number(self):
        data = str(atimu.openimu_get_device_id())
        data = data.split(sep=' ',maxsplit=-1)[3]
        data = data.split(sep=':')[1]
        refv = self.item_properties[3]['reference value']
        reff = self.item_properties[3]['function']
        rslt = 'pass' if refv in data else 'fail'

        return (reff,refv,data,rslt)

    def check_default_baud_rate(self):
        data = str(atimu.openimu_get_param(2)['value'])
        refv = self.item_properties[4]['reference value']
        reff = self.item_properties[4]['function']
        rslt = 'pass' if data == refv else 'fail'

        return (reff,refv,data,rslt)

    def check_packet_rate_ODR(self):
        data = str(atimu.openimu_get_param(4)['value'])
        refv = self.item_properties[5]['reference value']
        reff = self.item_properties[5]['function']
        rslt = 'pass' if data == refv else 'fail'

        return (reff,refv,data,rslt)

    def check_packet_type(self):
        data = atimu.openimu_get_param(3)['value'][0:2]
        refv = self.item_properties[6]['reference value']
        reff = self.item_properties[6]['function']
        rslt = 'pass' if data == refv else 'fail'

        return (reff,refv,data,rslt)

    def check_acc_lpf(self):
        data = str(atimu.openimu_get_param(5)['value'])
        refv = self.item_properties[7]['reference value']
        reff = self.item_properties[7]['function']
        rslt = 'pass' if data == refv else 'fail'

        return (reff,refv,data,rslt)

    def check_gyro_lpf(self):
        data = str(atimu.openimu_get_param(6)['value'])
        refv = self.item_properties[8]['reference value']
        reff = self.item_properties[8]['function']
        rslt = 'pass' if data == refv else 'fail'

        return (reff,refv,data,rslt)      

    def check_default_orientation(self):
        data = atimu.openimu_get_param(7)['value'][1:6]
        refv = self.item_properties[9]['reference value'][1:6]
        reff = self.item_properties[9]['function']
        rslt = 'pass' if data == refv else 'fail'

        return (reff,refv,data,rslt)

    def check_firmware_update(self):
        '''upgrade firmware upgrade by firwarm bin file name XX.bin
        '''
        # user should change the upgrade bin file name accordingly
        file_name = self.firmware_bin_name
        if atimu.openimu_upgrade_fw_prepare(file_name) == True:
            while not atimu.openimu_finish_upgrade_fw():
                atimu.openimu_upgrade_fw(file_name)

        print("update firmware success! reset the openimu300 unit!")
        self.outputWriter.writerow(['check_firmware_update',file_name,file_name,'pass'])
        atimu.openimu_start_app()
        return True

    def check_all_register_map(self):
        # TODO:
        return True

    def basic_fw_check(self):
        atimu.find_device()

        # com = OpenIMU_CLI()
        # com.connect_handler()

        print("************check start*************")

        time.sleep(0.8)
        for x in range(len(self.item_properties)):
            get_msg = eval('self.%s()'%(self.item_properties[x]["function"]))
            self.outputWriter.writerow([get_msg[0],get_msg[1],get_msg[2],get_msg[3]])
            print("{0} {1} {2} {3}".format(get_msg[0],get_msg[1],get_msg[2],get_msg[3]))
        time.sleep(0.1)
        # self.check_firmware_update()
        time.sleep(0.8) # wait for the initialize process
        for x in range(len(self.item_properties)):
            get_msg = eval('self.%s()'%(self.item_properties[x]["function"]))
            self.outputWriter.writerow([get_msg[0],get_msg[1],get_msg[2],get_msg[3]])
            print("{0} {1} {2} {3}".format(get_msg[0],get_msg[1],get_msg[2],get_msg[3]))

        print("************check end***************")

        self.outputFile.close() # close csv
        return True


    def test_command_handler(self):
        # TODO:
        return True



#####       
if __name__ == "__main__":
    dostep = AutoTest()
    dostep.basic_fw_check()

