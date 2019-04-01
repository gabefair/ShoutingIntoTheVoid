# pylint: disable=unsubscriptable-object
import sys, os, json, datetime, platform, io
from time import time

try:
    import pymongo
    import gridfs
except ImportError:
    print("Please run `pip install pymongo` from a command line ")
    exit()

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
response = 0
collection_conn = None
total_imported = 0

def update_progress(total_imported, skipped_files, current_location):
    text = str(total_imported) + "/" + str(total_imported + skipped_files) + " imported. " + str(
        len(error_ids)) + " errors. Looking in folder: " + current_location
    sys.stdout.write('\r' + text)
    sys.stdout.flush()


def login_to_database(database, destination_coll, connection_url, import_type):
    client = pymongo.MongoClient("mongodb://" + connection_url + ":27017",
                                 username='username',
                                 password='password',
                                 authSource='admin',
    db = client[database]
    if(import_type == 'users'):
      return gridfs.GridFSBucket(db, bucket_name=destination_coll)
    else:

      return db[destination_coll]


def executing_section_posts_and_comments(full_base, files, import_type):
  global collection_conn, total_processed, skipped_files, total_imported
  for file_name in files:
    if file_name.endswith((".json")) and not file_name == "auth.json":
      full_path = os.path.join(full_base, file_name)
      timestamp_of_json_collected = os.path.getmtime(full_path)  # Date created is not reliable as that could be the date it was copied to a folder, getting modified date instead
      collected_on = datetime.datetime.fromtimestamp(timestamp_of_json_collected)

      with open(full_path) as json_file:
        json_data = json.load(json_file)
      document = {}

      document['id'] = os.path.splitext(file_name)[0]
      document['collected_on'] = collected_on.strftime('%Y-%m-%d %H:%M:%S')
      document['data'] = json_data
      document['type'] = import_type
      try:
        response = collection_conn.insert_one(document)
        total_imported += 1
      except pymongo.errors.DuplicateKeyError:
        skipped_files += 1
        pass
      del json_data, json_file
  return


def executing_section_users(full_base, files):
  global collection_conn, total_processed, skipped_files, total_imported
  for file_name in files:
    if file_name.endswith((".json")) and not file_name == "auth.json":
      full_path = os.path.join(full_base, file_name)
      timestamp_of_json_collected = os.path.getmtime(full_path)  # Date created is not reliable as that could be the date it was copied to a folder, getting modified date instead
      collected_on = datetime.datetime.fromtimestamp(timestamp_of_json_collected)

      with open(full_path) as json_file:
        json_data = json.load(json_file)
      document = {}

      document['username'] = os.path.splitext(file_name)[0]
      document['id'] = json_data['user']['id']
      document['collected_on'] = collected_on.strftime('%Y-%m-%d %H:%M:%S')
      document['data'] = json_data
      document['type'] = 'users'
      document_file = io.StringIO(json.dumps(document))
      try:
        response = collection_conn.upload_from_stream(str(document['id']), document_file)
        total_imported += 1
      except pymongo.errors.DuplicateKeyError:
        skipped_files += 1
        pass

      except ValueError:
        any_errors = True
        error_msg = "Broken File: " + full_path
        error_ids.append(basename(full_path))
        errors_array.append(error_msg)
        pass

      del json_data, json_file
  return


def import_files(run_location, import_type, folder_path, database, destination_coll, connection_url):
    global total_processed, any_errors, error_ids, errors_array, skipped_files, response, collection_conn
    total_imported = 0
    any_errors = False
    errors_array = []
    error_ids = []
    skipped_files = 0

    collection_conn = login_to_database(database, destination_coll, connection_url, import_type)

    for root, dirs, files in os.walk(folder_path):
        full_base = os.path.join(run_location, root)  # type: str
        if import_type in root:
            try:
                update_progress(total_imported, skipped_files, root)
                if (import_type == "users"):
                    response = executing_section_users(full_base, files)
                elif (import_type == "posts" or import_type == "comments"):
                    response = executing_section_posts_and_comments(full_base, files, import_type)
                else:
                    print("\nUnexpected Import Type\nExiting")
                    exit()

            except KeyboardInterrupt:
                #report_last_file(full_path, response)
                #save_error_ids(len(error_ids), run_location, import_type)
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
                exit()

            except WindowsError:
                raise

            update_progress(total_imported, skipped_files, root)


def save_error_ids(error_len, base_path, import_type):
    global error_ids
    save_loc = os.path.join(base_path, sys.argv[1] + '_import_errors.txt')
    print("But there were " + str(
        error_len) + " errors \n A file has been created at " + save_loc + " with all the ids of the " + import_type + " that were not collected correctly")
    f = open(save_loc, 'w')
    f.write(str(error_ids))
    f.close()


def find_os():
    return platform.system()


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
    arg_length = len(sys.argv)

    if (arg_length <= 6):
        print(
            "Please specify 5 parameters: \n\t\t import_to_mongodb.py <posts|comments|users> <folder path> <mongodb database> <mongodb collection name> <connection_url>")
        exit()

    start_time = datetime.datetime.fromtimestamp(time())
    print("Starting Import with the following parameters: " + str(sys.argv))

    base_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
    import_type = fix_import_type(sys.argv[1])
    import_files(base_path, import_type, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    end_time = datetime.datetime.fromtimestamp(time())

    total_time = dateutil.relativedelta.relativedelta(end_time, start_time)
    print("\nImport completed in: %d days, %d hours, %d minutes and %d seconds" % (
    total_time.days, total_time.hours, total_time.minutes, total_time.seconds))

    if (any_errors):
        save_error_ids(str(len(error_ids)), base_path, import_type)


if __name__ == '__main__':
    #Gabriel Fair
    main()
