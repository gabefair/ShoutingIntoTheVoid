""" Scrapes Gab.ai posts. """
# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object
import sys, os, json, datetime, platform, argparse, traceback, random, json, subprocess
from time import sleep
from time import time
from multiprocessing import Process, freeze_support, JoinableQueue, Array

try:
    import mechanicalsoup
except ImportError:
    raise
    print("Please run `pip install mechanicalsoup` from a command line")
    exit()

try:
    import pymongo
except ImportError:
    print("Please run `pip install pymongo` from a command line ")
    exit()

try:
    import dateutil.relativedelta
except ImportError:
    print("Please run `pip install python-dateutil` from a command line ")
    exit()
# from bson import json_util
from os.path import basename

try:
    from exceptions import WindowsError
    import curses
except ImportError:
    class WindowsError(OSError):
        pass
except:
    pass

# Global Variables
total_imported = 0
total_scraped_users = 0
total_scraped_memes = 0
total_scraped_images = 0
any_errors = False
errors_array = []
error_ids = []
skipped_files = 0
response = 0
reached_the_end = 100
value = 0


def update_progress(i, import_type, odd_or_even, shared_arr):
    if import_type == 'posts':
        shared_arr[0+odd_or_even] = shared_arr[0+odd_or_even] + 1
    elif import_type == 'comments':
        shared_arr[2+odd_or_even] = shared_arr[2+odd_or_even] + 1

    total_scraped_posts = shared_arr[0] + shared_arr[1]
    total_scraped_comments = shared_arr[2] + shared_arr[3]
    total_skipped = shared_arr[4] + shared_arr[5] + shared_arr[6] + shared_arr[7]

    text = str(total_scraped_comments) + " Comments. " + str(total_scraped_posts) + " Posts scraped. " + str(total_skipped) + " Skipped. "

    total_processed = total_scraped_comments + total_scraped_posts

    return print_progress(total_processed, i, text)


def print_progress(total_processed, i, text):
    # global error_ids
    # total_processed = total + skipped
    if(not i % 100) or (total_processed < 500):
        current_location = str(i)
        sys.stdout.write('\r' + text + "Looking at id: " + current_location)
        sys.stdout.flush()


def login(username="", password=""):
    """ Login to gab.ai. """
    if not len(username) or not len(password):
        auth_data = json.load(open("auth.json"))
        try:
            username = auth_data["username"]
        except:
            print("No username specified.")
            return

        try:
            password = auth_data["password"]
        except:
            print("No password specified.")
            return

    browser = mechanicalsoup.StatefulBrowser(
        raise_on_404=True)
    browser.set_user_agent = [("User-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36")]
    r = browser.open("https://gab.ai/auth/login")

    form = browser.select_form(nr=1)
    form.choose_submit(None)
    browser["username"] = username
    browser["password"] = password
    resp = browser.submit_selected()

    # Debug output post-login

    #print(browser.get_current_page())
    #print(browser.get_url())
    return browser


def create_directories():
    # zfill(3)
    return


def get_next_id(i, import_type, odd_or_even):
    if(odd_or_even):
        return int(i) + 1
    return int(i) - 1


def process_submissions(browser, start_id, import_type, pid, shared_arr):
    global reached_the_end

    fail = 0
    j = 0
    k = 0
    odd_or_even = pid % 2
    i = int(start_id) - 1
    last_id = int(start_id)
    shared_arr[4] = 0

    while int(i) > 1:
        i = get_next_id(i, import_type, odd_or_even)
        if i < 100 :
            break

        if (reached_the_end > 100):
            i = last_id - 100
            reached_the_end = 0
        # Check if the post already exists.
        num = str(i)
        ones = num[-1]
        tens = num[-2:]
        hundreds = num[-3:]
        thousands = num[-4:]

        if os.path.isfile(import_type + "/" + ones + "/" + tens + "/" + hundreds + "/" + thousands + "/" + str(i) + ".json"):
            if import_type == 'posts':
                shared_arr[4 + odd_or_even] = shared_arr[4 + odd_or_even] + 1
            elif import_type == 'comments':
                shared_arr[6 + odd_or_even] = shared_arr[6 + odd_or_even] + 1
            continue
        update_progress(i, import_type, odd_or_even, shared_arr)

        # Make directory structure if necessary.
        if not os.path.exists(import_type):
            os.makedirs(import_type)
        if not os.path.exists(import_type + "/" + ones + "/"):
            os.makedirs(import_type + "/" + ones + "/")
        if not os.path.exists(import_type + "/" + ones + "/" + tens + "/"):
            os.makedirs(import_type + "/" + ones + "/" + tens + "/")
        if not os.path.exists(import_type + "/" + ones + "/" + tens + "/" + hundreds + "/"):
            os.makedirs(import_type + "/" + ones + "/" + tens + "/" + hundreds + "/")
        if not os.path.exists(import_type + "/" + ones + "/" + tens + "/" + hundreds + "/" + thousands + "/"):
            os.makedirs(import_type + "/" + ones + "/" + tens + "/" + hundreds + "/" + thousands + "/")

        # Read the post
        try:
            if import_type == 'posts':
                link = "https://gab.ai/posts/" + str(i)
                r = browser.open(link)
                #print("\n")
                #print(r.json())
            elif import_type == 'comments':
                link = "https://gab.ai/posts/" + str(i) + "/comments/index?sort=score"
                r = browser.open(link)
            else:
                print("Unexpected scrape type. Must be posts or comments")
                exit()

            data = r.json()

            with open(import_type + "/" + ones + "/" + tens + "/" + hundreds + "/" + thousands + "/" + str(i) + ".json",
                      "w") as f:
                json.dump(data, f)
                last_id = i

        except mechanicalsoup.LinkNotFoundError:
            reached_the_end += 1
            pass
        except ValueError as e:
            print(i)
            print(e)
            raise
        except:
            raise
            print(traceback.format_exc())
            print("ERROR: STILL DID NOT WORK")
            print(i)
            print("\n")
            raise


def split_work_receiver(import_type, process_no, i, shared_arr):
    browser = login()

    if browser is not None:
        print("\n Finished logging in")
        sleep(2)
        process_submissions(browser, i, import_type, process_no, shared_arr)
    else:
        print("Failed login.")
    return

def import_jsons(type, connection_url, database_name):
    script = ["python2", "v2_import.py", type, type, database_name, type, connection_url, "True"]
    process = subprocess.Popen(" ".join(script), shell=True, stdout=subprocess.DEVNULL,  preexec_fn=os.setpgrp)

def import_work(connection_url, database_name):
    while True:
        import_jsons("comments", connection_url, database_name)
        sleep(600)
        import_jsons("posts", connection_url, database_name)
        sleep(600)
        import_jsons("comments", "cci-prime-radiant-smuppal2.dyn.uncc.edu", database_name)
        sleep(600)
        import_jsons("posts", "cci-prime-radiant-smuppal2.dyn.uncc.edu", database_name)


def split_work(base_path, i, connection_url, database_name):
    shared_arr = Array('i', range(8))
    processes = [
        Process(target=split_work_receiver, args=("posts", 1, i, shared_arr)),
        Process(target=split_work_receiver, args=("posts", 2, i, shared_arr)),
        Process(target=split_work_receiver, args=("comments", 3, i, shared_arr)),
        #Process(target=import_work, args=(connection_url, database_name)),
        Process(target=split_work_receiver, args=("comments", 4, i, shared_arr))]

    #Run processes
    for p in processes:
        p.start()

    while True:
        sleep(600)

    return


def start(base_path, i, connection_url, database_name):
    """ Extracts command line arguments. """
    split_work(base_path, i, connection_url, database_name)
    #split_work_reciever("posts", 1, i)
    return


def fix_import_type(import_type):
    if import_type == "posts" or import_type == "post":
        import_type = "posts"
    elif import_type == "comments" or import_type == "comment":
        import_type = "comments"
    elif import_type == "users" or import_type == "user":
        import_type = "users"
    else:
        print("Can only import posts, users, or comments")
        exit()
    print("This script will skip the import of any json files that are not " + import_type)
    return import_type


def main():
    # https://gab.ai/users/80200/follow

    arg_length = len(sys.argv)

    if (arg_length < 4):
        print("Please specify at least 3 parameters: \n\t\t live_scrape.py <start_id> <connection url> <mongodb database> ")
        exit()

    start_time = datetime.datetime.fromtimestamp(time())
    print("Starting Import with the following parameters: " + str(sys.argv))

    base_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
    start(base_path, sys.argv[1], sys.argv[2], sys.argv[3])
    end_time = datetime.datetime.fromtimestamp(time())

    total_time = dateutil.relativedelta.relativedelta(end_time, start_time)
    print("\nImport completed in: %d days, %d hours, %d minutes and %d seconds" % (
        total_time.days, total_time.hours, total_time.minutes, total_time.seconds))


if __name__ == "__main__":
    freeze_support()
    main()
