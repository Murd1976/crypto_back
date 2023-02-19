#The list of available strategies
 
import numpy as np 
class Available_strategies():
    strategies_file_tuple = [('0', 'st_min_roi_trailing_loss_4_4.py'), ('1', 'st_min_roi_trailing_loss_4_4_dump.py'), ('2', 'st_min_roi_trailing_loss_4_4_v3.py'), ('3', 'st_min_roi_trailing_loss_5_5.py'),
                        ('4', 'st_min_roi_trailing_loss_curve.py'), ('5', 'st_min_roi_trailing_loss_n_green.py'), ('6', 'st_min_roi_trailing_loss_n_red.py'), 
                        ('7', 'st_reinforced_smooth_scalp_v2.py'), ('8', 'st_macd_strategy.py'), ('9', 'st_beep_boop_v2.py'), ('10', 'st_beep_boop_v3.py'), ('11', 'st_beep_boop_v4.py')]
    strategies_names_tuple = [('0', '4x4 Pump'), ('1', '4x4 Dump'), ('2', '4x4 Pump v3'), ('3', '5x5 Pump'),
                        ('4', 'Curve Inversion'), ('5', 'N Green Candles'), ('6', 'N Red Candles'), ('7', 'Scalp Strategy'), ('8', 'MACD Strategy'), 
                        ('9', 'BeepBoop Strategy v2'), ('10', 'BeepBoop Strategy v3'), ('11', 'BeepBoop Strategy v4')]
                        
    strategies_class_tuple = [('0', 'MyLossTrailingMinROI_4_4'), ('1', 'MyLossTrailingMinROI_4_4_dump'), ('2', 'MyLossTrailingMinROI_4_4_v3'), ('3', 'MyLossTrailingMinROI_5_5'),
                        ('4', 'MyLossTrailingMinROICurve'), ('5', 'MyLossTrailingMinROI_N_Green'), ('6', 'MyLossTrailingMinROI_N_Red'), 
                        ('7', 'MyReinforcedSmoothScalp_v2'), ('8', 'MyMACDStrategy'), ('9', 'MyBeepBoop_v2'), ('10', 'MyBeepBoop_v3'), ('11', 'MyBeepBoop_v4')]

    ignor_list = [
                    ('MyLossTrailingMinROI_4_4', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyLossTrailingMinROI_4_4_dump', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyLossTrailingMinROI_4_4_v3', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyLossTrailingMinROI_5_5', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyLossTrailingMinROICurve', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyLossTrailingMinROI_N_Green', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyLossTrailingMinROI_N_Red', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyReinforcedSmoothScalp_v2', ['buy_cci', 'sell_cci', 'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable', 'arg_T', 'agr_min_roi', 'arg_max_loss']),
                    ('MyMACDStrategy', ['buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 'sell_fastd_enable', 
                        'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi',
                        'arg_T', 'agr_min_roi', 'arg_max_loss',
                        'buy_mfi_enable', 'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable', 
                        'slow_len', 'fast_len', 'ema_trend', 'source', 'sma_source_enable', 'sma_signal_enable', 'ema_signal_enable']),
                    ('MyBeepBoop', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable', 
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable']),
                    ('MyBeepBoop_v2', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable', 
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable']),
                    ('MyBeepBoop_v3', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable', 
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable']),
                    ('MyBeepBoop_v4', ['buy_cci', 'sell_cci', 'buy_adx', 'buy_adx_enable', 'sell_adx', 'sell_adx_enable', 'buy_fastd', 'buy_fastd_enable', 'sell_fastd', 
                        'sell_fastd_enable', 'buy_fastk', 'buy_fastk_enable', 'sell_fastk', 'sell_fastk_enable', 'buy_mfi', 'buy_mfi_enable', 
                        'sell_mfi', 'sell_mfi_enable', 'sell_cci_scalp', 'sell_cci_scalp_enable'])
    ]
    
def set_fields_enable(strategy_name, parts):

        if strategy_name in ['4x4 Pump', '4x4 Dump', '4x4 Pump v3', '5x5 Pump', 'Curve Inversion', 'N Green Candles', 'N Red Candles']:
            parts.fields['f_buy_cci'].disabled = True
            parts.fields['f_sell_cci'].disabled = True
            
            parts.fields['f_buy_adx'].required = False
            parts.fields['f_buy_adx'].disabled = True
            parts.fields['f_buy_adx_enable'].disabled = True
            parts.fields['f_sell_adx'].disabled = True
            parts.fields['f_sell_adx_enable'].disabled = True
            parts.fields['f_buy_fastd'].disabled = True
            parts.fields['f_buy_fastd_enable'].disabled = True
            parts.fields['f_sell_fastd'].disabled = True
            parts.fields['f_sell_fastd_enable'].disabled = True
            parts.fields['f_buy_fastk'].disabled = True
            parts.fields['f_buy_fastk_enable'].disabled = True
            parts.fields['f_sell_fastk'].disabled = True
            parts.fields['f_sell_fastk_enable'].disabled = True
            parts.fields['f_buy_mfi'].disabled = True
            parts.fields['f_buy_mfi_enable'].disabled = True
            parts.fields['f_sell_mfi'].disabled = True
            parts.fields['f_sell_mfi_enable'].disabled = True
            parts.fields['f_sell_cci_scalp'].disabled = True
            parts.fields['f_sell_cci_scalp_enable'].disabled = True
            
            parts.fields['f_min_roi_beepboop'].disabled = True
            parts.fields['f_loss_beepboop'].disabled = True
            parts.fields['f_series_len_beepboop'].disabled = True
               
            parts.fields['f_fast_len'].disabled = True
            parts.fields['f_slow_len'].disabled = True
            parts.fields['f_ema_trend'].disabled = True
            parts.fields['f_source'].disabled = True
            parts.fields['f_sma_source_enable'].disabled = True
            parts.fields['f_sma_signal_enable'].disabled = True
            parts.fields['f_ema_signal_enable'].disabled = True
        
        if strategy_name in ['MACD Strategy']:
            parts.fields['f_series_len'].disabled = True
            parts.fields['f_persent_same'].disabled = True
            parts.fields['f_price_inc'].disabled = True
                
                
            parts.fields['f_buy_adx'].disabled = True
            parts.fields['f_buy_adx_enable'].disabled = True
            parts.fields['f_sell_adx'].disabled = True
            parts.fields['f_sell_adx_enable'].disabled = True
            parts.fields['f_buy_fastd'].disabled = True
            parts.fields['f_buy_fastd_enable'].disabled = True
            parts.fields['f_sell_fastd'].disabled = True
            parts.fields['f_sell_fastd_enable'].disabled = True
            parts.fields['f_buy_fastk'].disabled = True
            parts.fields['f_buy_fastk_enable'].disabled = True
            parts.fields['f_sell_fastk'].disabled = True
            parts.fields['f_sell_fastk_enable'].disabled = True
            parts.fields['f_buy_mfi'].disabled = True
            parts.fields['f_buy_mfi_enable'].disabled = True
            parts.fields['f_sell_mfi'].disabled = True
            parts.fields['f_sell_mfi_enable'].disabled = True
            parts.fields['f_sell_cci_scalp'].disabled = True
            parts.fields['f_sell_cci_scalp_enable'].disabled = True
              
            parts.fields['f_fast_len'].disabled = True
            parts.fields['f_slow_len'].disabled = True
            parts.fields['f_ema_trend'].disabled = True
            parts.fields['f_source'].disabled = True
            parts.fields['f_sma_source_enable'].disabled = True
            parts.fields['f_sma_signal_enable'].disabled = True
            parts.fields['f_ema_signal_enable'].disabled = True
            
            parts.fields['f_min_roi_beepboop'].disabled = True
            parts.fields['f_loss_beepboop'].disabled = True
            parts.fields['f_series_len_beepboop'].disabled = True
     
        if strategy_name in ['Scalp Strategy']:
            parts.fields["f_series_len"].disabled = True
            parts.fields["f_persent_same"].disabled = True
            parts.fields["f_price_inc"].disabled = True
               
            parts.fields['f_buy_cci'].disabled = True
            parts.fields['f_sell_cci'].disabled = True
                
            parts.fields['f_fast_len'].disabled = True
            parts.fields['f_slow_len'].disabled = True
            parts.fields['f_ema_trend'].disabled = True
            parts.fields['f_source'].disabled = True
            parts.fields['f_sma_source_enable'].disabled = True
            parts.fields['f_sma_signal_enable'].disabled = True
            parts.fields['f_ema_signal_enable'].disabled = True
            
            parts.fields['f_min_roi_beepboop'].disabled = True
            parts.fields['f_loss_beepboop'].disabled = True
            parts.fields['f_series_len_beepboop'].disabled = True
                
        if strategy_name in ['BeepBoop Strategy', 'BeepBoop Strategy v2', 'BeepBoop Strategy v3', 'BeepBoop Strategy v4']:
            #parts.fields['f_persent_same'].disabled = True
            #parts.fields['f_price_inc'].disabled = True
             
            parts.fields['f_buy_cci'].disabled = True
            parts.fields['f_sell_cci'].disabled = True
              
            parts.fields['f_buy_adx'].disabled = True
            parts.fields['f_buy_adx_enable'].disabled = True
            parts.fields['f_sell_adx'].disabled = True
            parts.fields['f_sell_adx_enable'].disabled = True
            parts.fields['f_buy_fastd'].disabled = True
            parts.fields['f_buy_fastd_enable'].disabled = True
            parts.fields['f_sell_fastd'].disabled = True
            parts.fields['f_sell_fastd_enable'].disabled = True
            parts.fields['f_buy_fastk'].disabled = True
            parts.fields['f_buy_fastk_enable'].disabled = True
            parts.fields['f_sell_fastk'].disabled = True
            parts.fields['f_sell_fastk_enable'].disabled = True
            parts.fields['f_buy_mfi'].disabled = True
            parts.fields['f_buy_mfi_enable'].disabled = True
            parts.fields['f_sell_mfi'].disabled = True
            parts.fields['f_sell_mfi_enable'].disabled = True
            parts.fields['f_sell_cci_scalp'].disabled = True
            parts.fields['f_sell_cci_scalp_enable'].disabled = True
                
        return parts