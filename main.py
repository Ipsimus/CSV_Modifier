import csv
import datetime


class Student:

    def __init__(self, student_id):

        self.student_id = student_id
        self.first_name = None
        self.last_name = None
        self.session = None
        self.month_hours = None
        self.original_attendance_data = None
        self.modified_attendance_dict = dict()

    # ********** Setters **********
    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_original_attendance_data(self, data):
        self.original_attendance_data = data

    def set_session(self, session):
        self.session = session

    # ********** Getters **********
    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_original_attendance_data(self):
        return self.original_attendance_data

    def get_session(self):
        return self.session

    # ********** Obj Functions **********
    def import_attendance(self):

        for day_row in self.original_attendance_data:

            # Create Clock_Day Obj
            day = Clock_Day()
            clock_in, clock_out = min_max_clock_entries(day_row)

            # Index position 3 is CLKDATE which is the clock_day.
            day.set_clock_day(convert_to_datetime(day_row[3]))

            # Set the clock in and out.
            day.set_clock_in(clock_in)
            day.set_clock_out(clock_out)

            # Set total hours from database index position 10.
            if day_row[10] != "":
                day.set_total_hours(float(day_row[10]))

            # Adds Clock_Day object to the modified attendance dictionary.
            self.modified_attendance_dict[day.get_clock_day().day] = day


class Clock_Day:

    def __init__(self):
        self.clock_day = None
        self.clock_in = None
        self.clock_out = None
        self.total_hours = None

    # ********** Setters **********
    def set_clock_day(self, date):
        self.clock_day = date

    def set_clock_in(self, clock_in):
        self.clock_in = clock_in

    def set_clock_out(self, clock_out):
        self.clock_out = clock_out

    def set_total_hours(self, hours):
        self.total_hours = hours

    # ********** Getters **********
    def get_clock_day(self):
        return self.clock_day

    def get_clock_in(self):
        return self.clock_in

    def get_clock_out(self):
        return self.clock_out

    def get_total_hours(self):
        return self.total_hours



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


def convert_to_datetime(date_time_str, date_only=True):

    str_arr = date_time_str.split(" ")

    date_str = str_arr[0]

    # Split Date and get year, month, day as integers.
    # date_str format is: mm/dd/yyyy
    date_split_arr = date_str.split("/")

    month_int = int(date_split_arr[0])
    day_int = int(date_split_arr[1])
    year_int = int(date_split_arr[2])

    if date_only is False:
        time_str = str_arr[1]

        is_am = False

        if str_arr[2] == "AM":
            is_am = True

        # Split the Time to get hours
        # Time format: hh:mm:ss
        time_split_arr = time_str.split(":")

        hour_int = int(time_split_arr[0])
        min_int = int(time_split_arr[1])
        sec_int = int(time_split_arr[2])

        if is_am is False:
            hour_int = hour_int % 12
            hour_int += 12

        date_obj = datetime.datetime(
            year_int, month_int, day_int, hour_int, min_int, sec_int)

    else:
        date_obj = datetime.datetime(year_int, month_int, day_int)

    return date_obj


def min_max_clock_entries(date_row):

    entries_arr = []

    # Index position 4 - 9 hold the clock in/outs for up to 3 entries.
    for clock_entry in date_row[4:10]:

        if clock_entry != "":
            entries_arr.append(convert_to_datetime(clock_entry, False))

    # If we have at least 2 entries we get the min & max.
    if len(entries_arr) >= 2:
        min_entry = entries_arr.pop(0)
        max_entry = entries_arr.pop()

        return min_entry, max_entry

    # If only one, we get at least min.
    elif len(entries_arr) == 1:
        min_entry = entries_arr.pop()
        return min_entry, None

    else:
        return None, None


def create_students_dict(student_dict):

    students = dict()

    for student_id in student_dict.keys():

        # Get student id and last name into Student Class.
        student_obj = Student(student_id)
        last_name, first_name = student_dict[student_id][0][1:3]
        student_obj.set_first_name(first_name)
        student_obj.set_last_name(last_name)

        # Set the original attendance data.
        student_obj.set_original_attendance_data(student_dict[student_id])

        # Import original data into the modified_attendance_dict
        student_obj.import_attendance()

        # Add student_obj to students dictionary.
        students[student_obj.student_id] = student_obj

    return students


def main():
    file = open('studentHoursTest.csv')

    csv_reader = csv.reader(file)

    # Getting the Header of the CSV file.
    header = []
    header = next(csv_reader)

    # Get the rows of data.
    rows = []
    for row in csv_reader:
        rows.append(row)

    # Close out the file
    file.close()

    # Isolate only the month and year data.
    month_rows = data_in_period(rows, 2022, 7)

    # Get a list representing the days class was in session in a month.
    # the list can be indexed by the day of the month for results.
    days_attended = get_all_days_attended_in_period(month_rows, 2022, 7)

    # Creates a dict() organized by student_id, containing the students clock
    # entries.
    students_data_dict = data_by_student_ids(month_rows)

    # Creates student objects in dictionary form
    students_dict = create_students_dict(students_data_dict)

    print(students_dict)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


