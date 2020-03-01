""" Scrapes Gab.ai posts. """
# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object
import argparse
import json
import os
import random
import sys
import time
import datetime
import traceback
import mechanize
from errno import EACCES, EPERM, ENOENT

reload(sys)
if sys.version_info.major < 3:
    sys.setdefaultencoding('utf8')

# Global Variables
any_errors = False
error_ids = []


def save_error_ids(error_len, import_type, x):
    global error_ids
    save_loc = 'users_import_errors.txt'
    print("But there were " + str(
        error_len) + " errors \n A file has been created at " + save_loc + " with all the ids of the " + import_type + " that were not collected correctly")
    f = open(save_loc, 'w')
    f.write(str(error_ids))
    f.close()
    process_users(login(), error_ids, x)


def update_progress(total_new, total_users, total_skipped, current_location, loop_count):
    global error_ids
    total_processed = total_new + total_skipped
    text = str(loop_count) + ": " + str(total_new) + " new. " + str(total_processed) + "/" + str(total_users) + " processed. " + str(len(error_ids)) + " errors. Looking at user: " + current_location + " "
    sys.stdout.write('\r' + text)
    sys.stdout.flush()


def write_names_txt(existing, new):
    with open("names.txt", "w") as f:
        for user in existing:
            f.write(user)
            f.write("\n")
        for user in new:
            f.write(user)
            f.write("\n")


def spider(loop_count):
    """ Main spidering code, searches for everyone who follows or is following anyone in current user list. """
    existing = set([x.strip().lower() for x in open("names.txt", "r").read().split("\n") if len(x.strip())])
    del (x)
    print("Spider has awoken")
    new = set([])
    total_new = 0
    total_skipped = 0
    total_users = len(existing)

    current_location = ''

    try:
        for i in existing:
            update_progress(total_new, total_users, total_skipped, i, loop_count)
            if i == "auu":
                print("skipping user: auu")
                continue
            elif i == "aux":
                print("skipping user: aux")
                continue
            elif i == "con":
                print("skipping user: con")
                continue
            elif i == "nul":
                print("skipping user: con")
                continue

            prefix = i[0:2].lower()
            try:
                data_file = json.loads(open("users/" + prefix + "/" + i + ".json", "r").read())
                for user in data_file["following"]["data"]:
                    user = user["username"].lower()
                    if user not in existing and user not in new:
                        # new.append(user["username"])
                        new.add(user)
                for user in data_file["followers"]["data"]:
                    user = user["username"].lower()
                    if user not in existing and user not in new:
                        # new.append(user["username"])
                        new.add(user)
                        total_new += 1
            except TypeError as e:
                total_skipped += 1
                pass
            except IOError as e:
                total_skipped += 1
                if (e.errno == ENOENT):
                    pass
                else:
                    raise

    except KeyboardInterrupt:
        pass

    write_names_txt(existing, new)
    print(len(new), "new users discovered.")
    print(len(existing) + len(new), "total users")


def shuffle_users(user_names):
    """ Generates a scraping order. """
    print("Generates a scraping order")
    #random.shuffle(user_names)
    user_names.reverse()
    return user_names


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

    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.set_handle_refresh(False)
    browser.addheaders = [("User-agent",
                           "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")]
    r = browser.open("https://gab.ai/auth/login")

    browser.select_form(nr=1)
    browser["username"] = username
    browser["password"] = password
    r = browser.submit()

    # print r.read()[0:500]

    return browser

def write_json(prefix, i, data):
    with open("users/" + prefix + "/" + str(i) + ".json", "w") as f:
        json.dump(data, f)

def process_users(browser, user_names, loop_count):
    """ Scrapes the specified posts. """
    global error_ids, any_errors
    j = 0
    k = 0
    total_imported = 0
    skipped_files = 0
    total_users = len(user_names)
    for i in user_names:
        high_intensity_user = 0

        # Check if the post already exists.
        prefix = i[0:2].lower()

        if os.path.isfile("users/" + prefix + "/" + i + ".json"):
            # print "Already have user " + i + ". Skipping."
            skipped_files += 1
            continue

        # Make directory structure if necessary.
        if not os.path.exists("users"):
            os.makedirs("users")
        if not os.path.exists("users/" + prefix):
            os.makedirs("users/" + prefix)

        # Read the user
        try:
            # print str(i), "user page"
            r = browser.open("https://gab.ai/users/" + str(i))
            user_data = json.loads(r.read())
            r = browser.open("https://gab.ai/users/" + str(i) + "/followers")
            # print str(i), "follower page"
            follower_data = json.loads(r.read())
            if not follower_data["no-more"]:
                page = 1
                done = 0
                while not done and page < 1500:
                    min_back = page * 30
                    r = browser.open("https://gab.ai/users/" + str(i) + "/followers?before=" + str(min_back))
                    page = page + 1
                    follower_page = json.loads(r.read())
                    if follower_page["no-more"]:
                        done = 1
                    follower_data["data"].extend(follower_page["data"])

                    if page % 10 == 1:
                        # print str(i), "follower page", str(page)
                        # time.sleep(3)
                        high_intensity_user = 1
                    else:
                        time.sleep(0.1)

            r = browser.open("https://gab.ai/users/" + str(i) + "/following")
            # print str(i), "following page"
            following_data = json.loads(r.read())
            if i == "aux":
                continue
            if not following_data["no-more"]:
                page = 1
                done = 0
                while not done and page < 1500:
                    min_back = page * 30
                    r = browser.open("https://gab.ai/users/" + str(i) + "/following?before=" + str(min_back))
                    page = page + 1
                    following_page = json.loads(r.read())
                    if following_page["no-more"]:
                        done = 1
                    following_data["data"].extend(following_page["data"])

                    if page % 10 == 1:
                        # print str(i), "following page", str(page)
                        # time.sleep(3)
                        high_intensity_user = 1
                    # else:
                    # time.sleep(0.1)

            data = {"user": user_data, "followers": follower_data, "following": following_data}

            write_json(prefix, str(i), data)

            # print data
            # print i
            # print ""
            total_imported += 1
        # Error handling.
        except mechanize.HTTPError as error_code:
            if isinstance(error_code.code, int) and error_code.code == 429:
                print("TOO MANY REQUESTS. SHUT DOWN.")
                print(i)
                any_errors = 1
                sys.exit(-1)
                return
            # elif isinstance(error_code.code, int) and error_code.code == 404:
            # print "Gab post deleted or ID not allocated"
            # print i
            elif isinstance(error_code.code, int) and error_code.code == 400:
                #print "Invalid request -- possibly a private Gab post?"
                data = {"user": "private", "followers": "unknown", "following": "unknown"}
                write_json(prefix, str(i), data)
                continue
            # print i
            else:
                print(error_code.code)
                # print traceback.format_exc()
                # print("ERROR: DID NOT WORK: " + i)
                # time.sleep(random.randint(1, 10))
                any_errors = 1
                skipped_files += 1
                error_ids.append(i)
        except:
            print(traceback.format_exc())
            print("ERROR: STILL DID NOT WORK")
            print(i)

        # Pausing between jobs.
        pause_timer = random.randint(1, 100)
        # if pause_timer >= 99:
        # print "Waiting..."
        # time.sleep(random.randint(1, 3))

        k = k + 1
        # j = j + 1
        if k >= 15000:
            # print "Long break."
            time.sleep(random.randint(1, 5))
            k = 0
        if high_intensity_user:
            print("Tough job, time to take a break.")
            time.sleep(random.randint(1, 20))

        update_progress(total_imported, total_users, skipped_files, i, loop_count)
    if (any_errors):
        save_error_ids(str(len(error_ids)), "users", loop_count)


def process_args(loop_count):
    """ Reads command line arguments for what users file to use. """
    parser = argparse.ArgumentParser(description="Gab.ai scraper.")
    parser.add_argument("-u", "--username", action="store", dest="username", help="Specify a username", default="")
    parser.add_argument("-p", "--password", action="store", dest="password", help="Specify a password", default="")
    parser.add_argument("-f", "--filename", action="store", dest="filename", help="Specify a filename",
                        default="names.txt")
    args = vars(parser.parse_args())

    user_names = [x.strip() for x in open(args["filename"], "r").read().split("\n") if len(x.strip())]

    user_order = shuffle_users(user_names)
    browser = login(args["username"], args["password"])

    if browser is not None:
        process_users(browser, user_order, loop_count)
    else:
        print("Failed login.")


def start():
    x = 0
    while x != 90:
        print("This is the loop count: " + str(x))
        spider(x)
        process_args(x)
        x += 1
        print("This is the loop count: " + str(x))


if __name__ == "__main__":
    start()
