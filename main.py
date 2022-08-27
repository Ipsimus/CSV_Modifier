import copy
import csv
import datetime
import random
import time


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

    def get_variance(self):
        return self.variance

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

        self.avg_clock_in = None
        self.avg_clock_out = None
        self.cur_clock_obj = None
        self.daily_hour_target = 0

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
        self.update_month_hours()
        return self.month_hours

    def get_needed_hours(self):
        return self.needed_hours

    def get_modified_days_attended(self):
        days_attended = set()
        for day in self.modified_attendance_dict.keys():
            days_attended.add(day)
        return days_attended

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

    def add_adj_day(self):
        # Use the set difference between the regular days and the days in
        school = self.school
        days_attended = self.get_modified_days_attended()
        regular_day_choices = school.regular_days.difference(days_attended)
        weekend_day_choices = school.weekend_days.difference(days_attended)

        if regular_day_choices:
            picked_day = random.choice(list(regular_day_choices))

        elif weekend_day_choices:
            picked_day = random.choice(list(weekend_day_choices))

        else:
            return False

        # Gets the first day of the month being processed.
        school_month_obj = school.get_school_month()
        # Get the current year and month.
        cur_year, cur_month = school_month_obj.year, school_month_obj.month
        # Create Clock_Day object.
        new_day = Clock_Day()
        new_day.set_clock_day(datetime.datetime(cur_year, cur_month, picked_day))
        # Add the new_day obj to the modified attendance.
        self.modified_attendance_dict[picked_day] = new_day

        return True

    def entry_near_boundary(self, clock_obj):
        clock_in, clock_out = clock_obj.get_clock_in(), clock_obj.get_clock_out()
        day_obj = clock_obj.get_clock_day()

        year, month, day = day_obj.year, day_obj.month, day_obj.day
        open_hour = self.school.get_regular_open()
        close_hour = self.school.get_regular_close()

        clock_in_diff = None
        clock_out_diff = None

        if clock_obj.is_weekend():

            open_hour = self.school.get_weekend_open()
            close_hour = self.school.get_weekend_close()

        if clock_in is not None:
            open_time = datetime.datetime(year, month, day, open_hour)
            clock_in_diff = clock_in - open_time

        if clock_out is not None:
            close_time = datetime.datetime(year, month, day, close_hour)
            clock_out_diff = close_time - clock_out

        if clock_in_diff is not None and clock_out_diff is not None:
            if clock_in_diff.total_seconds() < clock_out_diff.total_seconds():
                return clock_in  # represents clock in

            else:
                return clock_out  # represents clock out.

        elif clock_in_diff is not None:
            return clock_in

        elif clock_out_diff is not None:
            return clock_out

        # If both are None, then neither is closer to the close/open.
        return None

    def avg_hours_needed_per_day(self):
        """
        Gets the estimated hours needed per day.
        :return: float.
        """
        return self.needed_hours / len(self.modified_attendance_dict)

    def avg_clock_entries(self):
        """
        Returns the average time for clock ins and clock outs.
        :return: clock in and clock out datetime object.
        """
        arbitrary_date_in = copy.deepcopy(self.school.get_school_month())
        arbitrary_date_out = copy.deepcopy(self.school.get_school_month())

        clock_in_totals = 0
        clock_in_len = 0
        clock_out_totals = 0
        clock_out_len = 0

        for day in self.modified_attendance_dict.values():

            if day.clock_in is not None:
                clock_in_totals += (day.clock_in - arbitrary_date_in).seconds
                clock_in_len += 1

            if day.clock_out is not None:
                clock_out_totals += (day.clock_out - arbitrary_date_out).seconds
                clock_out_len += 1

        avg_clock_in = arbitrary_date_in + datetime.timedelta(seconds=int((clock_in_totals / clock_in_len)))
        avg_clock_out = arbitrary_date_out + datetime.timedelta(seconds=int((clock_out_totals / clock_out_len)))

        return avg_clock_in, avg_clock_out

    def remove_none_entry(self, clock_obj):

        cur_day = clock_obj.get_clock_day_int()
        rand_min = random.randint(0, 59)
        rand_sec = random.randint(0, 59)

        if clock_obj.get_clock_in() is None:
            rand_min = random.randint(0, 59)
            rand_sec = random.randint(0, 59)

            temp_day_obj = self.avg_clock_in.replace(day=cur_day,
                                                     minute=rand_min,
                                                     second=rand_sec)
            clock_obj.set_clock_in(temp_day_obj)

        if clock_obj.get_clock_out() is None:
            rand_min = random.randint(0, 59)
            rand_sec = random.randint(0, 59)

            temp_day_obj = self.avg_clock_out.replace(day=cur_day,
                                                      minute=rand_min,
                                                      second=rand_sec)
            clock_obj.set_clock_out(temp_day_obj)

    def is_over_boundary(self, clock_obj):

        # Variables
        clock_in = clock_obj.get_clock_in()
        clock_out = clock_obj.get_clock_out()
        reg_open_hour = self.school.get_regular_close()
        reg_close_hour = self.school.get_regular_close()
        weekend_open_hour = self.school.get_weekend_open()
        weekend_close_hour = self.school.get_weekend_close()
        variance = self.school.get_variance()

        # This are the Date time objects created for the opens and closes.
        datetime_weekend_open = clock_in.replace(hour=weekend_open_hour,
                                                 minute=0, second=0)
        datetime_weekend_close = clock_in.replace(hour=weekend_close_hour,
                                                 minute=0, second=0)
        datetime_reg_open = clock_in.replace(hour=reg_open_hour,
                                             minute=0, second=0)
        datetime_reg_close = clock_in.replace(hour=reg_close_hour,
                                              minute=0, second=0)

        # This are the Decimal Hours for Open and Close
        decimal_weekend_open = convert_to_decimal_hour(datetime_weekend_open)
        decimal_weekend_close = convert_to_decimal_hour(datetime_weekend_close)
        decimal_reg_open = convert_to_decimal_hour(datetime_reg_open)
        decimal_reg_close = convert_to_decimal_hour(datetime_reg_close)

        # Decimal Time for Clock in and out:
        clock_in_decimal = convert_to_decimal_hour(clock_in)
        clock_out_decimal = convert_to_decimal_hour(clock_out)

        # weekend instructions.
        if clock_obj.is_weekend():
            if clock_in_decimal < (decimal_weekend_open * (1 - variance)):
                return False
            if clock_out_decimal > (decimal_weekend_close * (1 + variance)):
                return False

        # regular instructions.
        else:
            if clock_in_decimal < (decimal_reg_open * (1 - variance)):
                return False
            if clock_out_decimal > (decimal_reg_close * (1 + variance)):
                return False
        return True

    def is_over_daily_limit(self, clock_obj):

        weekend_limit = self.school.get_weekend_hour_limit()
        regular_limit = self.school.get_regular_hour_limit()
        variance = self.school.get_variance()

        if clock_obj.is_weekend():
            if clock_obj.get_total_hours() > weekend_limit * (1 + variance):
                return True
        else:
            if clock_obj.get_total_hours() > regular_limit * (1 + variance):
                return True
        return False

    def is_at_target(self, clock_obj):

        regular_weekend_ratio = 1

        if clock_obj.is_weekend():
            regular_weekend_ratio = self.school.get_weekend_hour_limit() / \
                                 self.school.get_regular_hour_limit()

        return clock_obj.get_total_hours() >= (self.daily_hour_target * (
                1 - self.school.variance) * regular_weekend_ratio)

    def adj_clock_in(self, clock_obj):

        test_hour = clock_obj.get_clock_in().hour
        test_clock_obj = copy.deepcopy(clock_obj)
        test_clock_in = test_clock_obj.get_clock_in()

        # While not at the target we iterate.
        while not self.is_at_target(test_clock_obj):

            # Replace method returns a new object.
            test_clock_in = clock_obj.get_clock_in().replace(hour=test_hour)

            test_clock_obj.set_clock_in(test_clock_in)

            # 1) Are we past a boundary?
            # 2) Are we over our daily limit?
            if self.is_over_boundary(
                    test_clock_obj) or self.is_over_daily_limit(
                    test_clock_obj):
                # If we are over; Go 1 hour forward
                # While loop is in case more hours need to be subtracted.
                while self.is_over_boundary(
                        test_clock_obj) or self.is_over_daily_limit(
                        test_clock_obj):
                    test_clock_obj.inc_clock_in_hour()
                    test_clock_in = test_clock_obj.get_clock_in()
                break

            test_hour -= 1

        clock_obj.set_clock_in(test_clock_in)

    def adj_clock_out(self, clock_obj):
        test_hour = clock_obj.get_clock_out().hour
        test_clock_obj = copy.deepcopy(clock_obj)
        test_clock_out = test_clock_obj.get_clock_out()

        # While not at the target we iterate.
        while not self.is_at_target(test_clock_obj):

            # Replace method returns a new object.
            test_clock_out = clock_obj.get_clock_out().replace(hour=test_hour)

            test_clock_obj.set_clock_out(test_clock_out)

            # 1) Are we past a boundary?
            # 2) Are we over our daily limit?
            if self.is_over_boundary(
                    test_clock_obj) or self.is_over_daily_limit(test_clock_obj):
                # If we are over; Go 1 hour forward
                # While loop is in case more hours need to be subtracted.
                while self.is_over_boundary(
                        test_clock_obj) or self.is_over_daily_limit(test_clock_obj):

                    # You are Working here.
                    # Create a Decrement function for the Clock Day type.
                    test_clock_obj.dec_clock_out_hour()
                    test_clock_out = test_clock_obj.get_clock_out()
                break

            test_hour += 1

        clock_obj.set_clock_out(test_clock_out)

    def adj_day_entry(self, clock_obj):

        if self.daily_hour_target >= 8:
            self.daily_hour_target = 8

        # Removes none_clock entries and replaces them with random avg.
        self.remove_none_entry(clock_obj)

        # Correctly position earliest clock time as in and latest as out.
        clock_obj.sort_clock_in_out()

        nearest_boundary = self.entry_near_boundary(clock_obj)
        if nearest_boundary is None:
            print("The remove_none_entry is not working!!")

        # If clock in is closest begin with clock out.
        if clock_obj.get_clock_in() == nearest_boundary:
            self.adj_clock_out(clock_obj)
            self.adj_clock_in(clock_obj)

        # If clock out is closest to boundary time, begin with clock in.
        elif clock_obj.get_clock_out() == nearest_boundary:
            self.adj_clock_in(clock_obj)
            self.adj_clock_out(clock_obj)

        # Work here, you need to modify entries which are not None.
        # ***** ******
        print(f"The day: {clock_obj.get_clock_day().day} - "
              f"The hours: {clock_obj.get_total_hours()}")


    def generate_clock_entries(self):

        days_attended = self.get_modified_days_attended()
        modified_attendance_dict = self.get_modified_attendance_dict()

        for day_key in days_attended:
            clock_day = modified_attendance_dict[day_key]

            self.adj_day_entry(clock_day)

    # This function needs to be renamed!!!!!
    def adjust_hours(self):

        # Adds the approximate need of days.
        while True:
            # Check to see if the student has enough days.
            needs_more_days, needed_hours = self.needs_more_days()

            if needs_more_days is True:
                # Here you will code adding more days to student.
                # False means no more days can be added and will break loop.
                if self.add_adj_day() is False:
                    break
            else:
                break

        # Gets the estimated hours needed per day:
        self.daily_hour_target = self.avg_hours_needed_per_day()

        # Get avg hours entered per day
        self.avg_clock_in, self.avg_clock_out = self.avg_clock_entries()

        # Generate the clock entries for all days.
        self.generate_clock_entries()

        # Check that we have met the requirement.
        if self.get_month_hours() < self.get_needed_hours():

            if self.add_adj_day() is True:

                # Generate the clock entries again.
                self.generate_clock_entries()


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
        self.update_total_hours()

    def set_clock_out(self, clock_out):
        self.clock_out = clock_out
        self.update_total_hours()

    def set_total_hours(self, hours):
        self.total_hours = hours

    # ********** Getters **********
    def get_clock_day(self):
        return self.clock_day

    def get_clock_day_int(self):
        return self.clock_day.day

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
            return

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

    def is_weekend(self):
        if self.clock_day.weekday() > 4:
            return True
        return False

    def inc_clock_in_hour(self):
        """
        Increments the current clock_in time by 1 hour.
        :return: None.
        """
        new_hour = self.clock_in.hour + 1
        new_clock_in = self.clock_in.replace(hour=new_hour)
        self.clock_in = new_clock_in
        # Always update total hours after any changes to clock in/out.
        self.update_total_hours()

    def dec_clock_out_hour(self):
        """
        Decrements the current clock_out time by 1 hour.
        :return: None.
        """
        new_hour = self.clock_in.hour - 1
        new_clock_out = self.clock_in.replace(hour=new_hour)
        self.clock_out = new_clock_out
        # Always update total hours after any changes to clock in/out.
        self.update_total_hours()

    def sort_clock_in_out(self):

        if self.clock_in is None or self.clock_out is None:
            return

        else:
            if self.clock_in > self.clock_out:
                temp = self.clock_in
                self.clock_in = self.clock_out
                self.clock_out = temp


# ********** Static Functions **********
def is_datetime_weekend(datetime_obj):
    if datetime_obj.weekday() > 4:
        return True
    return False


def convert_to_decimal_hour(datetime_obj):

    hour = datetime_obj.hour
    min = datetime_obj.minute
    sec = datetime_obj.second

    total_sec = sec
    total_sec += (min * 60)
    total_sec += (hour * 60 * 60)

    return round(total_sec / (60 * 60), 2)


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

    # ********** Test Case **********
    student_dict = school.get_student_dict()

    student = student_dict["00041"]

    student.set_needed_hours(140)

    print(student.modified_attendance_dict.keys())

    student.adjust_hours()
    print(student.get_month_hours())

    print("end")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))


