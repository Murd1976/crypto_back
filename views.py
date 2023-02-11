from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.core.signing import BadSignature
from django.utils.encoding import smart_str
import os
import mimetypes
from datetime import datetime


from .forms import *
from .models import AdvUser, AllBackTests, DataBufer
#from .forms import ChangeUserInfoForm, RegisterUserForm
from .utilities import signer
from .main_web import BackTestApp
from .strategies_list import Available_strategies, set_fields_enable
# Celery Task
from .tasks import ProcessReport, ProcessBackTest


class BBLoginView(LoginView):
    template_name = 'crypto_templ/cr_login.html'
    
class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'crypto_templ/cr_logout.html'

class RegisterDoneView(TemplateView):
    template_name = 'crypto_templ/cr_register_done.html'
    
class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'crypto_templ/cr_register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('crypto_back:my_register_done')

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'crypto_templ/cr_change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('crypto_back:my_profile')
    success_message = 'User data changed'
    
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
    
class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'crypto_templ/cr_password_change.html'
    success_url = reverse_lazy('crypto_back:my_profile')
    success_message = 'User password changed'
    
class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'crypto_templ/cr_delete_user.html'
    success_url = reverse_lazy('crypto_back:index')
    
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'User deleted')
        return super().post(request, *args, **kwargs)
    
    def get_object(self, queryset = None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk = self.user_id)
    
def index(request):    
    return render(request, "crypto_templ/index.html")

@login_required
def user_profile(request):
    return render(request, 'crypto_templ/cr_profile.html')

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'crypto_templ/cr_bad_signature.html')
    
    user = get_object_or_404(AdvUser, username = username)
    if user.is_activated:
        template = 'crypto_templ/cr_user_is_activated.html'
    else:
        template = 'crypto_templ/cr_activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

#def index(request):
#    if request.method == "POST":
#        name = request.POST.get("name")
#        age = request.POST.get("age")     # получение значения поля age
#        checked1 = request.POST.get("check1")
#        return HttpResponse("<h2>Hello, {0} Checked: {1}</h2>".format(name, checked1))
#    else:
#        userform = UserForm()
#    return render(request, "index.html", {"form": userform})

@login_required
def test_mod_form(request):
#    if request.method == "POST":
#        userform = TestBackTestForm(request.POST or None)
#        if userform.is_valid():
#            bb = userform.save()
#            return redirect('crypto_back:index')
#        
    template = 'crypto_templ/cr_test_model.html'
    parts = TestBackTestForm(initial={'owner':request.user.pk})
    context = {"form": parts}
    return render(request, template, context)

@login_required
def tests_list_page(request):
	ui_utils = BackTestApp()
	ui_utils.server_user_directory = str(request.user)
	strategies_val, reports_val = ui_utils.connect_ssh()     
	template = 'crypto_templ/cr_tests_list.html'
	tests_list = reports_val
#    tests_list = AllBackTests.objects.all()
	context = {"total_files": tests_list, "user_name":request.user}
	return render(request, template, context)

@login_required
def tests_log_page(request):
#    if request.method == "POST":
#        userform = TestBackTestForm(request.POST or None)
#        if userform.is_valid():
#            bb = userform.save()
#            return redirect('crypto_back:index')
#        
    template = 'crypto_templ/cr_tests_log.html'
    tests_list = AllBackTests.objects.filter(owner=request.user)
#    tests_list = AllBackTests.objects.all()
#    tests_list.delete()
#    tests_list = AllBackTests.objects.all()
    context = {"tests_log": tests_list, "user_name":request.user}
    return render(request, template, context)

# delete record of tests
def delete_tests(request, files):
    ui_utils = BackTestApp()
    name=str(request.user)
    buf_str = files.strip('[]').split(',')
    print(buf_str)
    delete_list = []
#    delete_list.append(files)
    for f_name in buf_str:
        buf = f_name.strip()
        delete_list.append(buf.strip('\''))
    print(delete_list)    
    try:

    	ui_utils.delete_results(name, delete_list)

    	return redirect('crypto_back:my_tests_list')
    except AllBackTests.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")
    
# delete record of tests
def delete_test_log(request, id):
    try:
        test = AllBackTests.objects.get(id=id)
        test.delete()
        return redirect('crypto_back:my_tests_log')
    except AllBackTests.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")    

@login_required
def choise_strategy_page(request):
    template = 'crypto_templ/cr_choise_strategy.html'
#    ui_utils = BackTestApp()
#    strategies_val, reports_val = ui_utils.connect_ssh()
#    strategies_index = []
#    reports_index = []
#    if len(strategies_val) > 0:
#	    for b in range(len(strategies_val)):
#	        strategies_index.append(str(b))
            
#    if len(reports_val) > 0:
#	    for b in range(len(reports_val)):
#	        reports_index.append(str(b))

#    strategies_list = list(zip(strategies_index, strategies_val))
#    reports_list = list(zip(reports_index, reports_val))

    strategies_list = Available_strategies.strategies_names_tuple
    
    if request.method == "POST":
        text_buf = "Name of strategy: "
        userform = ChoiseStrategyForm(request.POST or None)
        text_buf += dict(strategies_value)[str(userform.data.get("f_strategies"))]
        
        
        if userform.is_valid():
            strategy_choise = userform.cleaned_data["f_strategies"]
            data_bufer = DataBufer.objects.filter(name=request.user)
            data_bufer.delete()
            
            data_bufer = DataBufer(name=request.user, user_strategy_choise=strategy_choise)
            data_bufer.save()
#            return reverse_lazy('crypto_back:my_backtest')
            return redirect('crypto_back:my_backtest')
#            return HttpResponse("<h2>Your choise: {0}  </h2>".format(user_strategy_choise))
        else:
            return HttpResponse(text_buf)
    
    
#    parts = ChoiseStrategyForm()
    parts = ChoiseStrategyForm(initial= {"f_text_log":strategies_list}) #{"f_strategies":strategies_val[0]})
    parts.fields['f_strategies'].choices = strategies_list
    context = {"form": parts}
    return render(request, template, context)

@login_required
def run_test_page(request):
    ui_utils = BackTestApp()
    ui_utils.server_user_directory = str(request.user)
    strategies_val, reports_val = ui_utils.connect_ssh()
#    strategies_index = []
    reports_index = []
#    if len(strategies_val) > 0:
#	    for b in range(len(strategies_val)):
#	        strategies_index.append(str(b))
            
    if len(reports_val) > 0:
	    for b in range(len(reports_val)):
	        reports_index.append(str(b))
            
#    strategies_list = list(zip(strategies_index, strategies_val))
    reports_list = list(zip(reports_index, reports_val))
    
    source_value = [('0', 'close'), ('1', 'open'), ('2', 'hight'), ('3', 'low')]

    strategies_list = Available_strategies.strategies_names_tuple
    strategies_files = Available_strategies.strategies_file_tuple

    template = 'crypto_templ/cr_run_test.html'
    strategy_keys = ['f_strategies', 'f_reports', 'f_parts', 'f_series_len', 'f_persent_same', 'f_price_inc', 'f_min_roi_time1', 'f_min_roi_value1', 'f_min_roi_time2', 'f_min_roi_value2',
                         'f_min_roi_time3', 'f_min_roi_value3', 'f_min_roi_time4', 'f_min_roi_value4', 'f_movement_roi', 'f_des_stop_loss', 'f_stop_loss', 'f_my_stop_loss_time', 'f_my_stop_loss_value',
                         'f_text_log', 'f_max_open_trades', 'f_hyperopt',
                         'f_buy_cci', 'f_sell_cci', 'f_buy_adx', 'f_buy_adx_enable', 'f_sell_adx', 'f_sell_adx_enable', 'f_buy_fastd', 'f_buy_fastd_enable', 'f_sell_fastd', 'f_sell_fastd_enable', 
                         'f_buy_fastk', 'f_buy_fastk_enable', 'f_sell_fastk', 'f_sell_fastk_enable', 'f_buy_mfi', 'f_buy_mfi_enable', 'f_sell_mfi', 'f_sell_mfi_enable', 'f_sell_cci_scalp', 'f_sell_cci_scalp_enable',
                         'f_slow_len', 'f_fast_len', 'f_ema_trend', 'f_source', 'f_sma_source_enable', 'f_sma_signal_enable', 'f_ema_signal_enable', 'f_series_len_beepboop', 'f_min_roi_beepboop', 'f_loss_beepboop',
                         'f_start_data', 'f_stop_data', 'f_start_d', 'f_stop_d', 'f_my_force_exit_time', 'f_my_force_exit_value']
    p = []

    data_bufer = DataBufer.objects.filter(name=request.user)
    data_str = str(data_bufer[0])
    user_strategy_choise = data_str.split(':')[1]

    p.append(dict(strategies_files)[user_strategy_choise])
    
# The second part for run backtest
#_________________________________________
    if request.method == "POST":
        text_buf = "Name of strategy: "
        userform = BackTestForm(request.POST or None)
        
        if userform.is_valid():
            pp = p.copy()
            
            for b in range(58):
                pp.append('')
            strategy_settings = dict(list(zip(strategy_keys, pp)))
            strategy_settings = ui_utils.param_of_cur_strategy(strategy_settings)
            #print('For test: ')
            #print(strategy_settings)
            #print()
            
            test_start = userform.cleaned_data["f_start_data"]
            print(test_start)
            
            back_test_model = AllBackTests.objects.all()
#            text_buf += dict(strategies_list)[userform.cleaned_data["f_strategies"]]
#            text_buf = "Name of strategy: " + dict(strategies_value)[str(userform.data.get("f_strategies"))]
            
#            p.append(dict(strategies_list)[userform.cleaned_data["f_strategies"]])
            
#            p.append(dict(reports_list)[userform.cleaned_data["f_reports"]])
            p.append('no reports')
            
            p.append(userform.cleaned_data["f_parts"])
            if dict(strategies_list)[user_strategy_choise] in ['MACD Strategy', 'Scalp Strategy']:
                p.append(int(strategy_settings["f_series_len"]))
                p.append(int(strategy_settings["f_persent_same"]))
                p.append(float(strategy_settings["f_price_inc"]))
            else:
                if dict(strategies_list)[user_strategy_choise] in ['BeepBoop Strategy', 'BeepBoop Strategy v2']:
                    p.append(int(userform.cleaned_data["f_series_len"]))
                    p.append(int(strategy_settings["f_persent_same"]))
                    p.append(float(strategy_settings["f_price_inc"]))
                else:
                    p.append(int(userform.cleaned_data["f_series_len"]))
                    p.append(int(userform.cleaned_data["f_persent_same"]))
                    p.append(float(userform.cleaned_data["f_price_inc"]))
                       
            p.append(userform.cleaned_data["f_min_roi_time1"])
            p.append(float(userform.cleaned_data["f_min_roi_value1"]))
            p.append(userform.cleaned_data["f_min_roi_time2"])
            p.append(float(userform.cleaned_data["f_min_roi_value2"]))
            p.append(userform.cleaned_data["f_min_roi_time3"])
            p.append(float(userform.cleaned_data["f_min_roi_value3"]))
            p.append(userform.cleaned_data["f_min_roi_time4"])
            p.append(float(userform.cleaned_data["f_min_roi_value4"]))

            p.append(float(userform.cleaned_data["f_movement_roi"]))
            p.append(float(userform.cleaned_data["f_des_stop_loss"]))
            p.append(float(userform.cleaned_data["f_stop_loss"]))
            
            p.append(userform.cleaned_data["f_my_stop_loss_time"])
            p.append(float(userform.cleaned_data["f_my_stop_loss_value"]))
                        
            p.append(userform.cleaned_data["f_text_log"])
            
            p.append(int(userform.cleaned_data["f_max_open_trades"]))
            p.append(int(userform.cleaned_data["f_hyperopt"]))
            
#            p.append(request.user)
            
            # for MACD strategy
            if dict(strategies_list)[user_strategy_choise] == 'MACD Strategy':
                p.append(int(userform.cleaned_data["f_buy_cci"]))
                p.append(int(userform.cleaned_data["f_sell_cci"]))
            else:
                p.append(int(strategy_settings["f_buy_cci"]))
                p.append(int(strategy_settings["f_sell_cci"]))
            
            #for Smooth Scalp strategy
            if dict(strategies_list)[user_strategy_choise] == 'Scalp Strategy':
                p.append(int(userform.cleaned_data["f_buy_adx"]))
                p.append(userform.cleaned_data["f_buy_adx_enable"])
                p.append(int(userform.cleaned_data["f_sell_adx"]))
                p.append(userform.cleaned_data["f_sell_adx_enable"])
            
                p.append(int(userform.cleaned_data["f_buy_fastd"]))
                p.append(userform.cleaned_data["f_buy_fastd_enable"])
                p.append(int(userform.cleaned_data["f_sell_fastd"]))
                p.append(userform.cleaned_data["f_sell_fastd_enable"])
            
                p.append(int(userform.cleaned_data["f_buy_fastk"]))
                p.append(userform.cleaned_data["f_buy_fastk_enable"])
                p.append(int(userform.cleaned_data["f_sell_fastk"]))
                p.append(userform.cleaned_data["f_sell_fastk_enable"])
            
                p.append(int(userform.cleaned_data["f_buy_mfi"]))
                p.append(userform.cleaned_data["f_buy_mfi_enable"])
                p.append(int(userform.cleaned_data["f_sell_mfi"]))
                p.append(userform.cleaned_data["f_sell_mfi_enable"])
            
                p.append(int(userform.cleaned_data["f_sell_cci_scalp"]))
                p.append(userform.cleaned_data["f_sell_cci_scalp_enable"])
            else:
                p.append(int(strategy_settings["f_buy_adx"]))
                p.append(strategy_settings["f_buy_adx_enable"])
                p.append(int(strategy_settings["f_sell_adx"]))
                p.append(strategy_settings["f_sell_adx_enable"])
            
                p.append(int(strategy_settings["f_buy_fastd"]))
                p.append(strategy_settings["f_buy_fastd_enable"])
                p.append(int(strategy_settings["f_sell_fastd"]))
                p.append(strategy_settings["f_sell_fastd_enable"])
            
                p.append(int(strategy_settings["f_buy_fastk"]))
                p.append(strategy_settings["f_buy_fastk_enable"])
                p.append(int(strategy_settings["f_sell_fastk"]))
                p.append(strategy_settings["f_sell_fastk_enable"])
            
                p.append(int(strategy_settings["f_buy_mfi"]))
                p.append(strategy_settings["f_buy_mfi_enable"])
                p.append(int(strategy_settings["f_sell_mfi"]))
                p.append(strategy_settings["f_sell_mfi_enable"])
            
                p.append(int(strategy_settings["f_sell_cci_scalp"]))
                p.append(int(strategy_settings["f_sell_cci_scalp_enable"]))
                
            #for Beep Boop strategy
            if dict(strategies_list)[user_strategy_choise] in ['BeepBoop Strategy', 'BeepBoop Strategy v2', 'BeepBoop Strategy v3',  'BeepBoop Strategy v4']:
                p.append(int(userform.cleaned_data["f_slow_len"]))
                p.append(int(userform.cleaned_data["f_fast_len"]))
                p.append(int(userform.cleaned_data["f_ema_trend"]))
                p.append(dict(source_value)[userform.cleaned_data["f_source"]])
                p.append(userform.cleaned_data["f_sma_source_enable"])
                p.append(userform.cleaned_data["f_sma_signal_enable"])
                p.append(userform.cleaned_data["f_ema_signal_enable"])
                
                if dict(strategies_list)[user_strategy_choise] in ['BeepBoop Strategy v3']:
                    p.append(int(userform.cleaned_data["f_series_len_beepboop"]))
                    p.append(float(userform.cleaned_data["f_min_roi_beepboop"]))
                    p.append(float(userform.cleaned_data["f_loss_beepboop"]))
                else:
                    p.append(int(strategy_settings["f_series_len_beepboop"]))
                    p.append(float(strategy_settings["f_min_roi_beepboop"]))
                    p.append(float(strategy_settings["f_loss_beepboop"]))
            else:
                p.append(int(strategy_settings["f_slow_len"]))
                p.append(int(strategy_settings["f_fast_len"]))
                p.append(int(strategy_settings["f_ema_trend"]))
                p.append(strategy_settings["f_source"])
                p.append(strategy_settings["f_sma_source_enable"])
                p.append(strategy_settings["f_sma_signal_enable"])
                p.append(strategy_settings["f_ema_signal_enable"])
                
                p.append(int(strategy_settings["f_series_len_beepboop"]))
                p.append(float(strategy_settings["f_min_roi_beepboop"]))
                p.append(float(strategy_settings["f_loss_beepboop"]))
             
            s1, s2 = check_date(userform.cleaned_data["f_start_data"], userform.cleaned_data["f_stop_data"], strategy_settings["f_start_d"], strategy_settings["f_stop_d"])
            p.append(s1)
            p.append(s2)
            p.append(strategy_settings["f_start_d"])
            p.append(strategy_settings["f_stop_d"])
            
            p.append(userform.cleaned_data["f_my_force_exit_time"])
            p.append(float(userform.cleaned_data["f_my_force_exit_value"]))
                
            print(p)
            print()
            back_test_record = AllBackTests(strategy_name= p[0], owner= request.user, parts= p[2], 
                                            minimal_roi1_time= p[6], minimal_roi1_value= p[7], minimal_roi2_time= p[8], minimal_roi2_value= p[9], minimal_roi3_time= p[10], minimal_roi3_value= p[11], minimal_roi4_time= p[12], minimal_roi4_value= p[13], 
                                            arg_N= p[3], arg_R= p[4], arg_P= p[5], arg_MR= p[14],
                                            stoploss= p[16], my_stoploss_time= p[17], my_stoploss_value= p[18], arg_stoploss= p[15], 
                                            text_log= p[19], max_open_trades= p[20], hyperopt= p[21],
                                            buy_cci= p[22], sell_cci= p[23],
                                            buy_adx= p[24], buy_adx_enable= p[25], sell_adx= p[26], sell_adx_enable= p[27], 
                                            buy_fastd= p[28], buy_fastd_enable= p[29], sell_fastd= p[30], sell_fastd_enable= p[31], 
                                            buy_fastk= p[32], buy_fastk_enable= p[33], sell_fastk= p[34], sell_fastk_enable= p[35], 
                                            buy_mfi= p[36], buy_mfi_enable= p[37], sell_mfi= p[38], sell_mfi_enable= p[39], 
                                            sell_cci_scalp= p[40], sell_cci_scalp_enable= p[41], slow_len= p[42], fast_len= p[43], ema_trend= p[44], source= p[45], 
                                            sma_source_enable= p[46], sma_signal_enable= p[47], ema_signal_enable= p[48], series_len_beepboop= p[49], min_roi_beepboop= p[50], loss_beepboop= p[51],
                                            start_data = p[52], stop_data = p[53], my_force_exit_time = p[56], my_force_exit_value = p[57])
            back_test_record.save()

            strategy_settings = dict(list(zip(strategy_keys, p)))
            
            name=str(request.user)
            
            # Create Task
            back_test_task = ProcessBackTest.delay(strategy_settings, name)
            # Get ID
            task_id = back_test_task.task_id
            # Print Task ID
            #print(f'Celery Task ID: {task_id}')
            #print()
#            print(back_test_task)
            # Return demo view with Task ID
            
#            ui_utils.run_backtest(strategy_settings, name)
            strategy_settings['f_strategies'] = dict(strategies_list)[user_strategy_choise]
            strategy_settings["f_text_log"] = str(request.user) + '/ ' + str(ui_utils.list_info)
#            parts = BackTestForm(initial={"f_text_log":str(request.user) + '/ ' + str(ui_utils.list_info)})
            print(len(strategy_settings))
            print(strategy_settings, '\n')
            parts = BackTestForm(initial= strategy_settings)

            parts = set_fields_enable(strategy_settings['f_strategies'], parts)
            #parts.fields['f_reports'].choices = reports_list
            
            
        
            context = {"form": parts, 'task_id': task_id, "start_data":strategy_settings['f_start_d'], "stop_data":strategy_settings['f_stop_d']}
            return render(request, template, context)
#            return HttpResponse("<h2>Hello, {0} :{1} :{2} </h2>".format(text_buf, strategies_list[1], nnn))
        else:
            return HttpResponse("Invalid data")

# The start part for choice parameters
#_________________________________________    
    #BackTestForm().yyy = range(2017, 2019)
    parts = BackTestForm()
    text_buf = str(ui_utils.list_info)
#    p.append( "min_roi_trailing_loss_4_4.py")
#    p.append(dict(strategies_files)[user_strategy_choise])
    for b in range(58):
        p.append('')
    strategy_settings = dict(list(zip(strategy_keys, p)))
    strategy_settings = ui_utils.param_of_cur_strategy(strategy_settings)
    strategy_settings['f_strategies'] = dict(strategies_list)[user_strategy_choise]
    
#    strategy_settings["f_text_log"] = strategy_settings
    strategy_settings['f_start_data'], strategy_settings['f_stop_data'] = check_date(strategy_settings['f_start_d'], strategy_settings['f_stop_d'], strategy_settings["f_start_d"], strategy_settings["f_stop_d"])
    print(len(strategy_settings))
    print(strategy_settings)
    parts = BackTestForm(initial= strategy_settings) #{"f_text_log":strategy_settings}) #text_buf})
    #parts.yyy = range(2017, 2019)
#    parts = BackTestForm(initial= {"f_text_log":p[0]}) #text_buf})
    
    #parts = set_fields_enable(strategy_settings['f_strategies'], parts)
    #parts.fields['f_reports'].choices = reports_list
   
    context = {"form": parts, "start_data":strategy_settings['f_start_d'], "stop_data":strategy_settings['f_stop_d']}
    return render(request, template, context)

def check_date(start, stop, start_range, end_range):
    #s1 = datetime.datetime.strptime(start_range, '%Y-%m-%d')
    #s2 = datetime.datetime.strptime(and_range, '%Y-%m-%d')
    #a = start.split('-')
    #b = stop.split('-')
    s1 = start_range.date()
    s2 = end_range.date()
    if start > stop :
        buf = start
        start = stop
        stop = buf
    if start == stop :
        stop += datetime.timedelta(days=1)
        
    if start < start_range.date() :
        start_d = s1
    else:
        if start >= end_range.date() :
            start_d = s2 - datetime.timedelta(days=1)
        else:
            start_d = start
        
    if stop > end_range.date() :
        stop_d = s2
    else:
        if stop <= start_range.date() :
            stop_d = s1 + datetime.timedelta(days=1)
            print('Stop_d = ', stop_d)
        else:
            stop_d = stop
    
    
    cc = str(stop_d-start_d)
    dd = cc.split()[0]
    if  int(dd) > 10:
        stop_d = start_d + datetime.timedelta(days=10)
    return start_d, stop_d

@login_required
def create_report_page(request):
    template = 'crypto_templ/cr_create_report.html'
    ui_utils = BackTestApp()
    ui_utils.server_user_directory = str(request.user)
    ui_utils.list_info = []
    strategies_val, reports_val = ui_utils.connect_ssh()
    
    reports_index = []
            
    if len(reports_val) > 0:
	    for b in range(len(reports_val)):
	        reports_index.append(str(b))
	        
    reports_list = list(zip(reports_index, reports_val))

    if request.method == "POST":
        userform = CreateReportForm(reports_list, request.POST or None)
                
        if userform.is_valid():
            text_buf = dict(reports_list)[str(userform.cleaned_data["f_reports"])]

            name=str(request.user)
            # Create Task
            report_task = ProcessReport.delay(text_buf, name)
            # Get ID
            task_id = report_task.task_id
            # Print Task ID
            print(f'Celery Task ID: {task_id}')
            # Return demo view with Task ID
            
            
#            ui_utils.run_report(text_buf, 'local', name)
            parts = CreateReportForm(reports_list, initial= {"f_text_log":str(ui_utils.list_info)})
#            parts.fields['f_reports'].choices = reports_list		
            context = {"form": parts, 'task_id': task_id}
            return render(request, template, context)
        
    parts = CreateReportForm(reports_list, initial= {"f_text_log":str(ui_utils.list_info)})    
#    parts = CreateReportForm(dynamic_choices = dict(reports_list))
#    parts.fields['f_reports'].choices = reports_list

    context = {"form": parts}
    return render(request, template, context)

@login_required
def reports_txt_files_list(request):
    name=str(request.user)
    f_path = './reports/' + name + '/txt/'

    if not os.path.exists('./reports/' + name):
        os.mkdir('./reports/' + name)
        os.mkdir(f_path)
    if not os.path.exists(f_path):
        os.mkdir(f_path)
        
    f_list = os.listdir('./reports/' + name + '/txt/')   
    
    return render(request, 'crypto_templ/cr_files_list.html', context = {'user_name':name, 'total_files':f_list, 'path':f_path})


    '''
def delete_txt_report(request, f_name):
    name=str(request.user)
    f_path = './reports/' + name + '/txt/' + f_name
    if os.path.exists(f_path):
        os.remove(f_path)
    
    return redirect('crypto_back:my_txt_reports')
    '''
@login_required
def delete_txt_report(request, files):
    ui_utils = BackTestApp()
    name=str(request.user)
    buf_str = files.strip('[]').split(',')
    print(buf_str)
    delete_list = []
#    delete_list.append(files)
    for f_name in buf_str:
        buf = f_name.strip()
        delete_list.append(buf.strip('\''))
    print(delete_list)    
    try:
        f_path = './reports/' + name + '/txt/'
        ui_utils.delete_tests(f_path, delete_list)

        return redirect('crypto_back:my_txt_reports')
    except AllBackTests.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")

@login_required
def reports_xlsx_files_list(request):
    name=str(request.user)
    f_path = './reports/' + name + '/xlsx/'
    if not os.path.exists('./reports/' + name):
        os.mkdir('./reports/' + name)
        os.mkdir(f_path)
    if not os.path.exists(f_path):
        os.mkdir(f_path)
        
    f_list = os.listdir('./reports/' + name + '/xlsx/')
    
    return render(request, 'crypto_templ/cr_files_list.html', context = {'user_name':name, 'total_files':f_list, 'path':f_path})

@login_required
def delete_xlsx_report(request, files):
    ui_utils = BackTestApp()
    name=str(request.user)
    buf_str = files.strip('[]').split(',')
    print(buf_str)
    delete_list = []
#    delete_list.append(files)
    for f_name in buf_str:
        buf = f_name.strip()
        delete_list.append(buf.strip('\''))
    print(delete_list)    
    try:
        f_path = './reports/' + name + '/xlsx/'
        ui_utils.delete_tests(f_path, delete_list)

        return redirect('crypto_back:my_xlsx_reports')
    except AllBackTests.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")
        
'''        
def delete_xlsx_report(request, f_name):
    name=str(request.user)
    f_path = './reports/' + name + '/xlsx/' + f_name
    if os.path.exists(f_path):
        os.remove(f_path)
    
    return redirect('crypto_back:my_xlsx_reports')
'''

@login_required
def download_report(request):
    # Get the filename
    file_name = request.GET.get('file_name')
    if file_name != '':
        user_name=str(request.user)
        st = file_name.split('.')
        path_to_file = ''
        if st[1] == 'txt':
            # Define the full file path
            path_to_file = "./reports/{0}/txt/{1}".format(user_name, file_name)
        if st[1] == 'xlsx':
            # Define the full file path
            path_to_file = "./reports/{0}/xlsx/{1}".format(user_name, file_name)
        if path_to_file == '':
           return render(request, 'crypto_templ/cr_files_list.html') 
            
        # Open the file for reading content
        f = open(path_to_file, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(path_to_file)
        # Set the return value of the HttpResponse
        response = HttpResponse(f, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
#       response['X-Sendfile'] = smart_str(path_to_file)
        return response
    else:
        # Load the template
        return render(request, 'crypto_templ/cr_files_list.html')


def other_page(request, page):
    try:
        template = get_template('crypto_templ/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request = request))

def home(request):
    data = {"header": "Main window", "message": "Welcome to Crypto-backtest!"}
    return render(request, "crypto_templ/home.html", context=data)
 
#def about(request):
#    header = "Personal Data"                    # обычная переменная
#    langs = ["English", "German", "Spanish"]    # массив
#    user ={"name" : "Tom", "age" : 23}          # словарь
#    addr = ("Абрикосовая", 23, 45)              # кортеж
 
#    data = {"header": header, "langs": langs, "user": user, "address": addr}
#    return render(request, "crypto_templ/pers_data.html", context=data)
 
def contact(request):
    return HttpResponse("<h2>Контакты</h2>")

def products(request, productid=17):
    category = request.GET.get("cat", "")
    output = "<h2>Product № {0}  Category: {1}</h2>".format(productid, category)
    return HttpResponse(output)
 
def users(request):
    id = request.GET.get("id", 1)
    name = request.GET.get("name", "Den")
    output = "<h2>User</h2><h3>id: {0}  name: {1}</h3>".format(id, name)
    return HttpResponse(output)

def m304(request):
    return HttpResponseNotModified()
 
def m400(request):
    return HttpResponseBadRequest("<h2>Bad Request</h2>")
 
def m403(request):
    return HttpResponseForbidden("<h2>Forbidden</h2>")
 
def m404(request):
    return HttpResponseNotFound("<h2>Not Found</h2>")
 
def m405(request):
    return HttpResponseNotAllowed("<h2>Method is not allowed</h2>")
 
def m410(request):
    return HttpResponseGone("<h2>Content is no longer here</h2>")
 
def m500(request):
    return HttpResponseServerError("<h2>Something is wrong</h2>")






