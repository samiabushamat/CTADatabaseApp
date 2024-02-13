# Overview: Python Application that has the user input a different number of command that do various number of tasks with the CTA data
# Sami Abushamat
# 1/31/2024

import sqlite3
import matplotlib.pyplot as plt
import math

# SQL queries as global constants so that they are not changed
# Also cleans up functions to store all together
query_one = "SELECT DISTINCT Stations.Station_ID, Stations.Station_Name FROM Stations WHERE Stations.Station_Name LIKE ? ORDER BY Stations.Station_Name ASC;"
query_two_a = "SELECT SUM(Num_Riders) FROM Stations Join Ridership WHERE Station_Name = ? AND Ridership.Station_ID = Stations.Station_ID AND Ridership.Type_Of_Day = 'W';"
query_two_b = "SELECT SUM(Num_Riders) FROM Stations Join Ridership WHERE Station_Name = ? AND Ridership.Station_ID = Stations.Station_ID AND Ridership.Type_Of_Day = 'A';"
query_two_c = "SELECT SUM(Num_Riders) FROM Stations Join Ridership WHERE Station_Name = ? AND Ridership.Station_ID = Stations.Station_ID AND Ridership.Type_Of_Day = 'U';"
query_two_d = "SELECT SUM(Num_Riders) FROM Stations Join Ridership WHERE Station_Name = ? AND Ridership.Station_ID = Stations.Station_ID;"
query_three_a = "SELECT Stations.Station_Name, SUM(Ridership.Num_Riders) AS Total_Riders FROM Stations JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID WHERE Ridership.Type_Of_Day = 'W' GROUP BY Stations.Station_Name ORDER BY Total_Riders DESC;"
query_three_b = "SELECT SUM(Num_Riders) AS Total_Riders FROM Ridership  WHERE Type_Of_Day = 'W';"
query_four_a = "SELECT Line_ID FROM Lines WHERE LOWER(Color) = ?"
query_four_b = "SELECT Stops.Stop_Name, Stops.Direction, Stops.ADA FROM Stops JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID JOIN Lines on StopDetails.Line_ID = Lines.Line_ID WHERE LOWER(Lines.Color) = ? AND LOWER(Stops.Direction) = ? ORDER BY Stops.Stop_Name"
query_five_a = "SELECT Lines.Color, Stops.Direction, COUNT(*) AS Stops_Count FROM Lines JOIN StopDetails ON Lines.Line_ID = StopDetails.Line_ID JOIN Stops ON StopDetails.Stop_ID = Stops.Stop_ID GROUP BY Lines.Color, Stops.Direction ORDER BY Lines.Color ASC, Stops.Direction ASC;"
query_five_b = "SELECT COUNT(*) FROM Stops;"
query_six = "SELECT strftime('%Y',Ride_Date) AS Year, SUM(Num_Riders) AS Total_Riders FROM Stations JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID WHERE Station_Name = ? GROUP BY Year ORDER BY Year;"
query_seven = "SELECT strftime('%m',Ride_Date) AS Month,strftime('%m/%Y',Ride_Date) AS Date, SUM(Num_Riders) AS Total_Riders FROM Stations JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID WHERE Station_Name = ? AND strftime('%Y', Ride_Date) = ? GROUP BY Month ORDER BY Month;"
query_eight = "SELECT strftime('%Y-%m-%d',Ride_Date) AS Date, SUM(Num_Riders) AS Daily_Riders FROM Stations JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID WHERE Station_Name = ? AND strftime('%Y', Ride_Date) = ? GROUP BY Date ORDER BY Date;"
query_nine = "SELECT DISTINCT Stations.Station_Name, Latitude, Longitude FROM Stops JOIN Stations ON Stations.Station_ID = Stops.Station_ID  WHERE ? <= Latitude AND Latitude <= ? AND ? <= Longitude AND Longitude <= ? ORDER BY Station_Name"

##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")

    # Executing the script for the number of stations
    dbCursor.execute("Select count(*) From Stations;")
    stations_result = dbCursor.fetchone();

    # Executing the script for the number of stops
    dbCursor.execute("Select count(*) From Stops;")
    stops_result = dbCursor.fetchone();

    # Executing the script for the number of ride entries
    dbCursor.execute("Select count(*) From Ridership;")
    ridership_result = dbCursor.fetchone();

    # Executing the script for the earliest date
    dbCursor.execute("Select strftime('%Y-%m-%d', Ride_Date) As Date From Ridership Order by Ride_Date LIMIT 1;")
    earliest_date = dbCursor.fetchone();

    # Executing the script for the latest date
    dbCursor.execute("Select strftime('%Y-%m-%d', Ride_Date) As Date From Ridership Order by Ride_Date DESC LIMIT 1;")
    latest_date = dbCursor.fetchone();

    # Executing the script for the number of riders
    dbCursor.execute("Select SUM(Num_Riders)  From Ridership;")
    total_result = dbCursor.fetchone();


    # Printing out all the data
    print("  # of stations:", f"{stations_result[0]:,}")
    print("  # of stops:", f"{stops_result[0]:,}")
    print("  # of ride entries:", f"{ridership_result[0]:,}")
    print("  date range:", f"{earliest_date[0]} - {latest_date[0]}")
    print("  Total ridership:", f"{total_result[0]:,}")
    print()

##################################################################  
#
# command_one
#
# Given a connection to the CTA database, executes one
# SQL query based on the users input 
#
def command_one(dbConn):
    # prompt for user input
    print()
    user = input("Enter partial station name (wildcards _ and %): ")
    # excecute query
    dbCursor = dbConn.cursor()
    dbCursor.execute(query_one, (user,))
    result = dbCursor.fetchall();

    # check if empty
    if not result:
        print("**No stations found...")
        print()

    # print all stations
    for row in result:
        print("%s : %s" %(row[0],row[1]))
    
    print()

##################################################################  
#
# command_two
#
# Given a connection to the CTA database, executes four sql queries
# SQL query based on the users input and displays some data ab the days of the week
# and the number of riders s
#
def command_two(dbConn):
    dbCursor = dbConn.cursor()
    print()
    # prompt user
    user = input("Enter the name of the station you would like to analyze:")

    # sql query #1 for weekday ridership
    dbCursor.execute(query_two_a, (user,))
    a = dbCursor.fetchone();

    # sql query #2 for saturday ridership
    dbCursor.execute(query_two_b, (user,))
    b = dbCursor.fetchone();

    # sql query #3 for sunday + holiday ridership
    dbCursor.execute(query_two_c, (user,))
    c = dbCursor.fetchone();

    # sql query #4 for total ridership
    dbCursor.execute(query_two_d, (user,))
    d = dbCursor.fetchone();

    # checking if the data set was empty
    if not a[0]:
        print(" **No data found...")
        print()
        return
    
    # getting the percentages
    a_percent = a[0] / d[0]
    b_percent = b[0] / d[0]
    c_percent = c[0] / d[0]

    # printing out the stats in correct format
    print(" Percentage of ridership for the %s station: " %(user))
    print("  Weekday ridership:", f"{a[0]:,}","(%.2f%%)" %(a_percent * 100))
    print("  Saturday ridership:", f"{b[0]:,}","(%.2f%%)" %(b_percent * 100) )
    print("  Sunday/holiday ridership:", f"{c[0]:,}","(%.2f%%)" %(c_percent * 100))
    print("  Total ridership:", f"{d[0]:,}")
    print()

##################################################################  
#
# command_three
# Given a connection to the CTA database, executes two sql queries one
# that finds the  percentage of riderships on the weekdays that are at each station
#
def command_three(dbConn):
    dbCursor = dbConn.cursor()

    # sql query for total ridership on weekdays for each station
    dbCursor.execute(query_three_a)
    result = dbCursor.fetchall();

    # sql query for total ridership on weekdays for all stations
    dbCursor.execute(query_three_b)
    total = dbCursor.fetchone();

    # printing out data with its percentage
    print("Ridership on Weekdays for Each Station")
    for row in result:
        percentage = row[1] / total[0]
        print("%s : %s (%.2f%%)" % (row[0], f"{row[1]:,}", percentage * 100))

    print()

##################################################################  
#
# command_four
# Given a connection to the CTA database, user inputs a line color and direction
# and it outputs all the stop in that direction on that color and if it is ADA 
#
def command_four(dbConn):
    
    # prompts user
    print()
    line = input("Enter a line color (e.g. Red or Yellow):").lower()

    # sql query that finds the users inputted line
    dbCursor = dbConn.cursor()
    dbCursor.execute(query_four_a,(line,))
    line_result = dbCursor.fetchone();

    # checking if none found
    if not line_result:
        print(" **No such line...")
        print()
        return
    
    # prompting user for direction
    direction = input(" Enter a direction (N/S/W/E): ").lower()

    # sql query #2 that finds all the stops in that direction and if they are accesible
    dbCursor.execute(query_four_b,(line,direction))
    direction_result = dbCursor.fetchall();

    # checkin if none found
    if not direction_result:
        print(" **That line does not run in the direction chosen...")
        print()
        return
    
    # printing out all stops and if they are accessible or not
    for row in direction_result:
        if(row[2] == 1):
            print("%s : direction = %c (handicap accessible)" %(row[0],row[1]))
        else:
            print("%s : direction = %c (not handicap accessible)" %(row[0],row[1]))
    print()

##################################################################  
#
# command_five
# Given a connection to the CTA database, Finds all the stops for each colored line
# Gives the percentage of stops out of total for each station
# 
#
def command_five(dbConn):
    # sql query that finds stops for each color
    dbCursor = dbConn.cursor()
    dbCursor.execute(query_five_a)
    stops = dbCursor.fetchall();

    # second sql query to find total number of stops
    dbCursor.execute(query_five_b)
    total_stops = dbCursor.fetchone();

    # printing out data
    print("Number of Stops For Each Color By Direction")
    for row in stops:
        print("%s going %c : %d (%.2f%%)" %(row[0],row[1],row[2],row[2]/total_stops[0] * 100))

##################################################################  
#
# command_six
# Given a connection to the CTA database,checks if a station exist and
# finds the number of ridership at that station every year
# Can plot the data
#
def command_six(dbConn):
    # vars
    years_list = []
    totals_list = []
    
    # prompting user for station name
    print()
    user = input("Enter a station name (wildcards _ and %): ")

    # sql query that checks if station exist 
    dbCursor = dbConn.cursor()
    dbCursor.execute(query_one, (user,))
    result = dbCursor.fetchall();

    # checking if no or too many stations
    if not result:
        print("**No station found...")
        print()
        return
    if len(result) > 1:
        print("**Multiple stations found...")
        print()
        return
    
    # executing second sql query
    dbCursor.execute(query_six,(result[0][1],))
    yearly = dbCursor.fetchall();

    # printing out data
    print("Yearly Ridership at %s" %(result[0][1]))
    for row in yearly:
        years_list.append(row[0])
        totals_list.append(row[1])
        print("%s : %s" %(row[0],f"{row[1]:,}"))

    # prompting for plot
    print()
    plot = input("Plot? (y/n) ")
    print() 

    # plotting graph
    if(plot == "y"):
        plt.plot(years_list,totals_list)
        plt.xlabel('Year')
        plt.ylabel('Number of Riders')
        plt.title('Yearly Ridership At %s Station' %(result[0][1],))
        plt.show()
    else:
        return
        
##################################################################  
#
# command_seven
# Given a connection to the CTA database, it prompts the user for a station and a year
# and returns the data for riders each month
# Can be plotted
#
def command_seven(dbConn):
    # vars
    month_list = []
    totals_list = []
    print()

    # prompting user input
    station = input("Enter a station name (wildcards _ and %):")
    
    # executing sql query to find the station 
    dbCursor = dbConn.cursor()
    dbCursor.execute(query_one, (station,))
    result = dbCursor.fetchall();

    # checking if no or too many stations
    if not result:
        print(" **No station found...")
        print()
        return
    if len(result) > 1:
        print(" **Multiple stations found...")
        print()
        return
    
    # setting station name
    station_name = result[0][1]

    # prompting for year
    year = input(" Enter a year: ")

    print("Monthly Ridership at %s for %s" %(station_name,year))

    # second sql query that gets the ridership for each month of the year at the certain station 
    dbCursor.execute(query_seven,(station_name,year,))
    monthly = dbCursor.fetchall();

    # printing data
    for row in monthly:
        month_list.append(row[0])
        totals_list.append(row[2])
        print("%s : %s" %(row[1],f"{row[2]:,}"))

    # prompting user for plot
    print()
    plot = input("Plot? (y/n) ")
    print()

    # plotting graph
    if(plot == "y"):
        plt.plot(month_list,totals_list)
        plt.xlabel('Month')
        plt.ylabel('Number of Riders')
        plt.title('Monthly Ridership At %s Station (%s)' %(station_name,year))
        plt.show()
    else:
        return

##################################################################  
#
# command_eight
# Given a connection to the CTA database, runs 3 sql queries to find the two station and
# all the number of riders each day and compare and plot
# Can be plotted
#
def command_eight(dbConn):
    # variables
    days = []
    station_one_riders = []
    station_two_riders = []
    dbCursor = dbConn.cursor()

    # prompting user
    print()
    year = input("Year to compare against? ")
    print()
    station_one = input("Enter station 1 (wildcards _ and %): ")

    # checking if the station exists
    dbCursor.execute(query_one,(station_one,))
    station_one_result = dbCursor.fetchall();

    # checking if no station
    if not station_one_result:
        print("**No station found...")
        print()
        return
    # checking if more than one station
    if len(station_one_result) > 1:
        print("**Multiple stations found...")
        print()
        return
    
    # set variables from data
    station_one_name = station_one_result[0][1]
    station_one_id = station_one_result[0][0]
    print()

    # prompting the second station
    station_two = input("Enter station 2 (wildcards _ and %): ")

    # checking if second station exists
    dbCursor.execute(query_one,(station_two,))
    station_two_result = dbCursor.fetchall();

    # checking no station
    if not station_two_result:
        print("**No station found...")
        print()
        return
    
    # checking if more than one station
    if len(station_two_result) > 1:
        print("**Multiple stations found...")
        print()
        return
    
    # setting variables
    station_two_name = station_two_result[0][1]
    station_two_id = station_two_result[0][0]

    # retreiving each day from the user inputted year
    dbCursor.execute(query_eight,(station_one_name,year,))
    station_one_days = dbCursor.fetchall();

    dbCursor.execute(query_eight,(station_two_name,year,))
    station_two_days = dbCursor.fetchall();

    # print the first and last 5 days
    print("Station 1: %s %s" %(station_one_id,station_one_name))
    if station_one_days:
        for row in station_one_days[:5]:
            print("%s %s" %(row[0],row[1]))
        for row in station_one_days[-5:]:
            print("%s %s" %(row[0],row[1]))
    print("Station 2: %s %s" %(station_two_id,station_two_name))
    if station_two_days:
        for row in station_two_days[:5]:
            print("%s %s" %(row[0],row[1]))
        for row in station_two_days[-5:]:
            print("%s %s" %(row[0],row[1]))
    print()

    # adding data to list for plot
    for row in station_one_days:
        days.append(len(days)+1)
        station_one_riders.append(row[1])
    for row in station_two_days:
        station_two_riders.append(row[1])


    # prompting plot
    plot = input("Plot? (y/n) ")
    print()

    # plotting the two stations
    if(plot == "y"):
        plt.plot(days,station_one_riders, label = station_one_name, color = 'blue')
        plt.plot(days,station_two_riders, label = station_two_name, color = 'orange')

        plt.xlabel('Day')
        plt.ylabel('Number of Riders')
        plt.title("Ridership Each Day of %s" %(year))
        plt.legend()
        plt.show()
    else:
        return
    
##################################################################  
#
# command_nine
# Given a connection to the CTA database, it executes a sql query to find all the stations within a mile
# of the users latitude and longitude inputted
#
#
def command_nine(dbConn):
    # vars
    x = []
    y = []
    names = []

    #prompting the user for lat and long and checking if they are within the bounds of chicago
    print()
    lat = input("Enter a latitude: ")
    if float(lat) < 40 or float(lat) > 43:
        print("**Latitude entered is out of bounds...")
        print()
        return
    
    long = input("Enter a longitude: ")
    if float(long)< -88 or float(long ) > -87:
        print("**Longitude entered is out of bounds...")
        print()
        return
    
    # calculating the bounds
    lat_lower = round(float(lat) - (1 / 69),3)
    lat_upper = round(float(lat) + (1 / 69),3)
    long_upper = round(float(long) - (1/51),3)
    long_lower = round(float(long) + (1/51),3)

    # executing the sql query
    dbCursor = dbConn.cursor()
    dbCursor.execute(query_nine,(str(lat_lower),str(lat_upper),str(long_upper),str(long_lower)))
    result = dbCursor.fetchall();

    # check if empty
    if not result:
        print("**No stations found...")
        print()
        return
    
    print()
    print("List of Stations Within a Mile")
    # printing the stations within the mile and their coordinates
    for row in result:
        print(f"{row[0]} : ({float(row[1]):}, {float(row[2]):})".rstrip('0').rstrip('.'))

    # prompting the plot question
    print()
    plot = input("Plot? (y/n) ")
    print()

    # if user wants plot
    if(plot == "y"):
        # set image and dimensions and labels 
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        plt.imshow(image, extent=xydims)
        plt.title("Stations Near You")
        plt.plot(x, y)
        # add the data to the graph
        for row in result:
            plt.annotate(row[0], (row[2], row[1]), textcoords="offset points", xytext=(0, 5), ha='center')
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()

##################################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)

command = input("Please enter a command (1-9, x to exit): ")

# loop for the users input
while(command != "x"):
    if command == "1":
        command_one(dbConn)
    elif command == "2":
        command_two(dbConn)
    elif command == "3":
        command_three(dbConn)
    elif command == "4":
        command_four(dbConn)
    elif command == "5":
        command_five(dbConn)
    elif command == "6":
        command_six(dbConn)
    elif command == "7":
        command_seven(dbConn)
    elif command == "8":
        command_eight(dbConn)
    elif command == "9":
        command_nine(dbConn)
    else:
        print("**Error, unknown command, try again...")
        print()

    command = input("Please enter a command (1-9, x to exit): ")

#
# done
#
