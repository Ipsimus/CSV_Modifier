import csv
import datetime
import random
import math


class School:

    def __init__(self, year, month):

        self.school_month = datetime.datetime(year, month, 1)
        # ***** School Rules *****
        # Hours are in 24hr time.
        self.regular_open = 9      # 9am
        self.regular_close = 20    # 8pm
        self.weekend_open = 10     # 10am
        self.weekend_close = 16    # 4pm
        # The maximum hours a student can have in a day.
        self.regular_hour_limit = 8
        self.weekend_hour_limit = 6
        self.variance = 0.05        # 5% variance allowed.

        # Days of the month where class was held. Same as days attended.
        self.days_open_arr = None

        # Days open consists of regular days + weekend days.
        self.days_open = set()

        # Regular Days
        self.regular_days = set()

        # Weekend Days
        self.weekend_days = set()

        # Students in good standing:
        self.allowed_students = dict()

        # holds the student objects.
        self.students_dict = dict()

    # ********** Setters **********
    def set_days_open_arr(self, arr):
        self.days_open_arr = arr

    # ********** Getters **********
    def get_school_month(self):
        return self.school_month

    def get_regular_open(self):
        return self.regular_open

    def get_regular_close(self):
        return self.regular_close

    def get_weekend_open(self):
        return self.weekend_open

    def get_weekend_close(self):
        return self.weekend_close

    def get_regular_hour_limit(self):
        return self.regular_hour_limit

    def get_weekend_hour_limit(self):
        return self.weekend_hour_limit

    def get_days_open(self):
        return self.days_open

    def get_regular_days(self):
        return self.regular_days

    def get_weekend_days(self):
        return self.weekend_days

    def get_student_dict(self):
        return self.students_dict

    # ********** Obj Functions **********
    def create_days_open_sets(self):

        for day in range(0, len(self.days_open_arr)):

            if self.days_open_arr[day] is True:

                year, month = self.school_month.year, self.school_month.month
                cur_date_obj = datetime.datetime(year, month, day)

                # The 0 (Monday) - 6 (Sunday). Greater than Friday is Weekend.
                if cur_date_obj.weekday() <= 4:
                    self.regular_days.add(day)

                else:
                    self.weekend_days.add(day)

        # Create days_open set, Union of regular days and weekend days:
        self.days_open = self.regular_days.union(self.weekend_days)

    def create_students_dict(self, student_data_dict):

        for student_id in student_data_dict.keys():
            # Get student id and school_obj into student class.
            student_obj = Student(student_id, self)
            last_name, first_name = student_data_dict[student_id][0][1:3]
            student_obj.set_first_name(first_name)
            student_obj.set_last_name(last_name)

            # Set the original attendance data.
            student_obj.set_original_attendance_data(
                student_data_dict[student_id])

            # Import original data into the modified_attendance_dict
            student_obj.import_attendance()

            # Update the total month hours.
            student_obj.update_month_hours()

            # Add student_obj to students dictionary.
            self.students_dict[student_obj.student_id] = student_obj


class Student:

    def __init__(self, student_id, school_obj):

        self.student_id = student_id
        self.first_name = None
        self.last_name = None
        self.school = school_obj
        self.session = None
        self.month_hours = None
        self.needed_hours = None
        self.original_attendance_data = None
        self.modified_attendance_dict = dict()

    # ********** Setters **********
    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_needed_hours(self, hours):
        self.needed_hours = hours

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

    def get_modified_attendance_dict(self):
        return self.modified_attendance_dict

    def get_session(self):
        return self.session

    def get_month_hours(self):
        return self.month_hours

    def get_needed_hours(self):
        return self.needed_hours

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

    def update_month_hours(self):

        self.month_hours = 0

        for day_key in self.modified_attendance_dict.keys():

            if self.modified_attendance_dict[day_key].get_total_hours() is None:
                continue

            self.month_hours += \
                self.modified_attendance_dict[day_key].get_total_hours()

    def needs_more_days(self):
        """
        Determines if a student needs more days.
        :return: A tuple with BOOL and an integer representing hours still
                needed.
        """

        my_school = self.school
        cur_possible_hours = 0

        for day in self.modified_attendance_dict.keys():
            if day in my_school.regular_days:
                cur_possible_hours += my_school.regular_hour_limit

            else:
                cur_possible_hours += my_school.weekend_hour_limit

        estimated_possible_hours = cur_possible_hours * (
                1 - my_school.variance)

        if self.needed_hours <= estimated_possible_hours:
            return False, 0

        hours_left = (self.needed_hours - estimated_possible_hours)
        return True, hours_left

    def add_more_days(self, hours_needed):
        # work here!!
        # Use the set difference between the regular days and the days in


    def adjust_hours(self):

        # Check to see if the student has enough days.
        needs_more_days, needed_hours = self.needs_more_days()

        if needs_more_days is True:

            # Here you will code adding more days to student.
            self.add_more_days(needed_hours)

        else:
            # Here you will just do the adjustment.
            pass


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

    # ********** Obj Functions **********
    def update_total_hours(self):

        if self.clock_in is None or self.clock_out is None:
            self.set_total_hours(None)

        if self.clock_in > self.clock_out:
            temp = self.clock_in

            self.clock_in = self.clock_out
            self.clock_out = temp

        # The difference
        diff = self.clock_out - self.clock_in

        seconds = diff.total_seconds()

        # Decimal hours is: seconds / 60sec in min and 60 min in hour.
        decimal_hours = seconds / (60 * 60)
        # Rounds to two decimal places.
        self.set_total_hours(round(decimal_hours, 2))


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


def main():

    year = 2022
    month = 7

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

    # Creates School class.
    school = School(year, month)

    # add school attendance data
    school.set_days_open_arr(days_attended)

    # Create days open, regular days, and weekend days sets:
    school.create_days_open_sets()

    # Add student objects into School in dictionary form
    school.create_students_dict(students_data_dict)

    # ***** Test Case *****
    student_dict = school.get_student_dict()

    student = student_dict["00041"]

    student.set_needed_hours(140)

    print(student.needs_more_days())

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


