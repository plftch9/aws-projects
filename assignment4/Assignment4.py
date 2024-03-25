"""
Paul Fitch
12/10/2023
sdev 400-
homework 4
Starts and runs snake game,
saves high scores to dynamo db table
writes scores to file
allows download of score file from s3 bucket
"""


import sys
from random import randint
import uuid
import curses
from botocore.exceptions import ClientError
import boto3


dynamo_db = boto3.resource('dynamodb')
db_client = boto3.client('dynamodb', region_name="us-east-1")
s3_client = boto3.client("s3")

def print_menu():
    print("Welcome to Snake Game")
    print("1. Play Game")
    print("2. Load Scores from database")
    print("3. Update Score File")
    print("4. Download Score File")
    print("5. Load Scores from S3 Bucket")
    print("6. Exit Program")


class App:
    """
    facilitates application when running
    """

    windowWidth = 1000
    windowHeight = 800
    player = 0
    apple = 0

    def __init__(self):
        if not self.table_exists("HighScores"):
            dynamo_db.create_table(
                TableName="HighScores",
                KeySchema=[
                    {
                        'AttributeName': 'ScoreId',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'ScoreId',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )

        self.create_bucket()
        
        
    def game(self):

        WINDOW_WIDTH = 60  # number of columns of window box
        WINDOW_HEIGHT = 20  # number of rows of window box

# setup window
        curses.initscr()
        win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)  # rows, columns
        win.keypad(1)
        curses.noecho()
        curses.curs_set(0)
        win.border(0)
        win.nodelay(1)  # -1

# snake and food
        snake = [(4, 4), (4, 3), (4, 2)]
        food = (6, 6)

        win.addch(food[0], food[1], '#')
# game logic
        score = 0

        ESC = 27
        key = curses.KEY_RIGHT

        while key != ESC:
            win.addstr(0, 2, 'Score ' + str(score) + ' ')
            win.timeout(150 - (len(snake)) // 5 + len(snake)//10 %
                120)  # increase speed

            prev_key = key
            event = win.getch()
            key = event if event != -1 else prev_key

            if key not in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, ESC]:
                key = prev_key

    # calculate the next coordinates
            y = snake[0][0]
            x = snake[0][1]
            if key == curses.KEY_DOWN:
                y += 1
            if key == curses.KEY_UP:
                y -= 1
            if key == curses.KEY_LEFT:
                x -= 1
            if key == curses.KEY_RIGHT:
                x += 1

            snake.insert(0, (y, x))  # append O(n)

    # check if we hit the border
            if y == 0:
                break
            if y == WINDOW_HEIGHT-1:
                break
            if x == 0:
                break
            if x == WINDOW_WIDTH - 1:
                break

    # if snake runs over itself
            if snake[0] in snake[1:]:
                break

            if snake[0] == food:
        # eat the food
                score += 1
                food = ()
                while not food:
                    food = (randint(1, WINDOW_HEIGHT-2), randint(1, WINDOW_WIDTH - 2))
                    if food in snake:
                        food = ()
                win.addch(food[0], food[1], '#')
            else:
        # move snake
                last = snake.pop()
                win.addch(last[0], last[1], ' ')

            win.addch(snake[0][0], snake[0][1], '*')

        curses.endwin()
        print(f"\nFinal score = {score}\n")
        score_id = uuid.uuid4().hex
        self.add_score(score_id, score)


    def table_exists(self, table_name):
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

    def add_score(self, score_id, score):
        """
        adds scores to dynamo db table
        """
        try:
            if dynamo_db.Table("HighScores").put_item(
                Item={
                    "ScoreId" : score_id,
                    "Score": score
                }
            ):
                return True

        except Exception as error:
            print(error)

        return False

    def load_scores_from_db(self):
        """
        loads scores from dynamo db table
        """
        try:
            response = dynamo_db.Table("HighScores").scan()
            scores = []
            for item in response["Items"]:
                scores.append(int(item["Score"]))
            scores.sort(reverse=True)
            return scores
        except Exception as error:
            print(error)
            return []

    def get_high_score(self):
        """
        returns high score from list of scores
        """
        return max(self.load_scores_from_db())

        

    def create_bucket(self, region_override=None):
        """
        creates high scores bucket
        """
        try:
            if region_override is not None:
                region = region_override
            elif region_override is None:
                s3_client.create_bucket(Bucket="sdev400-7380-high-scores")
            else:
                s3_client.create_bucket(Bucket="sdev400-7380-high-scores",
                                        CreateBucketConfiguration={"LocationConstraint": region})
        except AttributeError as error:
            print(f"\nFatal error {error}, closing application")
            sys.exit()

    def update_score_file(self):
        """
        gets current high scores from database table, writes returned scores to file,
        and uploads file to sdev-400-7380-high-scores bucket
        """
        scores = self.load_scores_from_db()
        try:
            with open("scores.txt", "r+", encoding="utf-8") as f:
                for line in scores:
                    f.write(str(line))
                try:
                    s3_client.put_object(Bucket="sdev400-7380-high-scores",
                                     Key="./scores.txt", Body=open("scores.txt", "rb"))
                except ClientError as error:
                    print(error)
                    f.close()
                f.close()
                print("\nScores file updated\n")
        except IOError:
            print("\nPlease download scores file first\n")
            
    def download_score_file(self):
        """
        downloads scores.txt from sdev-400-7380-high-scores bucket
        """
        try:
            bucket_objects = s3_client.list_objects_v2(Bucket="sdev400-7380-high-scores")
            if bucket_objects["KeyCount"] == 0:
                print("High Scores bucket is empty")
            else:
                s3_client.download_file(
                    "sdev400-7380-high-scores", "./scores.txt", "scores.txt"
                )
                print("\nScores file downloaded\n")
        except ClientError as error:
            print(error)

    def load_scores_from_bucket(self):
        """
        Fetches file from bucket, reads file, prints contents to console
        """
        print("\nScores:")
        bucket_objects = s3_client.list_objects_v2(Bucket="sdev400-7380-high-scores")
        if bucket_objects["KeyCount"] == 0:
            print("High Scores bucket is empty\n")
            return

        for obj in bucket_objects.get("Contents"):
            data = s3_client.get_object(
                Bucket="sdev400-7380-high-scores", Key=obj.get("Key"))
            contents = data["Body"].read()
            for line in contents.decode("utf-8"):
                print (line)
        print()


if __name__ == "__main__":
    app = App()
    while True:
        print_menu()
        user_select = str(input("Select number from menu: "))
        if user_select == "1":
            app.game()
        elif user_select == "2":
            print("\nScores:")
            db_scores = app.load_scores_from_db()
            for s in db_scores:
                print(s)
            print()
        elif user_select == "3":
            app.update_score_file()
        elif user_select == "4":
            app.download_score_file()
        elif user_select == "5":
            app.load_scores_from_bucket()
        elif user_select == "6":
            break
        else:
            print("That is not one of the options.")
