import logging
import boto3
from boto3.dynamodb.conditions import Attr
import json
import time

dynamo_db = boto3.resource('dynamodb')
db_client = boto3.client('dynamodb', region_name = "us-east-1")

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


def delete_table(table_name):
    """
    This function deletes a table
    param table_name: name of table to be deleted
    """
    if not table_exists(table_name):
        print(f"{table_name} table does not exist")
        return
    db_client.delete_table(TableName=table_name)
    time.sleep(10)
    print(f"{table_name} table deleted")
    
def table_exists(table_name):
    """
    This function checks if a table with a given name exists
    param table_name: name of table to be checked
    """
    tables = []
    for table in dynamo_db.tables.all():
        tables.append(table.name)
    if table_name in tables:
        return True
    return False


def create_course_table():
    """
    This function creates the Courses table
    """
    dynamo_db.create_table(
        TableName="Courses",
        KeySchema=[
            {
                'AttributeName': 'CourseID',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'CourseID',
                'AttributeType': 'N'
            }
        ],
         ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
        }
    )


def populate_table(table_name, data):
    """
    This function populates a table with a given name with
    specific data
    param table_name: name of table to be altered
    param data: json file with table data
    return: true if table is populated, false if population fails
    """
    subject = data["Subject"]
    catalog_nbr = data["CatalogNbr"]
    title = data["Title"]
    credit = data["Credits"]
    course_id = int(data["CourseId"])
    try:
        if dynamo_db.Table(table_name).put_item(
            Item={
                "Subject": subject,
                "CatalogNbr": catalog_nbr,
                "Title": title,
                "Credits": credit,
                "CourseID": course_id
            }
        ):
            time.sleep(2)
            return True

    except Exception as error:
        log_message(error)
    print("Populate Failed")
    return False


def get_title(subject, catalog_number):
    """
    this function gets the course title of a course with a given subject
    and catalog number
    param subject: subject to be checked
    param catalog_number: catalog number of subject
    return: title of course or none
    """

    try:
        db_response = dynamo_db.Table("Courses").scan(
            FilterExpression=Attr("Subject").eq(subject)
            & Attr("CatalogNbr").eq(catalog_number),
            ProjectionExpression=("Title")
        )
        title = [obj.get("Title") for obj in db_response["Items"]][0]
        return title
    except Exception as e:
        log_message(e)
    return None


def build():
    """
    This function builds the Courses table
    """
    if table_exists("Courses"):
        print("Courses already exists")
        return

    create_course_table()
    time.sleep(7)
    try:
        with open("courses.json", encoding="utf-8") as courses:
            json_reader = json.load(courses)
            for item in json_reader:
                populate_table("Courses", item)

    except Exception as error:
        log_message(error)

    print("Courses table created and populated")

def query():
    """
    this function allows users to query for course titles
    """

    if not table_exists("Courses"):
        print("Courses table does not exist")
        return

    loop_control = True
    while loop_control:
        subject = ""
        while not subject:
            subject = input("Enter subject: ")[:4].upper()
            if not len(subject) == 4 or not subject.isalpha():
                subject = ""
                print("Please enter the 4 letter course code")
        catalog_nbr = ""
        while not catalog_nbr.isdigit():
            catalog_nbr = input("Enter catalog number: ")[:3]
            if not len(catalog_nbr) == 3 or not catalog_nbr.isdigit():
                catalog_nbr = ""
                print("Please enter 3 digit Catalog Number")
        loop_control = False

        course_title = get_title(subject, catalog_nbr)
        if course_title is None:
            print(f"No course named {subject} {catalog_nbr} found")
        else:
            print(f"{subject} {catalog_nbr} {course_title}")


def main():
    """
    Main function, calls other functions as needed by user
    """
    while True:
        print("Select Function from the options below\n")
        print("1. Create DB")
        print("2. Search for courses")
        print("3. Delete Table")
        print("4. Exit program")

        user_select = str(input("Select number from menu: "))
        if user_select == "1":
            build()
        elif user_select == "2":
            query()
        elif user_select == "3":
            delete_table("Courses")
        elif user_select == "4":
            print("Exiting program. Goodbye!")
            break
        else:
            print("That is not one of the options")


main()