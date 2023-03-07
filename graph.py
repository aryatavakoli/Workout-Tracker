import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

def read_data(file_path):
    """
    Read the data from a CSV file and return a pandas DataFrame.
    """
    # Removing unnecessary columns
    df = pd.read_csv(file_path, usecols=['Date', 'Workout Name', 'Exercise Name', 'Weight', 'Reps', 'Sets', 'Notes'])

    # Replacing missing values with median
    df['Weight'].fillna(df['Weight'].median(), inplace=True)
    df['Reps'].fillna(df['Reps'].median(), inplace=True)
    df['Sets'].fillna(df['Sets'].median(), inplace=True)

    # Dropping duplicated rows
    df.drop_duplicates(inplace=True)

    # Converting 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Sorting by 'Date'
    df.sort_values(by='Date', inplace=True)

    return df

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_metric_over_time(df, metric_name, metric_func, min_exercises=0, last_x_days=None):
    """
    Plot a metric over time for each exercise that has been done at least min_exercises times over last_x_days.
    
    Args:
        df (pandas.DataFrame): The DataFrame to plot.
        metric_name (str): The name of the metric to plot.
        metric_func (callable): The function used to calculate the metric.
        min_exercises (int): The minimum number of times an exercise must have been done to be plotted. Default is 100.
        last_x_days (int): Filter workouts by the last x days
    Returns:
        None
    """
    groups = df.groupby('Exercise Name')
    # Filter groups to only include exercises that have been done at least min_exercises times
    exercise_counts = groups.size()
    popular_exercises = exercise_counts[exercise_counts >= min_exercises].index
    groups = [group for exercise, group in groups if exercise in popular_exercises]

    for group in groups:
        # Filter out rows with missing weight or reps
        group = group.dropna(subset=['Weight', 'Reps'])

        # Filter by last_x_days if specified
        if last_x_days:
            max_date = group['Date'].max()
            last_x_days_filter = group['Date'] >= (max_date - pd.Timedelta(days=last_x_days))
            group = group[last_x_days_filter]

        # Calculate the metric for the group
        group[metric_name] = metric_func(group)

        # Group the data by date and get the maximum value of the metric for each date
        date_groups = group.groupby('Date')
        max_metric = date_groups[metric_name].max()

        # Convert dates to Unix timestamp for plotting
        x = mdates.date2num(max_metric.index)

        # Plot the data
        plt.figure(figsize=(10, 5))
        plt.plot(max_metric.index, max_metric.values, label=f'{group["Exercise Name"].iloc[0]} {metric_name}')
        plt.plot(max_metric.index, np.polyval(np.polyfit(x, max_metric.values, 1), x), color='red') # Add line of best fit
        plt.title(f'{group["Exercise Name"].iloc[0]} {metric_name} Over Time')
        plt.xlabel('Date')
        plt.ylabel(metric_name)
        plt.legend()
        plt.tight_layout()


def plot_workouts_per_week(df, last_x_weeks):
    """
    Plot the number of workouts per week for the last x weeks.
    """
    end_date = df['Date'].max()
    start_date = end_date - pd.DateOffset(weeks=last_x_weeks)
    df_last_x_weeks = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    week_groups = df_last_x_weeks.groupby(pd.Grouper(key='Date', freq='W'))
    workouts_per_week = week_groups['Workout Name'].nunique()

    # Sort the dates before plotting the bars
    workouts_per_week = workouts_per_week.sort_index()

    plt.figure(figsize=(10, 5))
    plt.bar(workouts_per_week.index, workouts_per_week.values, width=0.9, edgecolor='black')
    plt.title(f'Workouts Per Week for the Last {last_x_weeks} Weeks')
    plt.xlabel('Week')
    plt.ylabel('Number of Workouts')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()



def calc_best_set(group):
    return group['Weight'] * group['Reps']


def calc_total_volume(group):
    return group['Weight'] * group['Reps'] * group['Sets']


def calc_max_consecutive_reps(group):
    return (group['Reps'].diff() != 1).cumsum() * (group['Reps'] == 1)


def calc_one_rep_max(group):
    return group['Weight'] * (1 + 0.0333 * group['Reps'])


if __name__ == '__main__':
    file_path = 'example_data.csv'
    df = read_data(file_path)

    #plot_metric_over_time(df, 'Best Set', calc_best_set)
    #plot_metric_over_time(df, 'Total Volume', calc_total_volume)
    #plot_metric_over_time(df, 'Max Consecutive Reps', calc_max_consecutive_reps)
    plot_metric_over_time(df, '1RM', calc_one_rep_max)

    plot_workouts_per_week(df,5)

    plt.show()
