import boto3
import json
import logging

lambda_client = boto3.client('lambda')

# logger configuration to write  messages to event_log.txt
logging.basicConfig(filename="./event_log.txt",
                    format="%(asctime)s %(levelname)s : %(message)s",
                    datefmt="%Y-%m-%d %H:%M",
                    filemode="a",
                    level=logging.INFO)


def log_message(message=None):
    """
    This function utilizes the logger to log messages
    param message: message to be logged
    """
    if message is not None:
        logging.info(message)

def call_addition(num1=0, num2=0):
    """
    param num 1, num2: user supplied numbers to be added together
    param default value: 0
    return response: response from 'lambda_addition' lambda function
    """
    response = lambda_client.invoke(
        FunctionName = "lambda_addition",
        InvocationType='RequestResponse',  # Can be 'Event' for asynchronous invocation
        LogType='Tail',
        Payload = json.dumps({
            "num1" : f"{num1}",
            "num2" : f"{num2}"
            })
        )
    result = response['Payload'].read().decode('utf-8')
    print("result: " + result + "\n")
    log_message(f"lambda_addition function called successfuly with result: \
        {result}")
    
    

def call_multiply(num1=0, num2=1, num3=1):
    """
    param num 1, num2, num3: user supplied numbers to be multiplied together
    param default value: 0 or 1
    return response: response from 'lambda_multiply' lambda function
    """
    response = lambda_client.invoke(
        FunctionName = "lambda_multiply",
        InvocationType='RequestResponse',  # Can be 'Event' for asynchronous invocation
        LogType='Tail',
        Payload = json.dumps({
            "num1" : f"{num1}",
            "num2" : f"{num2}",
            "num3" : f"{num3}"
            })
        )
    
    result = response['Payload'].read().decode('utf-8')
    print("result: " + result + "\n")
    log_message(f"lambda_multiply function called successfuly with result: \
        {result}")
    
    
def call_power(base=0, exponent=1):
    """
    param base, exponent: user supplied numbers to be used in an exponential calculation
    param default value: 0 or 1
    return response: response from 'lambda_power' lambda function
    """
    response = lambda_client.invoke(
        FunctionName = "lambda_power",
        InvocationType='RequestResponse',  # Can be 'Event' for asynchronous invocation
        LogType='Tail',
        Payload = json.dumps({
            "base" : f"{base}",
            "exponent" : f"{exponent}"
            })
        )
    
    result = response['Payload'].read().decode('utf-8')
    print("result: " + result + "\n")
    log_message(f"lambda_power function called successfuly with result: \
        {result}")
    


def print_menu():
    print("Welcome to the Lambda function caller\n")
    print("1. Add two numbers")
    print("2. Multiply up to 3 numbers")
    print("3. Exponential computation")
    print("4. Exit program\n")

def validate_numbers(function_name=None):
    """
    param function name: name of the function being called.
    Only needs to be specified if calling lambda multiply
    return num1, num2, num3: values of input numbers
    """
    loop_control = True
    num3 = None
    while loop_control:
        try:
            print("Enter numbers to use")
            num1 = float(input("Input first number: "))
            num2 = float(input("Input second number: "))
            if function_name == "lambda_multiply":
                num3 = float(input("Input third number: "))
            
            loop_control = False
        except ValueError as e:
            log_message(e)
            print("Check input. Only numbers are accepted.")
    
    if num3 is None:
        return[num1, num2]
    else:
        return[num1, num2, num3]
    
def handle_addition():
    user_nums = validate_numbers()
    call_addition(user_nums[0], user_nums[1])
    
def handle_multiply():
    user_nums = validate_numbers("lambda_multiply")
    call_multiply(user_nums[0], user_nums[1], user_nums[2])
    

def handle_power():
    user_nums = validate_numbers()
    call_power(user_nums[0], user_nums[1])
    

def main():
    while True:
        print_menu()
        user_select = str(input("Select number from menu: "))
        if user_select == "1":
            handle_addition()
        elif user_select == "2":
            handle_multiply()
        elif user_select == "3":
            handle_power()
        elif user_select == "4":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Plese use the numbers provided in the menu\n")
    
main()
