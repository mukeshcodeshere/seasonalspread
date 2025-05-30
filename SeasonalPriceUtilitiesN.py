#SeasonalPriceUtilitiesN.py
import time
from GvWSConnection import *
from PriceUtilites import *
import numpy as np
import sys
from datetime import timedelta, datetime as dt
from dotenv import load_dotenv
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("GvWSUSERNAME")
PASSWORD = os.getenv("GvWSPASSWORD")

conn = GvWSConnection(USERNAME, PASSWORD)

def getSeasonalPrices(contractIn,contractOut,monthIn,yearsListIn) :
    
    startDate = '1/1/2000'
    
    contractList = []
    contractOut = []
    for x in yearsListIn :
        
        if '#' in contractIn :
            
            contractList.append( contractIn  + monthIn + str(x))
        else:
            contractList.append( '/'+ contractIn  + monthIn + str(x))
                          
        contractOut.append( contractIn  + '_' + monthIn + str(x))  
    try :    
        d1 = conn.get_daily(contractList, start_date = dt.strptime(startDate ,'%m/%d/%Y'))
        
    except :
        d1 = conn.get_daily(contractList, start_date = dt.strptime(startDate ,'%m/%d/%Y'))
    # nameOut = ['14','15','16','17','18','19','20','21','22']

    xx = createDailyDataMV(d1,contractList,contractOut)
    
    return xx


def contractMonths(expireIn,contractIn) :
    
    contractMonths = expireIn[expireIn.index > dt.today()].copy()
    
    expireDate =  contractMonths[contractMonths['MonthCode']== contractIn]
    
    return expireDate.iloc[0,:]


def yearList(lastTradeIn,yearsBackIn,typeIn,contractIn1,contractIn2,futuresContractDictIn) :
    
    curYearInt = lastTradeIn['Year'] % 100 #Keep only last two digets of yeat
    
    # if contractIn1 == 'F' :
        
    #     curYearInt = int(lastTradeIn[-2:]) +1 #Accounts for Jan being year +1
        
    # else :
        
    #     curYearInt = int(lastTradeIn[-2:])
    
    yearList1 =[]
    yearList2 = []
    
        
    for i in range(curYearInt - yearsBackIn,curYearInt+1) :
        
        y1Temp = i
        
        if len(str(y1Temp)) == 1 :
            y1Temp = '0'+str(y1Temp)
            
            
        yearList1.append(str(y1Temp))
        
        if typeIn == 'Timing' or typeIn == 'Box' or typeIn == 'Fly' or typeIn == 'Custom':
            

            if futuresContractDictIn[contractIn1]['num'] <= futuresContractDictIn[contractIn2]['num'] :
                
                y2Temp = i    
                
            else :
                
                y2Temp = i+1
                
                
            if len(str(y2Temp)) ==1 :
                y2Temp = '0'+str(y2Temp)
                
            yearList2.append(str(y2Temp))
            
        elif typeIn =='Crack' or typeIn == 'Location' or typeIn == 'CrossProduct'or typeIn == 'Arb' or typeIn == 'Calendar' or typeIn == 'Quarterly': # Added Calendar and Quarterly
            
            y2Temp = i
            
            if len(str(y2Temp)) ==1 :
                y2Temp = '0'+str(y2Temp)
                
            yearList2.append(str(y2Temp))
        
        elif typeIn =='Flat' or typeIn == 'Diff':
            
            yearList2.append(str(y1Temp))
            
        else :
            
            sys.exit('Please Check Type')
        
    return (yearList1,yearList2)

def yearList_Dev(lastTradeIn,yearsBackIn,typeIn,contractIn1,contractIn2,futuresContractDictIn) :
    
    curYearInt = lastTradeIn['Year'] % 100 #Keep only last two digets of yeat
    
    # if contractIn1 == 'F' :
        
    #     curYearInt = int(lastTradeIn[-2:]) +1 #Accounts for Jan being year +1
        
    # else :
    #     curYearInt = int(lastTradeIn[-2:])
    
    yearList1 =[]
    yearList2 = []
    
        
    for i in range(curYearInt - yearsBackIn,curYearInt+1) :
        
        y1Temp = i
        
        if len(str(y1Temp)) == 1 :
            y1Temp = '0'+str(y1Temp)
            
            
        yearList1.append(str(y1Temp))
        
        # if typeIn == 'Timing' or typeIn == 'Box' or typeIn == 'Fly':
            

        if futuresContractDictIn[contractIn1]['num'] <= futuresContractDictIn[contractIn2]['num'] :
            
            y2Temp = i    
            
        else :
            
            y2Temp = i+1
            
            
        if len(str(y2Temp)) ==1 :
            y2Temp = '0'+str(y2Temp)
            
        yearList2.append(str(y2Temp))
            
        # elif typeIn =='Crack' or typeIn == 'Location' or typeIn == 'CrossProduct':
            
        #     y2Temp = i
            
        #     if len(str(y2Temp)) ==1 :
        #         y2Temp = '0'+str(y2Temp)
                
        #     yearList2.append(str(y2Temp))
        
        # else :
            
        #     sys.exit('Please Check Type')
        
    return (yearList1,yearList2)




def createSpread(priceIn1,priceIn2,lastTradeIn,yearListIn1,converstionFactorIn1,converstionFactorIn2,tradeTypeIn):
    
    listNameOut = []
    
    lastTrade = dt.strptime(lastTradeIn['LastTrade'],'%m/%d/%y')
    
    startD = (lastTrade - timedelta(weeks = 53)).strftime('%m/%d/%Y')
    endD = lastTrade.strftime('%m/%d/%Y')
    
    
    df_index = pd.date_range(start =startD, end = endD, freq = 'B' ).rename('Dates')
    spread = pd.DataFrame({}, index = df_index)
    
    price1List = [*priceIn1] # Easy way to make list out of Dict Keys
    price2List = [*priceIn2]
    
    p1 = priceIn1[price1List[-1]]['Close']*converstionFactorIn1
    
    if tradeTypeIn == 'Flat' or tradeTypeIn == 'Diff' :
        p2 = priceIn2[price2List[-1]]['Close']*0
    else :
        p2 = priceIn2[price2List[-1]]['Close']*converstionFactorIn2
    spread_temp = pd.merge(p1,p2, how = 'inner', left_index = True, right_index = True)
    spread_temp['spread'] = spread_temp.iloc[:,0] - spread_temp.iloc[:,1]
    spread_temp = spread_temp.iloc[:,2]
    spread_temp = spread_temp[startD:]
    spread = pd.merge(spread,spread_temp,how = 'left', left_index = True, right_index = True).ffill()
    spread[spread.index > spread_temp.index[-1]] =np.nan
    
    listNameOut.append(yearListIn1[-1])
    
    
    for i,j,m in zip(price1List[:-1],price2List[:-1],yearListIn1[:-1]):
        
        p1 = priceIn1[i]['Close']*converstionFactorIn1
        
        if tradeTypeIn == 'Flat' or tradeTypeIn == 'Diff' :
            p2 = priceIn2[j]['Close']*0
        else :
            p2 = priceIn2[j]['Close']*converstionFactorIn2
        
        spread_temp = pd.merge(p1,p2, how = 'inner', left_index = True, right_index = True)
        spread_temp['spread'] = spread_temp.iloc[:,0] - spread_temp.iloc[:,1]
        
        startD_temp = (spread_temp.index[0] - timedelta(weeks = 52)).strftime('%m/%d/%Y')
        endD_temp = spread_temp.index[-1].strftime('%m/%d/%Y')
        df_indexTemp = pd.date_range(start =startD_temp, end = endD_temp, freq = 'B' ).rename('Dates')
        spreadTemp_df = pd.DataFrame({}, index = df_indexTemp)
        
        spread_temp1 = pd.merge(spreadTemp_df,spread_temp['spread'], how ='left', left_index = True, right_index = True).ffill()
        
        index_len = len(spread)
        spread_temp2 = pd.DataFrame(spread_temp1.iloc[-index_len:,:])
        spread_temp2 = spread_temp2.set_index(spread.index)
        spread_temp2.columns = [j]
        spread = pd.merge(spread_temp2,spread,how = 'left', left_index = True, right_index = True)
        listNameOut.append(m)
    
    listNameOut.reverse() # Correcting order of list names
    spread.columns = listNameOut
    
    return spread


def createSpread_v100(priceIn1,priceIn2,expireScheduleIn,contractIn,yearListIn1,converstionFactorIn1,converstionFactorIn2,tradeTypeIn):
    
    listNameOut = []
    lastTradeIn = contractMonths(expireScheduleIn,contractIn)
    
    lastTrade = dt.strptime(lastTradeIn['LastTrade'],'%m/%d/%y')
    
    startD = (lastTrade - timedelta(weeks = 53)).strftime('%m/%d/%Y')
    endD = lastTrade.strftime('%m/%d/%Y')
    
    
    df_index = pd.date_range(start =startD, end = endD, freq = 'B' ).rename('Dates')
    spread = pd.DataFrame({}, index = df_index)
    
    price1List = [*priceIn1] # Easy way to make list out of Dict Keys
    price2List = [*priceIn2]
    
    p1 = priceIn1[price1List[-1]]['Close']*converstionFactorIn1
    
    if tradeTypeIn == 'Flat' or tradeTypeIn == 'Diff' :
        p2 = priceIn2[price2List[-1]]['Close']*0
    else :
        p2 = priceIn2[price2List[-1]]['Close']*converstionFactorIn2
    spread_temp = pd.merge(p1,p2, how = 'inner', left_index = True, right_index = True)
    spread_temp['spread'] = spread_temp.iloc[:,0] - spread_temp.iloc[:,1]
    spread_temp = spread_temp.iloc[:,2]
    spread_temp = spread_temp[startD:]
    spread = pd.merge(spread,spread_temp,how = 'left', left_index = True, right_index = True).ffill()
    spread[spread.index > spread_temp.index[-1]] =np.nan
    
    listNameOut.append(yearListIn1[-1])
    
    
    for i,j,m in zip(price1List[:-1],price2List[:-1],yearListIn1[:-1]):
        
        tempYear = int('20' + m)   # CAUTION, THIS WILL ONLY WORK IN TH 2000s (FIX LATER)
        tempLastTrade = dt.strptime(expireScheduleIn[(expireScheduleIn['MonthCode']==contractIn) & (expireScheduleIn['Year']== tempYear)]['LastTrade'][0],'%m/%d/%y')
        
        p1 = priceIn1[i]['Close']*converstionFactorIn1
        
        if tradeTypeIn == 'Flat' or tradeTypeIn == 'Diff' :
            p2 = priceIn2[j]['Close']*0
        else :
            p2 = priceIn2[j]['Close']*converstionFactorIn2
        
        spread_temp = pd.merge(p1,p2, how = 'inner', left_index = True, right_index = True)
        spread_temp['spread'] = spread_temp.iloc[:,0] - spread_temp.iloc[:,1]
        spread_temp = spread_temp[:tempLastTrade].copy()
        
        startD_temp = (spread_temp.index[0] - timedelta(weeks = 52)).strftime('%m/%d/%Y')
        endD_temp = spread_temp.index[-1].strftime('%m/%d/%Y')
        df_indexTemp = pd.date_range(start =startD_temp, end = endD_temp, freq = 'B' ).rename('Dates')
        spreadTemp_df = pd.DataFrame({}, index = df_indexTemp)
        
        spread_temp1 = pd.merge(spreadTemp_df,spread_temp['spread'], how ='left', left_index = True, right_index = True).ffill()
        
        index_len = len(spread)
        spread_temp2 = pd.DataFrame(spread_temp1.iloc[-index_len:,:])
        spread_temp2 = spread_temp2.set_index(spread.index)
        spread_temp2.columns = [j]
        spread = pd.merge(spread_temp2,spread,how = 'left', left_index = True, right_index = True)
        listNameOut.append(m)
    
    listNameOut.reverse() # Correcting order of list names
    spread.columns = listNameOut
    
    return spread


def createSpread_Custom(series_info_list, lastTradeIn, main_year_list):
    listNameOut = []

    lastTrade = dt.strptime(lastTradeIn['LastTrade'], '%m/%d/%y')
    startD = (lastTrade - timedelta(weeks=53)).strftime('%m/%d/%Y')
    endD = lastTrade.strftime('%m/%d/%Y')

    df_index = pd.date_range(start=startD, end=endD, freq='B').rename('Dates')
    spread = pd.DataFrame({}, index=df_index)

    current_year_key = main_year_list[-1]
    
    if not series_info_list:
        print("No series_info_list provided. Returning empty DataFrame.")
        return pd.DataFrame({}, index=df_index)

    # === Handle first series (current year) ===
    first_series_info = series_info_list[0]
    first_price_dict = first_series_info['data']
    first_cf = first_series_info['cf']
    first_s_name = first_series_info['series_name']
    first_c_month = first_series_info['contract_month']
    first_series_year_list = first_series_info['year_list']
    full_current_key_first_series = f"{first_s_name}_{first_c_month}{first_series_year_list[-1]}"
    
    if full_current_key_first_series not in first_price_dict:
        print(f"[ERROR] Missing key: {full_current_key_first_series} in {first_s_name}")
        return pd.DataFrame({}, index=df_index)

    first_price_series_data = first_price_dict[full_current_key_first_series]['Close'] * first_cf
    current_spread_df = pd.DataFrame({'spread': first_price_series_data})
    print(f"[INFO] Initial spread for current year: {full_current_key_first_series}")
    print(current_spread_df.head())

    # === Add other series for current year ===
    for series_idx in range(1, len(series_info_list)):
        series_info = series_info_list[series_idx]
        price_dict = series_info['data']
        conversion_factor = series_info['cf']
        s_name = series_info['series_name']
        c_month = series_info['contract_month']
        series_year_list = series_info['year_list']
        full_current_key = f"{s_name}_{c_month}{series_year_list[-1]}"

        if full_current_key not in price_dict:
            print(f"[WARNING] Missing key: {full_current_key} in {s_name}. Skipping.")
            continue

        current_series_data = price_dict[full_current_key]['Close'] * conversion_factor
        temp_col_name = f'temp_series_{series_idx}'

        print(f"[DEBUG] Merging current series {series_idx}: {full_current_key}")
        print(f"  current_spread_df shape before merge: {current_spread_df.shape}")
        print(f"  current_series_data shape: {current_series_data.shape}")

        current_spread_df = pd.merge(
            current_spread_df,
            current_series_data.rename(temp_col_name),
            how='inner',
            left_index=True,
            right_index=True
        )

        print(f"  current_spread_df shape after merge: {current_spread_df.shape}")
        current_spread_df['spread'] += current_spread_df[temp_col_name]
        current_spread_df.drop(columns=[temp_col_name], inplace=True)

    current_spread_df = current_spread_df[startD:]
    print(f"[INFO] Final current_spread_df shape: {current_spread_df.shape}")

    spread = pd.merge(spread, current_spread_df, how='left', left_index=True, right_index=True).ffill()
    print(f"[DEBUG] Spread after merging current year:\n{spread.tail()}")
    
    spread[spread.index > current_spread_df.index[-1]] = np.nan
    listNameOut.append(current_year_key)

    # === Historical years ===
    for year_idx_main, historical_year_label in enumerate(main_year_list[:-1]):
        first_series_info = series_info_list[0]
        first_price_dict = first_series_info['data']
        first_cf = first_series_info['cf']
        first_s_name = first_series_info['series_name']
        first_c_month = first_series_info['contract_month']
        first_series_year_list = first_series_info['year_list']

        if year_idx_main >= len(first_series_year_list):
            print(f"[WARNING] Not enough historical years in {first_s_name}. Skipping {historical_year_label}")
            continue

        historical_year_key = f"{first_s_name}_{first_c_month}{first_series_year_list[year_idx_main]}"
        if historical_year_key not in first_price_dict:
            print(f"[WARNING] Missing historical key: {historical_year_key}")
            continue

        historical_spread_temp = pd.DataFrame({
            'spread': first_price_dict[historical_year_key]['Close'] * first_cf
        })

        for series_idx in range(1, len(series_info_list)):
            series_info = series_info_list[series_idx]
            price_dict = series_info['data']
            conversion_factor = series_info['cf']
            s_name = series_info['series_name']
            c_month = series_info['contract_month']
            series_year_list = series_info['year_list']

            if year_idx_main >= len(series_year_list):
                print(f"[WARNING] Not enough years in {s_name} for year {historical_year_label}. Skipping.")
                continue

            historical_series_key = f"{s_name}_{c_month}{series_year_list[year_idx_main]}"
            if historical_series_key not in price_dict:
                print(f"[WARNING] Missing key: {historical_series_key} in {s_name}")
                continue

            historical_series_data = price_dict[historical_series_key]['Close'] * conversion_factor
            temp_col_name = f'temp_series_hist_{series_idx}'

            print(f"[DEBUG] Merging historical series {series_idx}: {historical_series_key}")
            print(f"  historical_spread_temp shape before merge: {historical_spread_temp.shape}")
            print(f"  historical_series_data shape: {historical_series_data.shape}")

            historical_spread_temp = pd.merge(
                historical_spread_temp,
                historical_series_data.rename(temp_col_name),
                how='inner',
                left_index=True,
                right_index=True
            )

            print(f"  historical_spread_temp shape after merge: {historical_spread_temp.shape}")
            historical_spread_temp['spread'] += historical_spread_temp[temp_col_name]
            historical_spread_temp.drop(columns=[temp_col_name], inplace=True)

        # Reindexing and merging to master spread
        startD_temp = (historical_spread_temp.index[0] - timedelta(weeks=52)).strftime('%m/%d/%Y')
        endD_temp = historical_spread_temp.index[-1].strftime('%m/%d/%Y')
        df_indexTemp = pd.date_range(start=startD_temp, end=endD_temp, freq='B').rename('Dates')
        spreadTemp_df = pd.DataFrame({}, index=df_indexTemp)

        spread_temp1 = pd.merge(spreadTemp_df, historical_spread_temp['spread'], how='left', left_index=True, right_index=True).ffill()

        index_len = len(spread)
        spread_temp2 = pd.DataFrame(spread_temp1.iloc[-index_len:, :])
        spread_temp2.set_index(spread.index, inplace=True)
        spread_temp2.columns = [historical_year_label]

        print(f"[DEBUG] Merging historical spread {historical_year_label} into final spread")
        print(f"  spread_temp2 shape: {spread_temp2.shape}")
        print(f"  spread shape before merge: {spread.shape}")

        spread = pd.merge(spread_temp2, spread, how='left', left_index=True, right_index=True)
        print(f"  spread shape after merge: {spread.shape}")
        listNameOut.append(historical_year_label)

    listNameOut.reverse()
    spread.columns = listNameOut

    print(f"[INFO] Final spread DataFrame:\n{spread.head()}")
    return spread

def _align_and_fill_spread_series(spread_series, master_df_index):
    """
    Aligns a given spread Series to a master DataFrame index,
    fills missing values (ffill), and ensures it matches the master index length.

    Args:
        spread_series (pd.Series): The Series containing spread values to align.
        master_df_index (pd.DatetimeIndex): The reference index (e.g., df_index)
                                            to align the spread Series to.

    Returns:
        pd.Series: The aligned and filled spread Series.
    """
    if spread_series.empty:
        # print(f"DEBUG: Input spread_series is empty. Returning NaN Series.") # Uncomment for more verbose debugging
        return pd.Series(np.nan, index=master_df_index, name='spread_val')

    # Create a temporary full date range covering the spread series
    # Add a buffer (e.g., 52 weeks) to the start for ffill to work if data starts slightly later
    start_date_temp = (spread_series.index.min() - timedelta(weeks=52))
    end_date_temp = spread_series.index.max()
    
    # Ensure start_date_temp is not before an arbitrarily early date to avoid conversion errors
    # (e.g., if a date calculation leads to a year like 0001)
    if start_date_temp < dt(1900, 1, 1):
        start_date_temp = master_df_index.min()

    df_indexTemp = pd.date_range(start=start_date_temp, end=end_date_temp, freq='B').rename('Dates')
    spreadTemp_df = pd.DataFrame(index=df_indexTemp)

    # Merge the temporary spread with the full temporary date range, then ffill
    temp_spread_aligned_initial = pd.merge(spreadTemp_df, spread_series.rename('spread_val'),
                                           how='left', left_index=True, right_index=True)
    temp_spread_aligned = temp_spread_aligned_initial.ffill()

    # Reindex to the master_df_index. This handles both shortening and lengthening.
    final_spread_series = temp_spread_aligned['spread_val'].reindex(master_df_index).ffill()
    final_spread_series.name = 'spread_val'

    # print(f"DEBUG: Aligned spread series shape: {final_spread_series.shape}") # Uncomment for more verbose debugging
    return final_spread_series

def createSpread_Calendar(instrument_cf_list, expireScheduleIn, year1_in, year2_in, years_back_for_history, futuresContractDictIn):
    """
    Calculates a calendar spread for multiple instruments.
    The spread is (Instrument_Year1 - Instrument_Year2) averaged across all instruments.
    The historical data will be the spread for `years_back_for_history` years leading up to year1_in - year2_in
    e.g., CLF25 - CLF26, CLG25 - CLG26 etc., averaged over all chosen instruments.
    """
    print(f"\nDEBUG: --- Entering createSpread_Calendar function ---")
    print(f"DEBUG: Inputs - instrument_cf_list: {instrument_cf_list}, year1_in: {year1_in}, year2_in: {year2_in}, years_back_for_history: {years_back_for_history}")

    current_year_suffix1 = str(year1_in)[-2:]
    current_year_suffix2 = str(year2_in)[-2:]
    print(f"DEBUG: Current year suffixes for spread: {current_year_suffix1}-{current_year_suffix2}")

    # Determine the date range for the spread DataFrame based on current year's expiry for a reference month (e.g., Dec 'Z')
    try:
        # It's May 2025. If year1_in is 2024, using Z2024. If 2025, using Z2025.
        # We need to make sure the expireScheduleIn has the relevant year's data.
        # The logic below attempts to get the LastTrade for Z in year1_in.
        last_trade_ref = expireScheduleIn[(expireScheduleIn['MonthCode'] == 'Z') & (expireScheduleIn['Year'] == year1_in)]['LastTrade'].iloc[0]
        last_trade = dt.strptime(last_trade_ref, '%m/%d/%y')
        print(f"DEBUG: Found last trade date for Z{year1_in}: {last_trade.strftime('%m/%d/%Y')}")
    except IndexError:
        print(f"ERROR: Could not find expiry for Z{year1_in}. Using current date ({dt.now().strftime('%m/%d/%Y')}) as reference for index creation.")
        last_trade = dt.now() # Use current datetime if expiry not found

    startD = (last_trade - timedelta(weeks=53)).strftime('%m/%d/%Y')
    endD = last_trade.strftime('%m/%d/%Y')
    df_index = pd.date_range(start=startD, end=endD, freq='B').rename('Dates')
    print(f"DEBUG: DataFrame index created from {startD} to {endD}. Index length: {len(df_index)}")

    # Generate the list of historical year labels for the columns of the output spread DataFrame.
    historical_spread_years = []
    for i in range(years_back_for_history + 1):
        hist_year1 = year1_in - i
        hist_year2 = year2_in - i
        historical_spread_years.append(f"{str(hist_year1)[-2:]}-{str(hist_year2)[-2:]}")
    print(f"DEBUG: Expected historical spread column names: {historical_spread_years}")
    
    # Initialize main_spread_df with all expected columns filled with 0.0
    main_spread_df = pd.DataFrame(0.0, index=df_index, columns=historical_spread_years)
    print(f"DEBUG: Initial main_spread_df created with columns: {main_spread_df.columns.tolist()}")

    # Process each instrument
    for instrument_info in instrument_cf_list:
        instrument_name = instrument_info['instrument']
        conversion_factor = instrument_info['cf']
        print(f"\nDEBUG: Processing instrument: {instrument_name} with conversion factor: {conversion_factor}")

        # Iterate through all contract months F-Z
        for month_code, month_info in futuresContractDictIn.items():
            # print(f"DEBUG:    Processing month: {month_code}") # Uncomment for more verbose debugging

            # Get historical data for the components of the spread
            years_to_fetch_year1_suffixes = [str(y)[-2:] for y in range(year1_in - years_back_for_history, year1_in + 1)]
            years_to_fetch_year2_suffixes = [str(y)[-2:] for y in range(year2_in - years_back_for_history, year2_in + 1)]
            # print(f"DEBUG:      Fetching prices for {instrument_name} {month_code}. Years for Year1 component: {years_to_fetch_year1_suffixes}, Years for Year2 component: {years_to_fetch_year2_suffixes}") # Uncomment for more verbose debugging
            
            fetched_prices_year1 = getSeasonalPrices(instrument_name, '', month_code, years_to_fetch_year1_suffixes)
            fetched_prices_year2 = getSeasonalPrices(instrument_name, '', month_code, years_to_fetch_year2_suffixes)

            if not fetched_prices_year1 or not fetched_prices_year2:
                print(f"WARNING: Could not fetch data for {instrument_name} {month_code}. Skipping this month for this instrument.")
                continue
            
            # Calculate the spread for each historical year
            for i in range(years_back_for_history + 1):
                hist_year1_full = year1_in - i
                hist_year2_full = year2_in - i
                hist_year_key1 = f"{instrument_name}_{month_code}{str(hist_year1_full)[-2:]}"
                hist_year_key2 = f"{instrument_name}_{month_code}{str(hist_year2_full)[-2:]}"
                
                spread_column_name = f"{str(hist_year1_full)[-2:]}-{str(hist_year2_full)[-2:]}"
                # print(f"DEBUG:      Calculating spread for historical period: {spread_column_name}") # Uncomment for more verbose debugging

                if hist_year_key1 in fetched_prices_year1 and hist_year_key2 in fetched_prices_year2:
                    price1_series = fetched_prices_year1[hist_year_key1]['Close']
                    price2_series = fetched_prices_year2[hist_year_key2]['Close']
                    
                    # print(f"DEBUG:        Fetched price1 series shape: {price1_series.shape}, price2 series shape: {price2_series.shape}") # Uncomment for more verbose debugging

                    # Ensure both series have data
                    if not price1_series.empty and not price2_series.empty:
                        # Combine series to calculate spread, handling potential date mismatches
                        combined_prices = pd.DataFrame({'price1': price1_series, 'price2': price2_series}).dropna()
                        if combined_prices.empty:
                            # print(f"WARNING: No overlapping dates for {hist_year_key1} and {hist_year_key2}. Skipping spread calculation.") # Uncomment for more verbose debugging
                            continue

                        temp_spread = (combined_prices['price1'] - combined_prices['price2']) * conversion_factor
                        # print(f"DEBUG:        Calculated temp_spread for {instrument_name} {month_code}, shape: {temp_spread.shape}") # Uncomment for more verbose debugging
                        
                        # Use the helper function to align and fill the temporary spread
                        final_temp_spread_series = _align_and_fill_spread_series(temp_spread, df_index)
                        
                        # Add the current month's spread for the historical year to the instrument's total for that year
                        main_spread_df[spread_column_name] += final_temp_spread_series.fillna(0)
                        # print(f"DEBUG:        Added {instrument_name} {month_code} spread to main_spread_df[{spread_column_name}]") # Uncomment for more verbose debugging
                    else:
                        print(f"WARNING: Price series for {hist_year_key1} or {hist_year_key2} is empty. Skipping spread calculation for this period.")
                else:
                    print(f"WARNING: Missing data for {hist_year_key1} or {hist_year_key2} in fetched_prices_year1/2. Skipping spread calculation for this period.")
        
    # After iterating through all instruments, average the spread over the number of instruments
    if instrument_cf_list:
        # Custom sort function to put current year last, others in descending order
        current_spread_col_name = f'{current_year_suffix1}-{current_year_suffix2}'
        
        def sort_key(col_name):
            if col_name == current_spread_col_name:
                return (2, col_name) # High tuple value to put it last
            try:
                # Sort historical years in descending order based on the first year in the spread label
                year_part = int(col_name.split('-')[0])
                return (1, -year_part) # Smaller tuple value, and negative year for descending sort
            except ValueError:
                return (0, col_name) # Fallback for unexpected column names

        # Ensure all historical_spread_years are in main_spread_df.columns (they should be due to initialization)
        # Then sort the actual columns of the DataFrame
        ordered_columns = sorted(main_spread_df.columns.tolist(), key=sort_key)
        main_spread_df = main_spread_df[ordered_columns] # Reorder columns
        
        main_spread_df = main_spread_df / len(instrument_cf_list)
        print(f"DEBUG: Divided main_spread_df by number of instruments ({len(instrument_cf_list)}) for averaging.")
    else:
        print("WARNING: No instruments processed, main_spread_df will be empty or all zeros.")

    print(f"DEBUG: Final main_spread_df head:\n{main_spread_df.head()}")
    print(f"DEBUG: Final main_spread_df columns:\n{main_spread_df.columns.tolist()}")
    print(f"DEBUG: --- Exiting createSpread_Calendar function ---")
    return main_spread_df

def createSpread_Quarterly(instrument_cf_list, expireScheduleIn, q1_code, q2_code, years_back, futuresContractDictIn, quarterlyMonthsIn):
    """
    Calculates a quarterly spread for multiple instruments.
    The spread is (Average of Q1 months - Average of Q2 months) for each instrument and then averaged across instruments.
    """
    print(f"\nDEBUG: --- Entering createSpread_Quarterly function ---")
    print(f"DEBUG: Inputs - instrument_cf_list: {instrument_cf_list}, q1_code: {q1_code}, q2_code: {q2_code}, years_back: {years_back}")

    # Determine the date range for the spread DataFrame based on current year's expiry for a reference month (e.g., Dec 'Z')
    current_actual_year = dt.now().year
    latest_year_suffix = str(current_actual_year)[-2:]
    
    try:
        last_trade_ref = expireScheduleIn[(expireScheduleIn['MonthCode'] == 'Z') & (expireScheduleIn['Year'] == current_actual_year)]['LastTrade'].iloc[0]
        last_trade = dt.strptime(last_trade_ref, '%m/%d/%y')
        print(f"DEBUG: Found last trade date for Z{current_actual_year}: {last_trade.strftime('%m/%d/%Y')}")
    except IndexError:
        print(f"ERROR: Could not find expiry for Z{current_actual_year}. Using current date ({dt.now().strftime('%m/%d/%Y')}) as reference for index creation.")
        last_trade = dt.now()

    startD = (last_trade - timedelta(weeks=53)).strftime('%m/%d/%Y')
    endD = last_trade.strftime('%m/%d/%Y')
    df_index = pd.date_range(start=startD, end=endD, freq='B').rename('Dates')
    print(f"DEBUG: DataFrame index created from {startD} to {endD}. Index length: {len(df_index)}")
    
    # Initialize the main spread DataFrame with columns for each historical year.
    all_historical_years_suffix = [str(y)[-2:] for y in range(current_actual_year - years_back, current_actual_year + 1)]
    main_spread_df = pd.DataFrame(0.0, index=df_index, columns=all_historical_years_suffix)
    print(f"DEBUG: Initial main_spread_df created with columns: {main_spread_df.columns.tolist()}")

    q1_months = quarterlyMonthsIn.get(q1_code, [])
    q2_months = quarterlyMonthsIn.get(q2_code, [])
    print(f"DEBUG: Q1 months: {q1_months}, Q2 months: {q2_months}")

    if not q1_months or not q2_months:
        print("ERROR: Invalid quarter codes provided. Returning empty DataFrame.")
        return pd.DataFrame()

    # Process each instrument
    for instrument_info in instrument_cf_list:
        instrument_name = instrument_info['instrument']
        conversion_factor = instrument_info['cf']
        print(f"\nDEBUG: Processing instrument: {instrument_name} with conversion factor: {conversion_factor}")

        # Loop through each year in the historical range
        for year_suffix in all_historical_years_suffix:
            current_full_year = int('20' + year_suffix) # Assuming 2000s for simplicity
            print(f"DEBUG:    Processing year: {current_full_year} ({year_suffix})")

            q1_prices_for_year = []
            q2_prices_for_year = []

            # Fetch Q1 months data for the current year
            # print(f"DEBUG:      Fetching Q1 months data for {current_full_year}") # Uncomment for more verbose debugging
            for month_code in q1_months:
                price_dict = getSeasonalPrices(instrument_name, '', month_code, [year_suffix])

                if price_dict:
                    key = f"{instrument_name}_{month_code}{year_suffix}"
                    if key in price_dict and not price_dict[key]['Close'].empty:
                        q1_prices_for_year.append(price_dict[key]['Close'])
                        # print(f"DEBUG:        Fetched {key} for Q1.") # Uncomment for more verbose debugging
                    else:
                        print(f"WARNING: Missing or empty data for {key} in fetched price dictionary for Q1. Skipping.")
                else:
                    print(f"WARNING: Could not fetch any data for {instrument_name} {month_code} {year_suffix} for Q1. Skipping.")

            # Fetch Q2 months data for the current year
            # print(f"DEBUG:      Fetching Q2 months data for {current_full_year}") # Uncomment for more verbose debugging
            for month_code in q2_months:
                price_dict = getSeasonalPrices(instrument_name, '', month_code, [year_suffix])
                if price_dict:
                    key = f"{instrument_name}_{month_code}{year_suffix}"
                    if key in price_dict and not price_dict[key]['Close'].empty:
                        q2_prices_for_year.append(price_dict[key]['Close'])
                        # print(f"DEBUG:        Fetched {key} for Q2.") # Uncomment for more verbose debugging
                    else:
                        print(f"WARNING: Missing or empty data for {key} in fetched price dictionary for Q2. Skipping.")
                else:
                    print(f"WARNING: Could not fetch any data for {instrument_name} {month_code} {year_suffix} for Q2. Skipping.")
            
            if q1_prices_for_year and q2_prices_for_year:
                # Align and average Q1 prices
                q1_combined = pd.concat(q1_prices_for_year, axis=1).mean(axis=1)
                # print(f"DEBUG:      Q1 combined prices for {current_full_year}, shape: {q1_combined.shape}") # Uncomment for more verbose debugging
                # Align and average Q2 prices
                q2_combined = pd.concat(q2_prices_for_year, axis=1).mean(axis=1)
                # print(f"DEBUG:      Q2 combined prices for {current_full_year}, shape: {q2_combined.shape}") # Uncomment for more verbose debugging

                # Calculate the quarterly spread for this instrument and year
                instrument_quarterly_spread = (q1_combined - q2_combined) * conversion_factor
                # print(f"DEBUG:      Calculated instrument_quarterly_spread for {instrument_name} {year_suffix}, shape: {instrument_quarterly_spread.shape}") # Uncomment for more verbose debugging
                
                # Use the helper function to align and fill
                final_temp_spread_series = _align_and_fill_spread_series(instrument_quarterly_spread, df_index)
                
                # Add this instrument's quarterly spread for the current year to the main spread DataFrame
                main_spread_df[year_suffix] += final_temp_spread_series.fillna(0)
                # print(f"DEBUG:      Added instrument {instrument_name}'s contribution to main_spread_df[{year_suffix}]. Current total shape: {main_spread_df[year_suffix].shape}") # Uncomment for more verbose debugging
            else:
                print(f"WARNING: Insufficient Q1 or Q2 price data for {instrument_name} for year {year_suffix}. Skipping spread calculation for this instrument and year.")

    # After iterating through all instruments, average the spread over the number of instruments
    if instrument_cf_list:
        main_spread_df = main_spread_df / len(instrument_cf_list)
        print(f"DEBUG: Divided main_spread_df by number of instruments ({len(instrument_cf_list)}) for averaging.")
    else:
        print("WARNING: No instruments processed, main_spread_df will be empty or all zeros.")

    # Final column ordering: current year last, others in descending order
    # The columns were initialized in ascending order (current_actual_year - years_back to current_actual_year).
    # We want current year last, and historicals in reverse chronological (descending) order.
    current_year_col_name = str(current_actual_year)[-2:]
    
    # Exclude current year, sort historicals descending
    historical_cols_sorted = sorted([col for col in all_historical_years_suffix if col != current_year_col_name], 
                                    key=lambda x: int(x), reverse=True)
    
    final_column_order = historical_cols_sorted + [current_year_col_name]
    
    # Ensure all expected columns are present (should be, as initialized), then reorder
    for col in final_column_order:
        if col not in main_spread_df.columns:
            main_spread_df[col] = np.nan # Add with NaNs if somehow missed

    main_spread_df = main_spread_df[final_column_order]

    print(f"DEBUG: Final main_spread_df head:\n{main_spread_df.head()}")
    print(f"DEBUG: Final main_spread_df columns:\n{main_spread_df.columns.tolist()}")
    print(f"DEBUG: --- Exiting createSpread_Quarterly function ---")
    return main_spread_df