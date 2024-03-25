"""
Paul Fitch
Homework 1
This python program is used to manipulate aws s3 buckets
"""
import datetime
import logging
import random
import re
import sys
import boto3
from botocore.exceptions import ClientError


# logger configuration to write  messages to event_log.txt
logging.basicConfig(filename="./event_log.txt",
                    format="%(asctime)s %(levelname)s : %(message)s",
                    datefmt="%Y-%m-%d %H:%M",
                    filemode="w",
                    level=logging.INFO)


def log_message(message=None):
    """
    This function utilizes the logger to log messages
    param message: message to be logged
    """
    if message is not None:
        logging.info(message)
        print("\n")
        print("\n", message)
        print("\n")


def get_bucket_list(s3_client):
    """
    This is a general function that returns a list containing all current buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param s3_client: boto s3 client object
    return: list of current buckets
    """
    buckets = []
    try:
        for bucket in s3_client.list_buckets()["Buckets"]:
            buckets.append(bucket["Name"])
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()
    except ClientError as error:
        log_message(error)
        return False
    return buckets


def select_bucket(s3_client):
    """
    This is a general function to allow users to select buckets
    param s3_client: boto s3 client object
    """
    valid_bucket_index = []
    selected_bucket = None
    try:
        current_buckets = get_bucket_list(s3_client)
        if len(current_buckets) == 0:
            print("There are no buckets\n")
        else:
            index = 0
            for bucket in current_buckets:
                print(f"{index}.{bucket}")
                valid_bucket_index.append(index)
                index += 1
            while selected_bucket not in valid_bucket_index:
                try:
                    selected_bucket = int(
                        input("Please select the bucket number: "))
                except ValueError:
                    print("Invalid selection. Please try again.\n")
                if selected_bucket in valid_bucket_index:
                    selected_bucket = current_buckets[selected_bucket]
                    break
                else:
                    print("please select an appropriate number.\n")
    except ClientError as error:
        log_message(error)
    except AttributeError as error:
        log_message(error)
        print("\nFatal Error. Closing application")
        sys.exit()
    return selected_bucket


def select_object(s3_client, bucket_name):
    """
    This is a general function used to select objects in buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    """
    valid_object_index = []
    selected_object = None
    try:
        bucket_objects = s3_client.list_objects_v2(Bucket=bucket_name)
        if bucket_objects["KeyCount"] > 0:
            index = 0
            for c_object in bucket_objects["Contents"]:
                print(f"{index}.{c_object['Key']}")
                valid_object_index.append(index)
                index += 1
            while selected_object not in valid_object_index:
                try:
                    selected_object = int(
                        input("Please select the object number: "))
                except ValueError:
                    print("Invalid selection. Please try again.\n")
                if selected_object in valid_object_index:
                    selected_object = bucket_objects["Contents"][int(
                        selected_object)]
                    break
                else:
                    print("please select an appropriate number.\n")
    except ClientError as error:
        log_message(error)
    except AttributeError as error:
        log_message(error)
        print("\nFatal Error. Closing application")
        sys.exit()
    return selected_object


def handle_new_buckets(s3_client, region_override=None):
    """
    This function is part of the algorithm used to create new s3 buckets
    This function handles creating new buckets and gathers data used to name buckets
    param s3_client: boto s3 client object
    param region_override: region to be used to create bucket
    """
    list_of_buckets = get_bucket_list(s3_client)
    loop_control = True
    while loop_control:
        first_name = input("Input your first name: ")
        if not re.fullmatch("^[a-z A-Z]+(-[a-z A-Z]+)?$", first_name):
            print("\nInvalid characters detected. Please try again.\n")
            continue
        while True:
            last_name = input("Input your last name: ")
            if not re.fullmatch("^[a-z A-Z]+(-[a-z A-Z]+)?$", last_name):
                print("\nInvalid characters detected. Please try again.\n")
                continue
            loop_control = False
            break
    new_bucket_name = first_name + last_name + \
        str(random.randint(100000, 999999))
    if new_bucket_name not in list_of_buckets and \
            create_new_bucket(new_bucket_name, s3_client, region_override):
        log_message(f"New bucket named {new_bucket_name} created")


def create_new_bucket(bucket_name, s3_client, region_override=None):
    """
    This function is part of the algorithm used to create new s3 buckets
    This function uses the boto3 create_bucket method to create buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param bucket_name: name of new bucket
    param s3_client: boto s3 client object
    param region_override: region to be used to create bucket
    return: true if bucket created, false if bucket not created
    """
    try:
        if region_override is not None:
            region = region_override
        elif region_override is None:
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client("s3", region_name=region_override)
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration={"LocationConstraint": region})
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()
    except ClientError as error:
        log_message(error)
        return False
    return True


def handle_add_to_bucket(s3_client):
    """
    This function is part of the algorithm used to put objects in buckets
    param s3_client: boto 3 client object
    """
    destination = select_bucket(s3_client)
    # no such file / directory: ./hello.txt
    if place_in_bucket(s3_client, destination, "hello.txt", "./hello.txt"):
        print(f"Check the {destination} bucket for the new file\n")
        log_message(f"hello.txt file uploaded to {destination}")


def place_in_bucket(s3_client, destination, obj_name, placed_object):
    """
    This function is part of the algorithm used to put objects in buckets
    This function uses the boto3 put_object method to put objects in buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param s3_cleint: boto3 s3 client object
    param destination: name of the destination bucket
    param object: object to be placed in the destination bucket
    """
    put_data = obj_name
    if isinstance(put_data, str):
        try:
            put_data = open(placed_object, "rb")
        except FileNotFoundError as error:
            log_message(error)
            return False
        except IOError as error:
            log_message(error)
            return False
    try:
        s3_client.put_object(Bucket=destination,
                             Key=placed_object, Body=put_data)
    except ClientError as error:
        log_message(error)
        return False
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()
    finally:
        if getattr(put_data, "close", None):
            put_data.close()
    return True


def handle_delete_object_in_bucket(s3_client):
    """
    This function is part of the algorithm used to delete objects in buckets
    This function uses the boto3 delete_object method to delete objects from buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param s3_client: boto3 s3 client object
    """
    print("Select the bucket to delete from: ")
    destination = select_bucket(s3_client)
    print("Select object to delete")
    selected_object = select_object(s3_client, destination)
    try:
        if selected_object is not None:
            s3_client.delete_object(
                Bucket=destination, Key=selected_object["Key"])
            print(f"Deleted {selected_object['Key']} from{destination}\n")
            log_message(f"{selected_object['Key']} deleted from {destination}")
        else:
            print(f"The selected bucket {destination} is empty\n")
    except ClientError as error:
        log_message(error)
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()


def handle_delete_bucket(s3_client):
    """
    This function is part of the algorithm used to delete buckets
    This function used the boto3 delete_bucket method to delete empty buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param s3_client: boto3 s3 client object
    """
    selected_bucket = select_bucket(s3_client)
    try:
        bucket_objects = s3_client.list_objects_v2(Bucket=selected_bucket)
        if bucket_objects["KeyCount"] > 0:
            print(
                f"{selected_bucket} is not empty. Buckets must be empty to be deleted\n")
        else:
            s3_client.delete_bucket(Bucket=selected_bucket)
            print(f"Bucket {selected_bucket} deleted")
    except ClientError as error:
        log_message(error)
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()
    log_message(f"Bucket {selected_bucket} deleted")


def handle_copy_to_bucket(s3_client):
    """
    This function handles copying objects from one bucket to another
    This function uses the boto3 copy_object method to copy objects
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param s3_client: boto3 s3 client object
    """
    print("Select bucket to copy from")
    origin_bucket = select_bucket(s3_client)
    try:
        bucket_objects = s3_client.list_objects_v2(Bucket=origin_bucket)
        if bucket_objects["KeyCount"] == 0:
            print(f"{origin_bucket} is empty. Please select a bucket with objects\n")
        else:
            print("Select object to copy")
            selected_object = select_object(s3_client, origin_bucket)
            loop_control = True
            while loop_control:
                destination = select_bucket(s3_client)
                if destination == origin_bucket:
                    print("You cannot copy to and from the origin bucket\n")
                else:
                    loop_control = False
            try:
                copy = {"Bucket": origin_bucket,
                        "Key": selected_object["Key"]}
                s3_client.copy_object(
                    CopySource=copy, Bucket=destination, Key=selected_object["Key"])
                print(
                    f"{selected_object['Key']} copied from {origin_bucket} to {destination}")
            except ClientError as error:
                log_message(error)
    except ClientError as error:
        log_message(error)
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()
    log_message(
        f"{selected_object['Key']} copied from {origin_bucket} to {destination}")


def handle_download(s3_client):
    """
    This function handles downloading bucket objects
    This function uses the boto3 download_file method to download files from buckets
    reference:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_s3_code_examples.html#actions
    param s3_client: boto3 s3 client object
    """
    print("Select bucket to download from: ")
    origin_bucket = select_bucket(s3_client)
    try:
        bucket_objects = s3_client.list_objects_v2(Bucket=origin_bucket)
        if bucket_objects["KeyCount"] == 0:
            print(f"{origin_bucket} is empty")
        else:
            selected_object = select_object(s3_client, origin_bucket)
            try:
                s3_client.download_file(
                    origin_bucket, selected_object["Key"], "downloaded_file")
                print(f"{selected_object['Key']} has been downloaded\n")
            except ClientError as error:
                log_message(error)
    except ClientError as error:
        log_message(error)
    except AttributeError as error:
        log_message(error)
        print("\nFatal error, closing application")
        sys.exit()
    log_message(f"{selected_object['Key']} has been downloaded")


def main():
    """
    main function creating menu and calling necessary functions 
    based on used input
    """
    s3_client = boto3.client("s3")
    while True:
        print("Select a function from the options below\n")
        print("1. Create s3 bucket\n")
        print("2. Put an object in a bucket\n")
        print("3. Delete object in bucket\n")
        print("4. Delete bucket\n")
        print("5. Copy object from one bucket to another\n")
        print("6. Download object from bucket\n")
        print("7. Exit program\n")

        user_select = str(input("Select number from menu: "))
        if user_select == "1":
            handle_new_buckets(s3_client)
        elif user_select == "2":
            handle_add_to_bucket(s3_client)
        elif user_select == "3":
            handle_delete_object_in_bucket(s3_client)
        elif user_select == "4":
            handle_delete_bucket(s3_client)
        elif user_select == "5":
            handle_copy_to_bucket(s3_client)
        elif user_select == "6":
            handle_download(s3_client)
        elif user_select == "7":
            date_time_now = datetime.datetime.now()
            date_time_format = date_time_now.strftime("%m/%d/%Y %H:%M")
            print("Exiting program. Goodbye!")
            print(date_time_format)
            break
        else:
            print("Plese use the numbers provided in the menu\n")


main()
