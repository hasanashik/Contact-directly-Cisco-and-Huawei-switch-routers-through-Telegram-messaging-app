import telebot 
import requests
from bs4 import BeautifulSoup
import re

from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect

def find_model(net_connect,cmd):
    #send_command("show whatever", delay_factor=2)
    output = net_connect.send_command(cmd)    
    return output

def try_connect(src_ip,router):
    #print('Connecting with ',src_ip)
    net_connect = ConnectHandler(**router)
    device_prompt = net_connect.find_prompt()
    #print(device_prompt)
    
    if '#' in device_prompt:
        device_type = 'cisco'
    elif '>' in device_prompt:
        device_type = 'huawei'
    else:
        device_type = 'none'
    
    return net_connect,device_type,device_prompt

def make_connect(src_ip):
    router = {
        'device_type': 'autodetect',
        'host':   src_ip,
        'username': 'username1',
        'password': 'password1',
        'port' : 22,         
        'secret': '',    
    }
    device_type = ''
    device_prompt = ''
    net_connect = ''
    error_message = ''
    connect_success = 0

    try:
        net_connect,device_type,device_prompt = try_connect(src_ip,router)
        connect_success = 1
    except Exception as e:
        connect_success = 0
        error_message = error_message + str(e) + '\n\n\n'
        

    if connect_success == 0:
        router = {
            'device_type': 'cisco_xr',
            'host':   src_ip,
            'username': 'username2',
            'password': 'password2',
            'port' : 22,         
            'secret': '',    
        }
        try:
            net_connect,device_type,device_prompt = try_connect(src_ip,router)
            connect_success = 1
        except Exception as e:
            connect_success = 0
            error_message = error_message + str(e) + '\n\n\n'

    if connect_success == 0:
        router = {
            'device_type': 'huawei',
            'host':   src_ip,
            'username': 'username3',
            'password': 'password3',
            'port' : 22,         
            'secret': '',    
        }
        try:
            net_connect,device_type,device_prompt = try_connect(src_ip,router)
            connect_success = 1
        except Exception as e:
            connect_success = 0
            error_message = error_message + str(e) + '\n\n\n'
    
    if connect_success == 0:
        router = {
            'device_type': 'autodetect',
            'host':   src_ip,
            'username': 'username4',
            'password': 'password4',
            'port' : 22,         
            'secret': '',    
        }
        try:
            net_connect,device_type,device_prompt = try_connect(src_ip,router)
            connect_success = 1
        except Exception as e:
            connect_success = 0
            error_message = error_message + str(e) + '\n\n\n'
    
    return net_connect,device_type,device_prompt, error_message


def give_me_optical_power(src_ip,int_name):
    device_version_cmd_cisco = 'show version'
    device_version_cmd_huawei = 'display version'
    error_message = ''
    version = ''
    output_power = ''

    net_connect,device_type,device_prompt, error_message = make_connect(src_ip)
    #print(device_type,device_prompt,error_message)
    if net_connect:
        if device_type == 'cisco':
            net_connect.send_command('terminal length 0')
            version = find_model(net_connect,device_version_cmd_cisco)
        elif device_type == 'huawei':
            net_connect.send_command('screen-length 0 temporary')
            version = find_model(net_connect,device_version_cmd_huawei)
            #print(version)
        else:
            print('Not correct device_type. ',device_type)
            version = ''

        if 'Cisco A901-12C-F-D' in version or 'Cisco A901-12C-FT-D' in version or 'Cisco A901-6CZ-F-A' in version or 'Cisco A901-6CZ-F-D' in version or 'Cisco A901-6CZ-FT-D' in version or 'cisco ME-3400-24FS-A' in version or 'cisco ME-3400-24TS-A' in version or 'cisco ME-3800X-24FS-M' in version or 'cisco WS-C2960-24TC-L' in version or 'cisco WS-C2960-24TC-S' in version :
            #print('type 1')
            type1_power_cmd = 'sh int '+ str(int_name)+' transceiver | b Optical'
            type1_power_cmd_output = net_connect.send_command(type1_power_cmd)
            #print(type1_power_cmd_output)
            output_power = type1_power_cmd_output
        elif 'cisco ASR-902 (RSP2)' in version or 'cisco ASR-903 (RSP1)' in version or 'cisco ASR-903 (RSP2)' in version or 'cisco ASR-920-12CZ-D' in version or 'cisco ASR-920-24SZ-IM' in version or 'cisco ASR-920-24SZ-M' in version or 'cisco ASR-920-8S4Z-PD' in version:
            #print('type 2')
            pattern = r'\/'
            int_name_splitted = re.split(pattern, int_name)
            #['Gi 0', '0', '1']
            pattern = r'\d+'
            int_name_splitted_first_digit = re.findall(pattern, int_name_splitted[0])
            #['0']
            type2_power_cmd = 'sh hw-module subslot ' + str(int_name_splitted_first_digit[0])+'/'+str(int_name_splitted[1]) + ' transceiver '+str(int_name_splitted[2]) + ' status | i dBm'
            #sh hw-module subslot 0/1 transceiver 1 status | i dBm
            type2_power_cmd_output = net_connect.send_command(type2_power_cmd)
            #print(type2_power_cmd_output)
            output_power = type2_power_cmd_output
        elif 'cisco N540X-6Z18G-SYS-D' in version or 'cisco NCS-540' in version or 'cisco NCS-5500 ' in version:
            #print('type 3')
            type3_power_cmd = 'sh controllers '+ str(int_name)+' phy  | i x Power:'
            type3_power_cmd_output = net_connect.send_command(type3_power_cmd)
            #print(type3_power_cmd_output)
            output_power = type3_power_cmd_output
        elif 'HUAWEI ATN 910B-F DC' in version or 'HUAWEI NE40E-M2K' in version or 'HUAWEI NE40E-X8A' in version or 'HUAWEI NetEngine 8000 M8' in version or 'HUAWEI NE20E-S2F' in version or 'HUAWEI NE40E-X3A' in version:
            #print('type 4')
            #display interface phy-option GigabitEthernet 0/3/32 | i x Power:
            type4_power_cmd = 'display interface phy-option '+ str(int_name) + ' | i x Power:'
            type4_power_cmd_output = net_connect.send_command(type4_power_cmd)
            type4_power_cmd_output = str(type4_power_cmd_output).split('CTRL_C to break.')[1]
            #print(type4_power_cmd_output)
            output_power = type4_power_cmd_output
        elif 'HUAWEI CE6865-48S8CQ-EI' in version:
            #print('type 5')
            #display interface 100GE1/0/4 transceiver brief
            type5_power_cmd = 'display interface  '+ str(int_name)+' transceiver brief '
            #print(type5_power_cmd)
            type5_power_cmd_output = net_connect.send_command(type5_power_cmd)
            #print(type5_power_cmd_output)
            output_power = type5_power_cmd_output
        elif 'HUAWEI S2320-28TP-EI-AC Routing Switch' in version or 'HUAWEI S5300-28X-LI-24S-AC Routing Switch' in version or 'HUAWEI S5320-32X-EI-24S-AC Routing Switch' in version or 'HUAWEI S5320-32X-EI-24S-DC Routing Switch' in version or 'HUAWEI S5320-32X-EI-DC Routing Switch' in version or 'HUAWEI S5720S-28X-LI-24S-AC Routing Switch' in version or 'HUAWEI S6320-30C-EI-24S-DC Routing Switch' in version or 'HUAWEI S6320-50L-HI-48S Routing Switch' in version or 'HUAWEI S6720-30C-EI-24S-AC Routing Switch' in version or 'Quidway S2318TP-EI Routing Switch' in version or 'Quidway S3328TP-EI-24S Routing Switch' in version or 'Quidway S3328TP-SI Routing Switch' in version or 'Quidway S3700-28TP-EI-24S-AC Routing Switch' in version or 'Quidway S5328C-EI-24S Routing Switch' in version:
            #print('type 6')
            #display transceiver diagnosis interface GigabitEthernet 0/0/5
            type6_power_cmd = 'display transceiver diagnosis interface '+ str(int_name)+''
            #print(type6_power_cmd)
            type6_power_cmd_output = net_connect.send_command(type6_power_cmd)
            #print(type6_power_cmd_output)
            output_power = type6_power_cmd_output
        elif 'cisco ASR9K' in version:
            #print('type 7')
            type7_power_cmd = 'sh controllers '+ str(int_name)+' phy  | i dBm'
            type7_power_cmd_output = net_connect.send_command(type7_power_cmd)
            #print(type7_power_cmd_output)
            output_power = type7_power_cmd_output
        elif 'HUAWEI NE05E-SE' in version:
            #print('type 8')
            type8_power_cmd = 'display interface phy-option '+ str(int_name) + ' | i l Power:'
            type8_power_cmd_output = net_connect.send_command(type8_power_cmd)
            #print(type8_power_cmd)
            output_power = type8_power_cmd_output
        else:
            #print('Unknown device version.')
            output_power = 'Unknown device version.'

        net_connect.disconnect()

    else:
        #print('Could not connect.  Check SSH connection.')
        output_power = 'Could not connect.  Check SSH connection.'
    
    return output_power



def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def main() -> None:
    TOKEN = 'YOUR_TOKEN_FOUND_FROM_BOTFATHER'
    bot = telebot.TeleBot(TOKEN, parse_mode=None)


    @bot.message_handler(func=lambda message: True)
    def proccess_scr(message):
        print(message.chat.id,type(message.chat.id) )
        msg = message.text
        msg = "".join(str(msg).split())
        msg_split = msg.split(",")
        
        if message.chat.id == YOUR_TELEGRAM_CHAT_ID:
            #bot.reply_to(message, "Authorised user.")
            if validate_ip(msg_split[0]) and ',' in msg:
                #print(msg_split[0],msg_split[1])
                optical_power = give_me_optical_power(msg_split[0],msg_split[1])
                bot.reply_to(message, optical_power)
            else:
                #print('You have entered wrong SCR/ ip port format.')
                bot.reply_to(message, "You have entered wrong SCR/ ip port format.")
        else:
            bot.reply_to(message, "Unauthorised user. Your info will be reported to Admin.")

    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
