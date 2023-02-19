#  2022-06-15 / 22:30:03
 
import numpy as np 
class config_strategy(): 
    minimal_roi = { 
    "0":  0.04
    }
    arg_N =  4
    arg_R =  100
    arg_P =  4
    arg_MR =  0.015
    my_force_exit = np.array([180, 0.002])
    stoploss = -0.02
    my_stoploss = np.array([32, -0.003])
    arg_stoploss =  0.004
#
# for MACD strategy
    buy_cci_val =  -48
    sell_cci_val =  687
    
    slow_len_val = 26
    fast_len_val = 12

# for Beep Boop strategy        
    ema_trend_val = 50
    source_val = 'close'
    sma_source_enable_val = False
    sma_signal_enable_val = False
    ema_signal_enable_val = False
    
    arg_T = 0
    arg_min_roi = 0.0
    arg_max_loss = -0.0
#
# for Smooth Scalp strategy
    buy_adx_val =  32
    buy_adx_enable_val =  True
    sell_adx_val =  53
    sell_adx_enable_val =  False
#
    buy_fastd_val =  30
    buy_fastd_enable_val =  True
    sell_fastd_val =  79
    sell_fastd_enable_val =  True
#
    buy_fastk_val =  26
    buy_fastk_enable_val =  False
    sell_fastk_val =  70
    sell_fastk_enable_val =  True
#
    buy_mfi_val =  22
    buy_mfi_enable_val =  True
    sell_mfi_val =  92
    sell_mfi_enable_val =  False
#
    sell_cci_scalp_val =  183
    sell_cci_scalp_enable_val =  True
#
# for Hyper opt
    hyperopt =  False
