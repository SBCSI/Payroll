import pandas as pd
import datetime
import numpy as np

def round_time(dt):
    # Calculate the number of minutes past the last 15-minute mark
    minutes = (dt.minute % 15) * 60 + dt.second

    # If the number of minutes is less than 7, round down; otherwise, round up
    if minutes < 7 * 60:
        dt = dt - datetime.timedelta(minutes=dt.minute % 15, seconds=dt.second)
    else:
        dt = dt + datetime.timedelta(minutes=15 - dt.minute % 15, seconds=-dt.second)

    return dt

# Load the Excel file
df = pd.read_excel('C:\\test\\Payroll.xlsx')

# Convert the 'Ticket Date', 'Actual Clock In Time', and 'Actual Clock Out Time' columns to datetime
df['Ticket Date'] = pd.to_datetime(df['Ticket Date'])
df['Actual Clock In Time'] = pd.to_datetime(df['Actual Clock In Time']).apply(round_time)
df['Actual Clock Out Time'] = pd.to_datetime(df['Actual Clock Out Time']).apply(round_time)

# Calculate the total hours worked for each job
df['Total Hours Worked'] = (df['Actual Clock Out Time'] - df['Actual Clock In Time']).dt.total_seconds() / 3600

# Create a list to hold the results
results = []

# Group by 'Employee Name', 'Quote/Job Number Number', 'Agency', and 'Ticket Date'
grouped = df.groupby(['Employee Name', 'Quote/Job Number Number', 'Agency', df['Ticket Date'].dt.date])

for name, group in grouped:
    total_hours = group['Total Hours Worked'].sum()

    # Deduct 30 minutes for lunch break if the employee worked for more than 5 hours
    if total_hours > 5:
        total_hours -= 0.5

    regular_hours = round(min(8, total_hours), 2)
    overtime_hours = round(max(0, total_hours - 8), 2)

    # If the Ticket Date is on a Saturday or Sunday, all hours are overtime
    if group['Ticket Date'].dt.dayofweek.iloc[0] >= 5:
        overtime_hours = round(total_hours, 2)
        regular_hours = 0

    results.append(pd.DataFrame({
        'Employee Name': [name[0]],
        'Quote/Job Number Number': [name[1]],
        'Agency': [name[2]],
        'Ticket Date': [name[3]],
        'Day': [group['Ticket Date'].dt.day_name().iloc[0]],
        'Regular Hours': [regular_hours],
        'Overtime Hours': [overtime_hours],
        'Actual Clock In Time': [group['Actual Clock In Time'].iloc[0]],
        'Actual Clock Out Time': [group['Actual Clock Out Time'].iloc[0]]
    }))

# Concatenate all the results into a single dataframe
result = pd.concat(results)

# Save the result to a new Excel file
result.to_excel('C:\\test\\result.xlsx', index=False)







