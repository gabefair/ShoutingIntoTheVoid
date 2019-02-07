# pylint: disable=unsubscriptable-object
import sys, os, json, datetime
from time import time

try:
    import dateutil.relativedelta
except ImportError:
    print("Please run `pip install python-dateutil` from a command line ")
    exit()

from os.path import basename

# Global Variables
total_processed = 0
any_errors = False
errors_array = []
error_ids = []
skipped_files = 0
usernames_so_far = []


def write_file():
    global usernames_so_far
    with open('gab_ai_usernames.txt', 'a', encoding="utf-8") as f:
        for line in usernames_so_far:
            f.write(line+"\n")
    usernames_so_far = []


def update_progress(total_imported, skipped_files, current_location):
    text = str(total_imported) + "/" + str(total_imported + skipped_files) + " processed. " + str(
        len(error_ids)) + " errors. Looking in folder: " + current_location
    sys.stdout.write('\r' + text)
    sys.stdout.flush()


def executing_section_users(full_base, files):
    global total_processed, skipped_files, usernames_so_far
    for file_name in files:
        if file_name.endswith((".json")) and not file_name == "auth.json":
            try:
                usernames_so_far.append(os.path.splitext(file_name)[0])
                total_processed += 1

            except KeyError:
                print(file_name)
                print("\n\n")
                raise
    return


def process_files(run_location, folder_path):
    global total_processed, any_errors, error_ids, errors_array, skipped_files, response, usernames_so_far
    total_processed = 0
    any_errors = False
    errors_array = []
    error_ids = []
    skipped_files = 0

    for root, dirs, files in os.walk(folder_path):
        full_base = os.path.join(run_location, root)  # type: str
        if "users" in root.lower():
            try:
                update_progress(total_processed, skipped_files, root)
                response = executing_section_users(full_base, files)

            except KeyboardInterrupt:
                # report_last_file(full_path, response)
                # save_error_ids(len(error_ids), run_location, import_type)
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
                exit()

            except WindowsError:
                raise

            update_progress(total_processed, skipped_files, root)
            if total_processed % 1000 == 0:  #I arbitrarily chose some conditions for intermittently writing to disk to keep RAM low
                write_file()
    write_file()


def main():
    arg_length = len(sys.argv)

    if (arg_length <= 1):
        print(
            "Please specify at 1 parameter: \n\t\t collect_user_jsons_to_one_file.py  <folder path>")
        exit()

    start_time = datetime.datetime.fromtimestamp(time())
    print("Starting Rollup with the following parameters: " + str(sys.argv))

    base_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
    process_files(base_path, sys.argv[1])
    end_time = datetime.datetime.fromtimestamp(time())

    total_time = dateutil.relativedelta.relativedelta(end_time, start_time)
    print("\nProcess completed in: %d days, %d hours, %d minutes and %d seconds" % (
        total_time.days, total_time.hours, total_time.minutes, total_time.seconds))


if __name__ == '__main__':
    # Gabriel Fair
    main()
