#  2022-11-11 / 08:58:46
 
import numpy as np 
class config_strategy(): 
    minimal_roi = { 
        "0":  0.02,        
    }
    arg_N = 9
    arg_R = 0
    arg_P = 0.0
    arg_MR =  0.0
    stoploss = -0.01
    my_stoploss = np.array([32, -0.00])
    arg_stoploss =  0.0
#
# for MACD strategy
    buy_cci_val =  -48
    sell_cci_val =  687
    
    slow_len_val = 26
    fast_len_val = 12

# for Beep Boop strategy        
    ema_trend_val = 200
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

