import csv
import datetime


def get_header(file):
    header = []


def get_all_days_attended_in_period(data_rows, year, month):

    attendance_days = [False for x in range(0, 32)]

    for row in data_rows:

        # Skip empty dates.
        if row[3] == "":
            continue

        split_date_arr = row[3].split("/")
        # The string is in mm/dd/yyyy format
        row_month = int(split_date_arr[0])
        row_day = int(split_date_arr[1])
        row_year = int(split_date_arr[2])

        # Add day as attended if within the period entered
        if row_year == year and row_month == month:

            # Change the list only if the day is False currently.
            if attendance_days[row_day] is False:
                attendance_days[row_day] = True

    return attendance_days


def data_in_period(data_rows, year, month):

    new_arr = []

    for row in data_rows:

        if row[3] == "":
            continue

        split_date_arr = row[3].split("/")
        # The string is in mm/dd/yyyy format
        row_month = int(split_date_arr[0])
        row_day = int(split_date_arr[1])
        row_year = int(split_date_arr[2])

        # Get only the month and year entries.
        if row_year == year and row_month == month:
            new_arr.append(row)

    return new_arr


def data_by_student_ids(data_rows):

    student_dict = dict()

    for row in data_rows:
        student_id = row[0]

        if student_id not in student_dict:
            student_dict[student_id] = []
            student_dict[student_id].append(row)

        else:
            student_dict[student_id].append(row)

    return student_dict


def convert_to_datetime(date_time_str):

    str_arr = date_time_str.split(" ")

    date_str = str_arr[0]
    time_str = str_arr[1]

    is_am = False

    if str_arr[2] == "AM":
        is_am = True

    # Split Date and get year, month, day as integers.
    # date_str format is: mm/dd/yyyy
    date_split_arr = date_str.split("/")

    month_int = int(date_split_arr[0])
    day_int = int(date_split_arr[1])
    year_int = int(date_split_arr[2])

    # Split the Time to get hours
    # Time format: hh:mm:ss
    time_split_arr = time_str.split(":")

    hour_int = time_split_arr[0]
    min_int = time_split_arr[1]
    sec_int = time_split_arr[2]

    if is_am is False:
        hour_int += 12

    date_obj = datetime.datetime(
        year_int, month_int, day_int, hour_int, min_int, sec_int)

    return date_obj


def main():
    file = open('studentHoursTest.csv')

    csv_reader = csv.reader(file)

    # Getting the Header of the CSV file.
    header = []
    header = next(csv_reader)
    print(header)

    # Get the rows of data.
    rows = []
    for row in csv_reader:
        rows.append(row)

    # Isolate only the month and year data.
    month_rows = data_in_period(rows, 2022, 7)

    # Get a list representing the days class was in session in a month.
    # the list can be indexed by the day of the month for results.
    days_attended = get_all_days_attended_in_period(month_rows, 2022, 7)

    # Generate a list of IDs and last, first names.
    student_dict = data_by_student_ids(month_rows)

    print(student_dict)

    print(convert_to_datetime('7/1/2022 9:31:56 AM'))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


