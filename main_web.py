import sys  # sys нужен для передачи argv в QApplication
import os
import re
import pandas as pd
import numpy as np
from datetime import datetime, date, time
import time as ttime

import  subprocess
import logging
import paramiko
import socket
import json
from celery_progress.backend import ProgressRecorder

from .my_ssh import ssh_conf
from .global_report_24 import rep_from_test_res  # файл с функциями построения отчета
from .test_json_to_txt import my_reports  # файл с функциями построения форматированного текстового отчета

class BackTestApp():

#    server_directory = '/home/murd/buf/ft_userdata/'
#    server_directory = '/root/application'
#    server_strategy_directory = '/user_data/strategies/'
#    server_backtests_directory = '/user_data/backtest_results/'
#    server_reports_directory = '/reports/'
#    server_user_directory = 'My_backtest_results' #'admin_dir'
#    client_directory = ''
#    reports_directory = './reports/'

    # Информация о сервере, имя хоста (IP-адрес), номер порта, имя пользователя и пароль

#    hostname = "172.18.90.46"
#    port = 2222
#    username = "murd"
#    password = "Ambaloid!"

#    hostname = "gate.controller.cloudlets.zone"
#    hostname = "node7441-ft-stable.node.cloudlets.zone"
#    hostname = "212.127.94.1"
#    port = 3022
#    username = "7441-732"

    version = 2.2

    hostname = ssh_conf.hostname
    port = ssh_conf.port
    username = ssh_conf.username

    server_directory = ssh_conf.server_directory
    server_strategy_directory = ssh_conf.server_strategy_directory
    server_backtests_directory = ssh_conf.server_backtests_directory
    server_reports_directory = ssh_conf.server_reports_directory
    local_reports_directory = ssh_conf.local_reports_directory
    server_user_directory = ssh_conf.server_user_directory
    client_directory = ssh_conf.client_directory    

    list_info = []

    num_try = 3
    bar_len = 100
    one_percent = 1
    cur_progress = 0

    my_txt_rep = my_reports()   #создаем объект нашего собственного класса my_reports()
        
    my_rep = rep_from_test_res() #создаем объект нашего собственного класса rep_from_test_res()


    def delete_tests(self, f_path, delete_list):
        #print(results_path)
        #list_dir = .listdir(path=results_path)
        #print('Existed: ', f_path + delete_list)
        for del_item in delete_list:
            del_item = str(del_item)
              
            try:
              print('Locked for: ', f_path + del_item)
              if os.path.exists(f_path + del_item):
                  print('Existed: ', f_path + del_item)
                  os.remove(f_path + del_item)
                  self.list_info.append("Deleted file: " + del_item)
            except:
              self.list_info.append("Can't delete file: " + del_item)
            finally:   
              self.list_info.append('________________________________________') 
        
        return 'Ok'
    
    def delete_results(self, user_name, delete_list):

        for i in range(self.num_try):
            client = self.get_ssh_connect()    #создаем ssh-подключение
            if client != 'error':
                sftp_client = client.open_sftp()
                
                break
            else:
                self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (connect_ssh)")
                self.list_info.append('________________________________________')
                return
            
        results_path = '/' + self.server_directory + self.server_backtests_directory +user_name + '/'
        try:
#          print(results_path)
          list_dir = sftp_client.listdir(path=results_path)
          
          for del_item in delete_list:
              del_item = str(del_item)
              
              splited_str = del_item.split('.')
              
              del_name = splited_str[0]
              
              for file_name in list_dir:
                 file_name = file_name.strip('\n')
                 splited_str = file_name.split('.')
                
                 if len(splited_str) >= 1:
                     
                     if splited_str[0] == del_name:
                         try:
                            sftp_client.remove(results_path+file_name)
                            self.list_info.append("Deleted file: " + file_name)
                         except:
                             self.list_info.append("Can't delete file: " + file_name)
        except:
           self.list_info.append("Can't complite deleting!")
        finally:   
           self.list_info.append('________________________________________') 
            
        sftp_client.close()
        client.close()
        return 'Ok'
    
    def get_ssh_connect(self, show_info = True):

        logger = paramiko.util.logging.getLogger()
        hdlr = logging.FileHandler('app.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)

         # Создать объект SSH
        if show_info: 
            self.list_info.append("Runing SSH...")
            self.list_info.append("Host name: " + self.hostname )
            self.list_info.append("Port: " + str(self.port))
        try:        
            client = paramiko.SSHClient()
         # Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.RSAKey.from_private_key_file('RSA_private_1.txt')
         # подключиться к серверу
        
#            client.connect(self.hostname, self.port, self.username, self.password, compress=True)
            client.connect(self.hostname, self.port, self.username, pkey=private_key, timeout=3, disabled_algorithms=dict(pubkeys=['rsa-sha2-256', 'rsa-sha2-512']))
                        
        except Exception as e:
            logging.debug(e)
            self.list_info.append('Error connection to server: ' + str (e) )
            #self.listInfo.addItem("Invalid login/password!")
            self.list_info.append('________________________________________')
            return 'error'
            
        else:
            if show_info:
                self.list_info.append("Connected to server!" + '\n')
                self.list_info.append('________________________________________' + '\n')

        return client

    def get_sftp_connect(self):

        logger = paramiko.util.logging.getLogger()
        hdlr = logging.FileHandler('app.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)

        try:
#        self.server_directory ='/home/murd/buf/ft_userdata'
            private_key = paramiko.RSAKey.from_private_key_file('RSA_private_1.txt')
            transport = paramiko.Transport((self.hostname, self.port))
            transport.connect(username = self.username, pkey = private_key)
        
            sftp = paramiko.SFTPClient.from_transport(transport)    
            
        except Exception as e:
            logging.debug(e)
            self.list_info.append('Error connection to server (sftp): ' + str (e) + '\n')
            #self.listInfo.addItem("Invalid login/password!")
            self.list_info.append('________________________________________' + '\n')
            return 'error'
            
        else:
            self.list_info.append("Connected to server (sftp)!" + '\n')
            self.list_info.append('________________________________________' + '\n')

        return sftp

    def connect_ssh(self):
        
        # На случай, если в списке уже есть элементы
        list_backtest = []
        list_strategies = []
        
        max_bytes=60000

#        self.username = self.lineEdit_Login.text()
#        self.password = self.lineEdit_Password.text()
       
        for i in range(self.num_try):
            client = self.get_ssh_connect() #создаем ssh-подключение
            if client != 'error':
                sftp_client = client.open_sftp()
                current_dir = sftp_client.getcwd()
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (get_strategy)")
            self.list_info.append('________________________________________')
            #print('info: ', self.list_info)
            return list_strategies, list_backtest
                
        
        #Проверяем наличие, на сервере, полльзователького каталога, если такго не существует - создаем
        try:
            sftp_attributes = sftp_client.stat(self.server_directory + self.server_backtests_directory+self.server_user_directory)
        except Exception as e:
#            self.listInfo.addItem('Error connection to server: ' + str (e))
            sftp_client.mkdir(self.server_directory + self.server_backtests_directory+self.server_user_directory)
            self.list_info.append("Created user directory: " + self.server_user_directory + '\n')

        try:
            sftp_attributes = sftp_client.stat(self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory)
        except Exception as e:
            sftp_client.mkdir(self.server_directory + self.server_backtests_directory + self.server_user_directory + self.server_reports_directory)
            self.list_info.append("Created user report directory: " + self.server_user_directory + self.server_reports_directory + '\n')

         # Выполнить команду linux
        command = 'ls /' + self.server_directory + self.server_strategy_directory
        
        stdin, stdout, stderr = client.exec_command(command)

        for file_name in stdout:  # для каждого файла в директории
            file_name = file_name.strip('\n')
            splited_str = file_name.split('.')
            if len(splited_str) == 2:
               if splited_str[1] == 'py':
                  splited_str2 = splited_str[0].split('_')
                  if splited_str2[0] in ['min']:
                     list_strategies.append(file_name) # добавить файл в listStrategies


        command = 'ls /' + self.server_directory + self.server_backtests_directory + self.server_user_directory
        
        stdin, stdout, stderr = client.exec_command(command)
        for file_name in stdout:  # для каждого файла в директории
            file_name = file_name.strip('\n')
            if file_name != '.last_result.json':
               splited_str = file_name.split('.')
               if len(splited_str) == 2:
                  if splited_str[1] == 'json': 
                     list_backtest.append(file_name)   # добавить файл в listBtResults

        
        sftp_client.close()
        client.close()
        #print('info: ', self.list_info)
        return list_strategies, list_backtest
            
    def get_strategy(self, f_name: str):

        for i in range(self.num_try):
            client = self.get_ssh_connect(show_info = False) #создаем ssh-подключение
            if client != 'error':
                sftp_client = client.open_sftp()
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (get_strategy)")
            self.list_info.append('________________________________________')
            return 'error'

        try:
            remote_file = sftp_client.open (self.server_directory + self.server_strategy_directory + f_name) # Путь к файлу
            strategy_name = 'none'
            for line in remote_file:
                line = line.strip()
                if ('class' in line) and ('IStrategy' in line):
                    pars_str1 = line.split()
                    pars_str = pars_str1[1].split('(') #re.split(' |()', line)
                    strategy_name = pars_str[0]
                    
                    self.list_info.append("Strategy name: ")
                    self.list_info.append(strategy_name)
                    self.list_info.append('________________________________________')
                    
        finally:
            remote_file.close()

        client.close()
        #print('strategy_name: ', strategy_name)
        return strategy_name

    def run_report(self, backtest_file_name, mode, user_name):

        self.list_info = []
        
        self.server_user_directory = user_name
#        my_txt_rep = my_reports()   #создаем объект нашего собственного класса my_reports()
        
#        my_rep = rep_from_test_res() #создаем объект нашего собственного класса rep_from_test_res()
        if mode == 'local':
            if not os.path.exists("./reports/" + user_name + "/"):
                os.mkdir("reports/" + user_name)
                os.mkdir("reports/" + user_name + "/txt")
                os.mkdir("reports/" + user_name + "/xlsx")
                self.list_info.append("Created directory: /reports/" + user_name)
                
            f_path = './reports/' + user_name + '/xlsx/'
            if not os.path.exists(f_path):
                os.mkdir(f_path)
                self.list_info.append("Created directory: " + f_path)
                
            f_path = './reports/' + user_name + '/txt/'
            if not os.path.exists(f_path):
                os.mkdir(f_path)
                self.list_info.append("Created directory: " + f_path)
                
        for i in range(self.num_try):
            client = self.get_ssh_connect() #создаем ssh-подключение
            if client != 'error':
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (get_strategy)")
            self.list_info.append('________________________________________')
            return 'error'

            
        print('Rep-start!')    
        if client != 'error':
            sftp = client.open_sftp()
            remote_file = sftp.open ('/' + self.server_directory + self.server_backtests_directory +self.server_user_directory + '/' + backtest_file_name, mode = 'r') # Путь к файлу results
            json_obj = json.loads(remote_file.read())
            
            self.list_info.append("Creating report, please wait... ")
            buf_str = backtest_file_name.split('.')
            
            print('/' + self.server_directory + self.server_backtests_directory +self.server_user_directory + '/' + buf_str[0] + '.conf')
            conf_part = sftp.open ('/' + self.server_directory + self.server_backtests_directory +self.server_user_directory + '/' + buf_str[0] + '.conf', mode = 'r') # Путь к файлу config
            conf_obj = []
            for line in conf_part:
                conf_obj.append(line.strip().strip('\n'))
            
            if mode == 'local':
              res_report = self.my_txt_rep.json_to_txt(json_obj, conf_obj, remote_file, mode, self.local_reports_directory + user_name + '/txt/', backtest_file_name)
            else:
                remote_file = sftp.open ('/' + self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory +buf_str[0] + '.txt', mode = 'w') # Путь к файлу
                res_report = self.my_txt_rep.json_to_txt(json_obj, remote_file, mode, self.server_reports_directory, backtest_file_name)
            self.list_info.append("Created report: ")
            self.list_info.append(buf_str[0] + '.txt')
            
            res_report = self.my_rep.get_report(json_obj, mode, user_name, self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory, backtest_file_name)
            if res_report == 'unknown series len (N)':
                self.list_info.append("Unknown series len (N). Probably an imported strategy.")
            else:
                if res_report == "no_trades":
                    self.list_info.append("Created report error: No trades in test results!")
                else:
                    self.list_info.append("Created report: ")
                    self.list_info.append(backtest_file_name.split('.')[0]+'_t1.xlsx')
            self.list_info.append('________________________________________')
            rep_done =True
            sftp.close()
            for val_ls in self.list_info:
                print(val_ls)
        else:
            return 'error'
        

        return rep_done

    def run_backtest(self, user_strategy_settings, user_name):

        self.list_info = []
        
        self.server_user_directory = user_name
        buf_str = self.get_strategy(user_strategy_settings["f_strategies"])
        file_config = 'usr_' + buf_str + '_config.py'
        max_bytes=160000
        short_pause=1
        long_pause=5
        
        if buf_str != 'none':
            datadir = " --datadir user_data/data/binance "
            export = " --export trades "
            config = " --config user_data/config_p" + user_strategy_settings["f_parts"] + ".json "
            print(user_strategy_settings["f_start_data"])
            print(user_strategy_settings["f_stop_data"])
            #start_d = datetime.strptime(user_strategy_settings["f_start_data"].split('T')[0], '%Y-%m-%d')
            #stop_d = datetime.strptime(user_strategy_settings["f_stop_data"].split('T')[0], '%Y-%m-%d')
            start_d = user_strategy_settings["f_start_data"].split('T')[0].replace('-', '')
            stop_d = user_strategy_settings["f_stop_data"].split('T')[0].replace('-', '')
            print(start_d)
            print(stop_d)
            print('Timeframe: ', user_strategy_settings["f_timeframe"])
            time_range = " --timerange=" + start_d.strip('-') + "-" + stop_d.strip('-')
            max_open_trades = ' --max-open-trades ' + str(user_strategy_settings["f_max_open_trades"])
            if user_strategy_settings["f_series_len"] > 0:
                export_filename = " --export-filename user_data/backtest_results/" + self.server_user_directory + "/bc_" + str(user_strategy_settings["f_series_len"]) +'_p' + user_strategy_settings["f_parts"]+ '_' + buf_str + '.json'
                res_path = "user_data/backtest_results/" + self.server_user_directory + "/bc_" + str(user_strategy_settings["f_series_len"]) +'_p' + user_strategy_settings["f_parts"]+ '_' + buf_str 
            else:
                export_filename = " --export-filename user_data/backtest_results/" + self.server_user_directory + "/bc_0" +'_p' + user_strategy_settings["f_parts"]+ '_' + buf_str + '.json'
                res_path = "user_data/backtest_results/" + self.server_user_directory + "/bc_0" +'_p' + user_strategy_settings["f_parts"]+ '_' + buf_str

            strategy = " -s "+ buf_str
            
            run_str = "docker-compose run --rm freqtrade backtesting " + datadir + export + config + time_range + max_open_trades + export_filename + strategy + ' -i ' + user_strategy_settings["f_timeframe"]
            print(run_str)
            self.list_info.append('Command line for run test:')
            self.list_info.append(run_str)
            self.list_info.append('________________________________________')
        else:
            self.list_info.append('Strategy name not found!!!')
            self.list_info.append('________________________________________')

        # Minimal ROI designed for the strategy.
        not_first = False
        print(user_strategy_settings)
        
        buf_str = '# Test data range'
        strategy_settings = pd.Series([buf_str])
        buf_str = '    start_data = ' + start_d
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    stop_data = ' + stop_d
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    timeframe = ' + "'" + user_strategy_settings["f_timeframe"] + "'"
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '    minimal_roi = { '
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        
        if user_strategy_settings["f_min_roi_value1"] > 0:
            buf_str = '        "' + str(user_strategy_settings["f_min_roi_time1"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value1"])
            buf_str += ','
            strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        if user_strategy_settings["f_min_roi_value2"] > 0:
            buf_str = '        "' + str(user_strategy_settings["f_min_roi_time2"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value2"])
            buf_str += ','
            strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        if user_strategy_settings["f_min_roi_value3"] > 0:
            buf_str = '        "' + str(user_strategy_settings["f_min_roi_time3"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value3"])
            buf_str += ','
            strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        if user_strategy_settings["f_min_roi_value4"] > 0:
            buf_str = '        "' + str(user_strategy_settings["f_min_roi_time4"]) + '":  ' + self.normalyze_percents(user_strategy_settings["f_min_roi_value4"])
            strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
            
        if ((user_strategy_settings["f_min_roi_value1"] <= 0) & (user_strategy_settings["f_min_roi_value2"] <= 0) & 
           (user_strategy_settings["f_min_roi_value3"] <= 0) & (user_strategy_settings["f_min_roi_value4"] <= 0)):
            buf_str = '        "0":  10'
            strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
           

        buf_str = '    }'
        
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        if user_strategy_settings["f_series_len"] > 0:
            buf_str = '    arg_N =  ' + str(user_strategy_settings["f_series_len"])
        else:
            buf_str = '    arg_N = ' + '0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        #arg_R=0
        if user_strategy_settings["f_persent_same"] > 0:
            buf_str = '    arg_R =  ' + str(user_strategy_settings["f_persent_same"])
        else:
            buf_str = '    arg_R = ' + '0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        #- arg_P % price increase in arg_N candles
        if user_strategy_settings["f_price_inc"] != 0:
            buf_str = '    arg_P =  ' + str(user_strategy_settings["f_price_inc"])
        else:
            buf_str = '    arg_P = ' + '0.0'    
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)       
           
        #- arg_MR % movement ROI
        if user_strategy_settings["f_movement_roi"] > 0:
            buf_str = '    arg_MR =  ' + self.normalyze_percents(user_strategy_settings["f_movement_roi"])
        else:
            buf_str = '    arg_MR = ' + '0.0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        # Optimal ROI of force exit designed for the BeepBoop strategy.
        if user_strategy_settings["f_my_force_exit_time"] != 0:
            buf_str = '    my_force_exit = np.array([' + str(user_strategy_settings["f_my_force_exit_time"]) + ', '+ self.normalyze_percents(user_strategy_settings["f_my_force_exit_value"]) + '])'
        else:
            buf_str = '    my_force_exit = np.array([0, 0.0])'    
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # Optimal stoploss designed for the strategy.
        if user_strategy_settings["f_stop_loss"] != 0:
            buf_str = '    stoploss = -' + self.normalyze_percents(user_strategy_settings["f_stop_loss"])
        else:
            buf_str = '    stoploss = ' + '0.0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # Optimal time-depended stoploss designed for the strategy.
        if user_strategy_settings["f_my_stop_loss_time"] != 0:
            buf_str = '    my_stoploss = np.array([' + str(user_strategy_settings["f_my_stop_loss_time"]) + ', -'+ self.normalyze_percents(user_strategy_settings["f_my_stop_loss_value"]) + '])'
        else:
            buf_str = '    my_stoploss = np.array([0, 0.0])'    
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True) 

        #(S = desired Stop-Loss Value)
        if user_strategy_settings["f_des_stop_loss"] != 0:
            buf_str = '    arg_stoploss =  ' + self.normalyze_percents(user_strategy_settings["f_des_stop_loss"])
        else:
            buf_str = '    arg_stoploss = ' + '0.0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)

        # for MACD strategy
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '# for MACD strategy'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '    buy_cci =  ' + str(user_strategy_settings["f_buy_cci"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '    sell_cci =  ' + str(user_strategy_settings["f_sell_cci"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        #for Beep Boop strategy
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '# for Beep Boop strategy'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '    slow_len =  ' + str(user_strategy_settings["f_slow_len"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    fast_len =  ' + str(user_strategy_settings["f_fast_len"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    min_macd =  ' + str(user_strategy_settings["f_min_macd"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    ema_trend =  ' + str(user_strategy_settings["f_ema_trend"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    source = "' +(user_strategy_settings["f_source"]) + '"'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sma_source_enable =  ' + str(user_strategy_settings["f_sma_source_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sma_signal_enable =  ' + str(user_strategy_settings["f_sma_signal_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    ema_signal_enable =  ' + str(user_strategy_settings["f_ema_signal_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        if user_strategy_settings["f_series_len_beepboop"] > 0:
            buf_str = '    arg_T =  ' + str(user_strategy_settings["f_series_len_beepboop"])
        else:
            buf_str = '    arg_T = ' + '0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        # Optimal min ROI designed for the BeepBoop strategy.
        if user_strategy_settings["f_min_roi_beepboop"] != 0:
            buf_str = '    arg_min_roi = ' + self.normalyze_percents(user_strategy_settings["f_min_roi_beepboop"])
        else:
            buf_str = '    arg_min_roi = ' + '0.0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        # Optimal stoploss designed for the BeepBoop strategy.
        if user_strategy_settings["f_loss_beepboop"] != 0:
            buf_str = '    arg_max_loss = -' + self.normalyze_percents(user_strategy_settings["f_loss_beepboop"])
        else:
            buf_str = '    arg_max_loss = ' + '0.0'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        #for Smooth Scalp strategy
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '# for Smooth Scalp strategy'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '    buy_adx =  ' + str(user_strategy_settings["f_buy_adx"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_adx_enable =  ' + str(user_strategy_settings["f_buy_adx_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_adx =  ' + str(user_strategy_settings["f_sell_adx"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_adx_enable =  ' + str(user_strategy_settings["f_sell_adx_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_fastd =  ' + str(user_strategy_settings["f_buy_fastd"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_fastd_enable =  ' + str(user_strategy_settings["f_buy_fastd_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_fastd =  ' + str(user_strategy_settings["f_sell_fastd"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_fastd_enable =  ' + str(user_strategy_settings["f_sell_fastd_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_fastk =  ' + str(user_strategy_settings["f_buy_fastk"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_fastk_enable =  ' + str(user_strategy_settings["f_buy_fastk_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_fastk =  ' + str(user_strategy_settings["f_sell_fastk"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_fastk_enable =  ' + str(user_strategy_settings["f_sell_fastk_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_mfi =  ' + str(user_strategy_settings["f_buy_mfi"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    buy_mfi_enable =  ' + str(user_strategy_settings["f_buy_mfi_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_mfi =  ' + str(user_strategy_settings["f_sell_mfi"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_mfi_enable =  ' + str(user_strategy_settings["f_sell_mfi_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_cci_scalp =  ' + str(user_strategy_settings["f_sell_cci_scalp"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    sell_cci_scalp_enable =  ' + str(user_strategy_settings["f_sell_cci_scalp_enable"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        #Hyper opt
        buf_str = '#'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '# for Hyper opt'
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        buf_str = '    hyperopt =  ' + str(user_strategy_settings["f_hyperopt"])
        strategy_settings = pd.concat([strategy_settings, pd.Series([buf_str])], ignore_index = True)
        
        
#        with open(file_config, 'w') as out_file:
#            out_file.write('#  '+datetime.now().strftime('%Y-%m-%d / %H:%M:%S')+'\n \n')
#            out_file.write('import numpy as np \n')
#            out_file.write('class config_strategy(): \n')
            
            # сохранить файл конфигурации тестируемой стратегии в каталоге пользователя
#            for buf_str in strategy_settings:
#                out_file.write(buf_str+'\n')

#        out_file.close()

        
        for i in range(self.num_try):
            client = self.get_ssh_connect() #создаем ssh-подключение
            if client != 'error':
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (get_strategy)")
            self.list_info.append('________________________________________')
            
            
        if client != 'error':
            sftp_client = client.open_sftp()
            remote_file = sftp_client.open ('/' + self.server_directory + self.server_strategy_directory + file_config, mode = 'w') # Путь к файлу
            try:
                remote_file.write('#  '+datetime.now().strftime('%Y-%m-%d / %H:%M:%S')+'\n \n')
                remote_file.write('import numpy as np \n')
                remote_file.write('class config_strategy(): \n')
            
            # сохранить файл конфигурации тестируемой стратегии в каталоге пользователя
                for buf_str in strategy_settings:
                    remote_file.write(buf_str+'\n')

            finally:
                remote_file.close()
            #загрузить файл конфигурации тестируемой стратегии на сервер
#            sftp.put("./" + file_config, '/' + self.server_directory + self.server_strategy_directory + file_config)
                sftp_client.close()

        else:
            return 'error'

        self.list_info.append('Settings for current test:')
        for buf_str in strategy_settings:
            self.list_info.append(buf_str)

        self.list_info.append('Saved in config file: ' + file_config)   
        self.list_info.append('________________________________________')
        #for val_ls in self.list_info:
        #    print(val_ls)

        for i in range(self.num_try):
            client = self.get_ssh_connect() #создаем ssh-подключение
            if client != 'error':
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (run_report)")
            self.list_info.append('________________________________________')
            return 'error'

        time_1 = ttime.time()
        time_interval = 0

        test_time_range = 15 #minute
        self.one_percent = test_time_range*60/100
        print('Path for results: ', res_path)                
        with client.invoke_shell() as ssh:
            ssh.recv(max_bytes)
            self.list_info.append('________________________________________')

            command = "cd /" + self.server_directory
            ssh.send(f"{command}\n")
            ttime.sleep(short_pause)

            command = "source freqtrade/.env/bin/activate"
            ssh.send(f"{command}\n")
            ttime.sleep(short_pause)

            part = ssh.recv(max_bytes).decode("utf-8")
            self.list_info.append(part) 

            commands = [run_str]  # команда(строка) для запуска бектеста с заданными параметрами
            result = {}
#            wating_test_result = 300
#            pb_step = wating_test_result/100
#            self.timer.start(round(pb_step*1000))
            for command_ in commands:
                ssh.send(f"{command_}\n")
                ssh.settimeout(1)    #пауза после отправки команды, чтобы дать появиться сопутствующему тексту консоли
                  
                output = ""
                
                while (time_interval < test_time_range) and (not("Closing async ccxt session" in part)):
                    time_2 = ttime.time()
                    time_interval = (time_2 - time_1)/60

                    self.cur_progress = round(time_interval*60/self.one_percent, 2)
#                    progress_description = 'Back test progress (' + str(self.cur_progress) + '%)'
                    progress_description = 'Back test in progress... ( ' + str(self.cur_progress) + ' %)'
                    self.progress_recorder.set_progress(self.cur_progress, 100, description = progress_description)
                    
                    try:
                        part = ssh.recv(max_bytes).decode("utf-8")
                        self.list_info.append(part)
#                        print(self.list_info)
                        ttime.sleep(0.5)
#                        if (time_interval >= test_time_range) and (test_time_range < 7) and (not("Closing async ccxt session" in part)):
#                            test_time_range += 1
#                            self.one_percent = test_time_range*60/100
                        
                    except socket.timeout:
                        continue

               # if res_path in part:
               #     print(part)
               #     print(part.split('\n'))

                if "Closing async ccxt session" in part:
                    
                    self.cur_progress = 100
                    progress_description = 'Back test progress (' + str(self.cur_progress) + '%)'
                    self.progress_recorder.set_progress(self.cur_progress, 100, description = progress_description)
                    self.list_info.append('The test was completed successfully!')
                    
                    self.save_current_config(strategy_settings)
                else: 
                    if "ERROR - Fatal exception" in part:
                        self.cur_progress = 100
                        progress_description = 'Back test progress (' + str(self.cur_progress) + '%)'
                        self.progress_recorder.set_progress(self.cur_progress, 100, description = progress_description)
                        self.list_info.append('The test was completed successfully!')
                    
                        self.save_current_config(strategy_settings)
                    else:
                        if (time_interval >= test_time_range):
                            self.list_info.append('Test was broke) by timeout!')
            
            self.list_info.append('________________________________________')
            for val_ls in self.list_info:
                print(val_ls)
            print('---------------------')
#            self.reset_pb_test()

            client.close()
    def save_current_config(self, cur_config):
    
        for i in range(self.num_try):
            client = self.get_ssh_connect() #создаем ssh-подключение
            if client != 'error':
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (run_report)")
            self.list_info.append('________________________________________')
            return 'error'
            
        if client != 'error':
            try:
                sftp = client.open_sftp()
            
                remote_file = sftp.open ('/' + self.server_directory + self.server_backtests_directory +self.server_user_directory + '/.last_result.json', mode = 'r') # Путь к файлу
                json_obj = json.loads(remote_file.read())
                last_f_name = str(json_obj['latest_backtest']).split('.')
                remote_file.close()
                res_path = '/' + self.server_directory + self.server_backtests_directory +self.server_user_directory + '/' + last_f_name[0] + '.conf'
                print('Current config saved to: ', res_path)
                remote_file = sftp.open (res_path, mode = 'w') # Путь к файлу
            
                            
                # сохранить файл конфигурации тестируемой стратегии в каталоге пользователя
                for buf_str in cur_config:
                    remote_file.write(buf_str+'\n')

            finally:
                remote_file.close()
            
#            if mode == 'local':
#              res_report = self.my_txt_rep.json_to_txt(json_obj, remote_file, mode, self.local_reports_directory + user_name + '/txt/', backtest_file_name)
#            else:
#                remote_file = sftp.open ('/' + self.server_directory + self.server_backtests_directory+self.server_user_directory + self.server_reports_directory +buf_str[0] + '.conf', mode = 'w') # Путь к файлу
#                res_report = self.my_txt_rep.json_to_txt(json_obj, remote_file, mode, self.server_reports_directory, backtest_file_name)
            self.list_info.append("Created config file: ")
            self.list_info.append(last_f_name[0] + '.conf')
            
            self.list_info.append('________________________________________')
            rep_done =True
            sftp.close()
            #for val_ls in self.list_info:
            #    print(val_ls)
        else:
            return 'error'
            
    def normalyze_percents(self, num: str):
       buf = round(float(num)/100, 4)
       str_num = str(buf)
       return str_num

    def get_data_range(self):
        #start_date = datetime.datetime.date(2022, 12, 10)
        #end_date = datetime.datetime.date(2023, 1, 9)
        start_date  = datetime.strptime("2022-12-10", '%Y-%m-%d')
        end_date = datetime.strptime("2023-01-09", '%Y-%m-%d')
        my_rep = rep_from_test_res() #создаем объект нашего собственного класса rep_from_test_res()
        for i in range(self.num_try):
            client = self.get_ssh_connect() #создаем ssh-подключение
            if client != 'error':
                break
        if client == 'error':
            self.list_info.append("SSH connect to server fail after " + str(self.num_try) + " tries... (run_report)")
            self.list_info.append('________________________________________')
            return 'error'
        
        f_pair_name = 'BTC_USDT'
        df_pair_1m = my_rep.get_pair_fdata(f_pair_name, '1m', client)
        print('For range detection used ', f_pair_name)
        #print(df_pair_1m)
        start_date = df_pair_1m['date'].iloc[0]
        end_date = df_pair_1m['date'].iloc[-1]
        
        return start_date, end_date
        
    def param_of_cur_strategy(self, user_strategy_settings):
        
           buf_str = self.get_strategy(user_strategy_settings["f_strategies"])
           if buf_str == 'error':
               buf_str = 'MyLossTrailingMinROI_4_4'
           buf_str = buf_str + '_config.py'
#           user_strategy_settings["f_reports"] = os.getcwd()
           f_path = './crypto_back/templates/conf_strategies/' + buf_str
           roi_flag = False
           roi_counter = 0
            
           user_strategy_settings["f_start_d"], user_strategy_settings["f_stop_d"] = self.get_data_range()
            
           user_strategy_settings["f_max_open_trades"] = 5
           if os.path.exists(f_path):
               with open(f_path, 'r') as f:
                   user_strategy_settings["f_parts"] = list('1')
                   for line in f:
                       line = line.strip()
                       #print(line)
                       if ('arg_N' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           
                           if buf == "'none'":
                               user_strategy_settings["f_series_len"] = 0
                           else: 
                               user_strategy_settings["f_series_len"] = pars_str[1].strip()
                           
                       if ('arg_T' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           
                           if buf == "'none'":
                               user_strategy_settings["f_series_len_beepboop"] = 0
                           else: 
                               user_strategy_settings["f_series_len_beepboop"] = pars_str[1].strip()
                           
                       if ('arg_R' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_persent_same"] = 0
                           else: 
                               user_strategy_settings["f_persent_same"] = pars_str[1].strip()

                       if ('arg_P' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_price_inc"] = 0
                           else: 
                               user_strategy_settings["f_price_inc"] = pars_str[1].strip()

                       if ('arg_MR' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_movement_roi"] = 0
                           else: 
                               buf = round((float(pars_str[1].strip())*100), 3)
                               user_strategy_settings["f_movement_roi"] = buf
                               
                       if ('arg_min_roi' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_min_roi_beepboop"] = 0
                           else: 
                               buf = round((float(pars_str[1].strip())*100), 3)
                               user_strategy_settings["f_min_roi_beepboop"] = buf
                               
                       if ('my_force_exit' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_my_force_exit_time"] = '0'
                               user_strategy_settings["f_my_force_exit_value"] = '0'
                           else: 
                               pars_str = pars_str[1].split('[')
                               pars_str = pars_str[1].split(']')
                               pars_str = pars_str[0].split(',')
                               user_strategy_settings["f_my_force_exit_time"] = pars_str[0].strip()
                               buf = (round(abs(float(pars_str[1].strip())*100), 3))
                               user_strategy_settings["f_my_force_exit_value"] = buf

                       if ('stoploss' in line):
                           pars_str = line.split('=')
                           if pars_str[0].strip() == 'stoploss' :
                               buf = pars_str[1].strip()
                               if buf == "'none'":
                                   user_strategy_settings["f_stop_loss"] = 0
                               else: 
                                   buf = (round(abs(float(pars_str[1].strip())*100), 3))
                                   user_strategy_settings["f_stop_loss"] = buf

                       if ('arg_stoploss' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_des_stop_loss"] = 0
                           else: 
                               buf = (round(float(pars_str[1].strip())*100, 3))
                               user_strategy_settings["f_des_stop_loss"] = buf

                       if ('my_stoploss' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == "'none'":
                               user_strategy_settings["f_my_stop_loss_time"] = '0'
                               user_strategy_settings["f_my_stop_loss_value"] = '0'
                           else: 
                               pars_str = pars_str[1].split('[')
                               pars_str = pars_str[1].split(']')
                               pars_str = pars_str[0].split(',')
                               user_strategy_settings["f_my_stop_loss_time"] = pars_str[0].strip()
                               buf = (round(abs(float(pars_str[1].strip())*100), 3))
                               user_strategy_settings["f_my_stop_loss_value"] = buf
                               
                       if ('arg_max_loss' in line):
                           pars_str = line.split('=')
                           if pars_str[0].strip() == 'arg_max_loss' :
                               buf = pars_str[1].strip()
                               if buf == "'none'":
                                   user_strategy_settings["f_loss_beepboop"] = 0
                               else: 
                                   buf = (round(abs(float(pars_str[1].strip())*100), 3))
                                   user_strategy_settings["f_loss_beepboop"] = buf

                       if ('minimal_roi' in line):
                           roi = []
                           roi_flag = True
                           roi_counter = 0
#                           pars_str = line.split('=')
#                           buf_str = pars_str[1].strip().strip('{}')
#                           pars_str = buf_str.strip().split(',')

                           user_strategy_settings["f_min_roi_time1"] = 0
                           user_strategy_settings["f_min_roi_value1"] = 0
                           user_strategy_settings["f_min_roi_time2"] = 24
                           user_strategy_settings["f_min_roi_value2"] = 0
                           user_strategy_settings["f_min_roi_time3"] = 30
                           user_strategy_settings["f_min_roi_value3"] = 0
                           user_strategy_settings["f_min_roi_time4"] = 60
                           user_strategy_settings["f_min_roi_value4"] = 0
                           
                       if (roi_flag == True):
                            if ('}' in line):
                                roi_flag = False
                                continue
                            
                            if (':' in line):
                               roi_counter +=1
                               pars_str = line.strip().split(',')
                                                   
                               buf_str = pars_str[0].strip().strip('{}').strip(',')
                               pars_str = buf_str.split(':')
                               
                               roi_val = str(round(abs(float(pars_str[1].strip())*100), 3))
                               roi_time = pars_str[0].strip('""')

                               

                               if roi_counter == 1:
                                   user_strategy_settings["f_min_roi_time1"] = roi_time
                                   user_strategy_settings["f_min_roi_value1"] = roi_val

                               if roi_counter == 2:
                                   user_strategy_settings["f_min_roi_time2"] = roi_time
                                   user_strategy_settings["f_min_roi_value2"] = roi_val

                               if roi_counter == 3:
                                   user_strategy_settings["f_min_roi_time3"] = roi_time
                                   user_strategy_settings["f_min_roi_value3"] = roi_val

                               if roi_counter == 4:
                                   user_strategy_settings["f_min_roi_time4"] = roi_time
                                   user_strategy_settings["f_min_roi_value4"] = roi_val
                                   
                       # for MACD strategy
                       if ('buy_cci_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_buy_cci"] = buf
                       if ('sell_cci_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_sell_cci"] = buf
                           
                       if ('slow_len_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_slow_len"] = buf
                       if ('fast_len_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_fast_len"] = buf
                           
                       #for Beep Boop strategy
                       if ('ema_trend_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_ema_trend"] = buf
                       if ('source_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_source"] = buf 
                       if ('sma_source_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sma_source_enable"] = buf
                       if ('sma_signal_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sma_signal_enable"] = buf
                       if ('ema_signal_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_ema_signal_enable"] = buf
                           
                       if ('min_macd' in line):
                           pars_str = line.split('=')
                           if pars_str[0].strip() == 'min_macd':
                               buf = pars_str[1].strip()
                               if buf == "'none'":
                                   user_strategy_settings["f_min_macd"] = 0
                               else:
                                   buf = (round(float(pars_str[1].strip()), 5))
                                   user_strategy_settings["f_min_macd"] = buf
                           
                       #for Smooth Scalp strategy
                       if ('buy_adx_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_buy_adx"] = buf
                       if ('buy_adx_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_buy_adx_enable"] = buf
                       if ('sell_adx_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_sell_adx"] = buf
                       if ('sell_adx_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sell_adx_enable"] = buf
                           
                       if ('buy_fastd_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_buy_fastd"] = buf
                       if ('buy_fastd_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_buy_fastd_enable"] = buf
                       if ('sell_fastd_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_sell_fastd"] = buf
                       if ('sell_fastd_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sell_fastd_enable"] = buf
                           
                       if ('buy_fastk_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_buy_fastk"] = buf
                       if ('buy_fastk_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_buy_fastk_enable"] = buf
                       if ('sell_fastk_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_sell_fastk"] = buf
                       if ('sell_fastk_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sell_fastk_enable"] = buf
                           
                       if ('buy_mfi_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_buy_mfi"] = buf
                       if ('buy_mfi_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_buy_mfi_enable"] = buf
                       if ('sell_mfi_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_sell_mfi"] = buf
                       if ('sell_mfi_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sell_mfi_enable"] = buf
                           
                       if ('sell_cci_scalp_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           user_strategy_settings["f_sell_cci_scalp"] = buf
                       if ('sell_cci_scalp_enable_val' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_sell_cci_scalp_enable"] = buf

                       #Hyper opt
                       if ('hyperopt' in line):
                           pars_str = line.split('=')
                           buf = pars_str[1].strip()
                           if buf == 'True':
                               buf = True
                           else:
                               buf = False
                           user_strategy_settings["f_hyperopt"] = buf
#                       print(buf_str)
               
               f.close()
           else:
              user_strategy_settings["f_reports"] += f_path
           return user_strategy_settings

def main():
    ui_utils = ExampleApp()  # Создаём объект класса ExampleApp
#    ui_utils.load_ssh_my_config() # load ssh_my_config file
    l1, l2 = ui_utils.connect_ssh()
    print("Host: {0}  Port: {1}  UserName: {2}".format(ui_utils.hostname, ui_utils.port, ui_utils.username))
    for b in range(len(ui_utils.list_info)):
    	print(ui_utils.list_info[b])
    print(l1, l2)
    print(os.getcwd())
 
#    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()    





