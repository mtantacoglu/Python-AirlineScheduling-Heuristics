# -*- coding: utf-8 -*-
"""
Created on Mon March 29 15:12:33 2023

@author: melis.tacoglu
"""


import pandas as pd
import numpy as np

passenger_data = pd.read_excel("Passenger_V2.xlsx")
scheduled_flights_data = pd.read_excel("Scheduled_Flights_V4.xlsx")
new_flights_data = pd.read_excel("New_Flights_for_domainreductionproblem_v2.xlsx")

grouped_passengers = passenger_data.groupby("Destination")

for destination,group  in grouped_passengers:
    first_destination_passenger_df = grouped_passengers.get_group(1)
    second_destination_passenger_df = grouped_passengers.get_group(2)
    third_destination_passenger_df = grouped_passengers.get_group(3)
    
grouped_scheduled_flights = scheduled_flights_data.groupby("Destination")

for destination,group  in grouped_scheduled_flights:
    first_destination_scheduled_df = grouped_scheduled_flights.get_group(1)
    original_first_destination_scheduled_df= first_destination_scheduled_df.copy(deep = True)
    second_destination_scheduled_df = grouped_scheduled_flights.get_group(2)
    third_destination_scheduled_df = grouped_scheduled_flights.get_group(3)

grouped_new_flights = new_flights_data.groupby("Destination")

for destination,group  in grouped_scheduled_flights:
    first_destination_new_df = grouped_new_flights.get_group(1)
    second_destination_new_df = grouped_new_flights.get_group(2)
    third_destination_new_df = grouped_new_flights.get_group(3)
    


# sort passengers based on ascencing order and add ready time to each passenger
def ready_time(arrivals,readytime):
    arrivals.sort_values(by="P Arrival Time", inplace=True)
    arrivals["P Arrival Time"]= arrivals["P Arrival Time"].apply(lambda x: x+ readytime)
    return arrivals

#create arrival departure assignment matrix
def assignment_scheduled(arrivals,departures):
# create an empty dataframe with columns for each flight index
    flight_indices = departures['Scheduled Flights']
    df = pd.DataFrame(columns=flight_indices)

    departures.sort_values(by="S Departure Time", inplace=True)
# loop through each passenger in the arrival data and check their arrival time against each flight's departure time
    for i, row in arrivals.iterrows():
        passenger_index = row['Passenger']
        passenger_arrival_time = row['P Arrival Time']
        for j, dep_row in departures.iterrows():
            flight_index = dep_row['Scheduled Flights']
            flight_departure_time = dep_row['S Departure Time']
            if flight_departure_time >= passenger_arrival_time:
                df.loc[passenger_index, flight_index] = 1
            else:
                df.loc[passenger_index, flight_index] = 0

# fill any missing values with 0
    df = df.fillna(0)

# print the resulting dataframe
    return df
    
def number_of_available_scheduled(arrivals):
    df = arrivals.sum(axis=1)
    return df


def waiting_time_scheduled(arrivals,departures):
    flight_indices = departures['Scheduled Flights']
    passenger_indices = arrivals['Passenger']
    df = pd.DataFrame(columns=flight_indices, index = passenger_indices)

#generate waiting time dataframe
    for i, row in arrivals.iterrows():
        passenger_index = row['Passenger']
        passenger_arrival_time = row['P Arrival Time']
        for j, dep_row in departures.iterrows():
            flight_index = dep_row['Scheduled Flights']
            flight_departure_time = dep_row['S Departure Time']
            if flight_departure_time > passenger_arrival_time:
                df.loc[passenger_index, flight_index] = flight_departure_time-passenger_arrival_time
            else:
                df.loc[passenger_index, flight_index] = 0
# fill any missing values with 0
    df = df.fillna(0)
    return df


def cost_updated_waiting_time_scheduled(df_waiting_scheduled):
    
    cost_updated_waiting_scheduled_df = df_waiting_scheduled.copy()
    
    for flight_index in df_waiting_scheduled.columns:
        for passenger_index in df_waiting_scheduled.index:
            value = df_waiting_scheduled.loc[passenger_index, flight_index]
    
            if value < 4:
               cost_updated_waiting_scheduled_df.loc[passenger_index, flight_index] = value * 1
            elif 4 <= value < 6:
                cost_updated_waiting_scheduled_df.loc[passenger_index, flight_index] = value * 4
            elif 6 <= value < 10:
                cost_updated_waiting_scheduled_df.loc[passenger_index, flight_index] = value * 20
            else:
                cost_updated_waiting_scheduled_df.loc[passenger_index, flight_index] = value * 50
                
    
    return cost_updated_waiting_scheduled_df

def heuristic_scheduled_flights(df_flights,df_passengers,df_waiting,max_waitingtime_parameter):
    wait=0
    #cost calculation parameters and inputs
    cost = cost_updated_waiting_time_scheduled(df_waiting)
    total_waiting_scheduled = 0
    counter_s = 0
     
# create a new DataFrame with zeros

    df_result = pd.DataFrame(np.zeros((len(df_passengers), len(df_flights))), index = df_passengers['Passenger'], columns=df_flights['Scheduled Flights'])
    
    df_passengers.set_index("Passenger Index",inplace=True)
    df_flights.set_index("Flight Index",inplace=True)
    
    assignment_df = assignment_scheduled(df_passengers, df_flights)
    
    
# loop over all passengers and find the maximum waiting time for each one

    for passenger_index, row in df_passengers.iterrows():
        min_waiting_time = 10
        min_waiting_flight_index = 0
        for flight_index in df_flights['Scheduled Flights']:
            waiting_time = df_waiting.loc[passenger_index,flight_index]
            if (assignment_df.loc[passenger_index, flight_index]==1) and (waiting_time <= min_waiting_time) and (max_waitingtime_parameter >= waiting_time) and (waiting_time > 0):
                min_waiting_time = waiting_time
                min_waiting_flight_index = flight_index
            else:
                min_waiting_flight_index = 0

    # check if the flight has available capacity and update the result accordingly
            if min_waiting_flight_index > 0 and (df_flights.loc[df_flights['Scheduled Flights'] == min_waiting_flight_index, 'Capacity'].values[0] > 0):
                total_waiting_scheduled = total_waiting_scheduled + cost.loc[passenger_index,min_waiting_flight_index]
                counter_s = counter_s + 1
                wait = wait +min_waiting_time
                df_result.loc[passenger_index, min_waiting_flight_index] = 1
            # delete passengers that are assigned to the scheduled flights
                df_passengers.drop( passenger_index,axis = 0,inplace = True)
                df_flights.loc[df_flights['Scheduled Flights'] == min_waiting_flight_index, 'Capacity'] -= 1
                if (df_flights.loc[df_flights['Scheduled Flights'] == min_waiting_flight_index, 'Capacity'].values[0] == 0):
                    df_flights.drop( min_waiting_flight_index,axis = 0,inplace = True)
                    df_waiting.drop(min_waiting_flight_index,axis = 1,inplace = True)
            

    return df_result,total_waiting_scheduled,counter_s, wait


def waiting_time_new(arrivals,departures):
    flight_indices = departures['New Flights']
    passenger_indices = arrivals['Passenger']
    df = pd.DataFrame(columns=flight_indices, index = passenger_indices)

    for i, row in arrivals.iterrows():
        passenger_index = row['Passenger']
        passenger_arrival_time = row['P Arrival Time']
        for j, dep_row in departures.iterrows():
            flight_index = dep_row['New Flights']
            flight_departure_time = dep_row['N Departure Time']
            if flight_departure_time > passenger_arrival_time:
                df.loc[passenger_index, flight_index] = flight_departure_time-passenger_arrival_time
            else:
                df.loc[passenger_index, flight_index] = 0

# fill any missing values with 0
    df = df.fillna(0)

    return df
 #uptade dataframe based on incremental cost 

def cost_updated_waiting_time_new(df_waiting_new):
    
    cost_updated_waiting_new_df = df_waiting_new.copy()
    
    for flight_index in df_waiting_new.columns:
        for passenger_index in df_waiting_new.index:
            value = df_waiting_new.loc[passenger_index, flight_index]
    
            if value < 4:
                cost_updated_waiting_new_df.loc[passenger_index, flight_index] = value * 1
            elif 4 <= value < 6:
                cost_updated_waiting_new_df.loc[passenger_index, flight_index] = value * 4
            elif 6 <= value < 10:
                cost_updated_waiting_new_df.loc[passenger_index, flight_index] = value * 20
            else:
                cost_updated_waiting_new_df.loc[passenger_index, flight_index] = value * 50
                
    
    return cost_updated_waiting_new_df

def assignment_new(arrivals,departures):
# create an empty dataframe with columns for each flight index
    flight_indices = departures['New Flights']
    df = pd.DataFrame(columns=flight_indices)

    departures.sort_values(by="N Departure Time", inplace=True)
# loop through each passenger in the arrival data and check their arrival time against each flight's departure time
    for i, row in arrivals.iterrows():
        passenger_index = row['Passenger']
        passenger_arrival_time = row['P Arrival Time']
        for j, dep_row in departures.iterrows():
            flight_index = dep_row['New Flights']
            flight_departure_time = dep_row['N Departure Time']
            if flight_departure_time >= passenger_arrival_time:
                df.loc[passenger_index, flight_index] = 1
            else:
                df.loc[passenger_index, flight_index] = 0

    df = df.fillna(0)
    return df

def heuristic_new_flights(df_new_flights,df_passengers,max_waitingtime_parameter,df_scheduled_flights,flight_duration_time, waiting_time_airport, buffer_time , waiting_dataframe):

    wait_n = 0

    df_new_flights.set_index("New Flight Index",inplace=True)
    
    assignment_df = assignment_new(df_passengers, df_new_flights)
    
#add flihgt duration time for each scheduled flight    
#    df_scheduled_flights["S Departure Time"] = df_scheduled_flights["S Departure Time"] + flight_duration_time
    
    b_time = int(buffer_time)
    wait = int(waiting_time_airport)
#create initial eligible new flight dataframe
    for _, row in df_scheduled_flights.iterrows():
        time= row ["S Departure Time"]
        mask = ((time - b_time <= df_new_flights["N Departure Time"] )& (df_new_flights["N Departure Time"]<= time + b_time + wait))
        df_new_flights = df_new_flights.loc[~mask]
    for _, row in df_scheduled_flights.iterrows():
        time= row ["S Departure Time"]        
        mask = ((time + wait - b_time <= df_new_flights["N Departure Time"]) & (df_new_flights["N Departure Time"]<= time+ wait + b_time))
        df_new_flights = df_new_flights.loc[~mask]
        
    df_waiting = waiting_time_new(df_passengers,df_new_flights)
    
    #cost calculation parameters and inputs
    cost = cost_updated_waiting_time_new(waiting_dataframe)
    total_waiting_new = 0
    counter_n= 0
    
 # create a new DataFrame with zeros  
    df_result = pd.DataFrame(np.zeros((len(df_passengers), len(df_new_flights))), index = df_passengers['Passenger'], columns=df_new_flights['New Flights'])
   
    # loop over all passengers and find the maximum waiting time for each one
    
    for passenger_index, row in df_passengers.iterrows():
        min_waiting_time = 10
        min_waiting_flight_index = 0
        for flight_index in df_new_flights['New Flights']:
            waiting_time = df_waiting.loc[passenger_index,flight_index]
            if (assignment_df.loc[passenger_index, flight_index]==1) and (waiting_time <= min_waiting_time) and (max_waitingtime_parameter >= waiting_time) and (waiting_time > 0):
                min_waiting_time = waiting_time
                min_waiting_flight_index = flight_index
            else:
                min_waiting_flight_index = 0
 
#update eligible new flights when passenger assigned to new flight                
            if min_waiting_flight_index > 0:  
                deleted_flight_list = []
                for i,row in df_new_flights.iterrows():
                    selected_new_flight_time= int(df_new_flights.loc[df_new_flights['New Flights'] == min_waiting_flight_index, 'N Departure Time'].values[0])
                    new_flight_times = int(df_new_flights.loc[df_new_flights['New Flights'] == i, 'N Departure Time'].values[0])
                    if ((selected_new_flight_time - b_time) <= new_flight_times <= (selected_new_flight_time + b_time) or (selected_new_flight_time + wait -b_time ) <= new_flight_times <= (selected_new_flight_time + wait + b_time)):
                        if (min_waiting_flight_index != i) :
                            deleted_flight_list.append(i)
                            for col in df_waiting.columns:
                                if col in deleted_flight_list:
                                    df_waiting[col].values[:]=0
                                    deleted_flight_list = []
                print(deleted_flight_list)
#assign passeneger to new flight                
            if min_waiting_flight_index > 0 and (df_new_flights.loc[df_new_flights['New Flights'] == min_waiting_flight_index , 'Capacity'].values[0] > 0):

                #waiting time calculation
                wait_n = wait_n + min_waiting_time
                #cost calculation
                total_waiting_new = total_waiting_new + cost.loc[passenger_index,min_waiting_flight_index]
                counter_n = counter_n + 1                
                  
            #passenger flight assignment
                df_result.loc[passenger_index, min_waiting_flight_index] = 1
            # delete passengers that are assigned to the new flights
                df_passengers.drop( passenger_index,axis = 0,inplace = True)
                df_new_flights.loc[df_new_flights['New Flights'] == min_waiting_flight_index, 'Capacity'] -= 1

               #if new flight capacity is zero, drop from the new flight and waiting dataframes         
                if (df_new_flights.loc[df_new_flights['New Flights'] == min_waiting_flight_index, 'Capacity'].values[0] == 0):
                    
                   df_new_flights.drop( min_waiting_flight_index,axis = 0,inplace = True)
                   df_waiting.drop(min_waiting_flight_index,axis = 1,inplace = True)
                         
  # check if the flight has available capacity and update the result accordingly
    return df_result,total_waiting_new,counter_n, wait_n

def heuristic(arrivals,readytime,scheduled,new,maximum_waiting_time_parameter_s,maximum_waiting_time_parameter_n,original_scheduled,flight_duration_time,waiting_time_airport,buffer_time):
    
    
    passenger_ready_time = ready_time(arrivals,readytime)
    
    passenger_arrivals = passenger_ready_time.copy(deep = True)

    wt_scheduled= waiting_time_scheduled(arrivals,scheduled)
    
    wt_scheduled_copy= wt_scheduled.copy(deep = True)

    passenger_scheduled_flights ,total_waiting_scheduled,counter_s, wait = heuristic_scheduled_flights(scheduled, arrivals, wt_scheduled,maximum_waiting_time_parameter_s)
    
    wt_new = waiting_time_new(arrivals,new)
    
    wt_new_copy=wt_new.copy(deep = True)
    
    passenger_new_flights , total_waiting_new , couneter_n , wait_n = heuristic_new_flights(new,arrivals,maximum_waiting_time_parameter_n,original_scheduled,flight_duration_time,waiting_time_airport,buffer_time,wt_new_copy)
    
    passenger_scheduled_flights.to_excel("passenger_scheduled_flights_fifo.xlsx", sheet_name="passenger_scheduled_flights")
    
    passenger_new_flights.to_excel("passenger_new_flights_fifo.xlsx", sheet_name="passenger_new_flights")

    return passenger_arrivals, wt_scheduled_copy ,passenger_scheduled_flights, wt_new_copy, passenger_new_flights,total_waiting_scheduled,wait ,counter_s,total_waiting_new , wait_n , couneter_n

# to generate arrival based on poisson, set the lambda parameter
lambda_param = 15


# Generate a sample of Poisson-distributed numbers
sample_size = 1100
numbers = np.random.poisson(lambda_param, sample_size)

# Round the numbers to the nearest integer
numbers = np.round(numbers)

# Clip the numbers to be within the desired range of 1 to 23
numbers = np.clip(numbers, 1, 20)

# Insert values into the "Numbers" column of the existing dataframe
first_destination_passenger_df["P Arrival Time"] = numbers

results = heuristic(first_destination_passenger_df,1,first_destination_scheduled_df,first_destination_new_df,10,10,original_first_destination_scheduled_df,1,2,1)
    
