import grpc
from protos import bank_pb2, bank_pb2_grpc
import inquirer

############### functions that interact with the gRPC server ################


def create_account(stub, account_id: str, account_type: str):
    try:
        response = stub.CreateAccount(bank_pb2.AccountRequest(
            account_id=account_id, account_type=account_type))
        return response.message
    except grpc.RpcError as e:
        return f"❌Error:\n error code: {e.code()},\nerror message: {e.details()}"


def get_balance(stub, account_id: str):
    try:
        response = stub.GetBalance(
            bank_pb2.AccountRequest(account_id=account_id))
        return ("The balance of the current account is >>", response.balance)
    except grpc.RpcError as e:
        return f"❌Error:\n error code: {e.code()},\nerror message: {e.details()}"


def deposit(stub, account_id: str, amount: float):
    try:
        response = stub.Deposit(bank_pb2.DepositRequest(
            account_id=account_id, amount=amount))
        return (response.message, "The new balance is >>", response.balance)
    except grpc.RpcError as e:
        return f"❌Error:\n error code: {e.code()},\nerror message: {e.details()}"


def withdraw(stub, account_id: str, amount: float):
    try:
        response = stub.Withdraw(bank_pb2.WithdrawRequest(
            account_id=account_id, amount=amount))
        return (response.message, "The new balance is >>", response.balance)
    except grpc.RpcError as e:
        return f"❌Error:\n error code: {e.code()},\nerror message: {e.details()}"


def calculate_interest(stub, account_id: str, annual_interest_rate: float):
    try:
        response = stub.CalculateInterest(bank_pb2.InterestRequest(
            account_id=account_id, annual_interest_rate=annual_interest_rate))
        return (response.message, "The new balance is >>", response.balance)
    except grpc.RpcError as e:
        return f"❌Error:\n error code: {e.code()},\nerror message: {e.details()}"

##############################################################################


def run():
    # welcome
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bank_pb2_grpc.BankServiceStub(channel)
        print("✨✨✨ Welcome to the Bank!✨✨✨")
        while True:
            print("****************************")
            questions = [
                inquirer.List('operation',
                              message="Please chooose your service!👇",
                              choices=['Create an account',
                                       'Get Balance',
                                       'Deposit',
                                       'Withdraw',
                                       'Calculate Interest',
                                       'Exit'],
                              ),
            ]

            # Operation List
            answers = inquirer.prompt(questions)
            operation = answers['operation']
            # Create an account
            if operation == 'Create an account':
                account_id = input("Please enter your new account id: ")
                questions = [
                    inquirer.List('account_type',
                                  message="Please select your account type",
                                  choices=['savings', 'checking'],
                                  ),
                ]
                answers = inquirer.prompt(questions)
                account_type = answers['account_type']
                print(create_account(stub, account_id, account_type))
            # get balance
            elif operation == 'Get Balance':
                account_id = input("Please enter your account id: ")
                print(get_balance(stub, account_id))
            # deposit
            elif operation == 'Deposit':
                account_id = input("Please enter your account id: ")
                amount = float(
                    input("Please enter the amount you want to deposit: "))
                print(deposit(stub, account_id, amount))
            # withdraw
            elif operation == 'Withdraw':
                account_id = input("Please enter your account id: ")
                amount = float(
                    input("Please enter the amount you want to withdraw: "))
                print(withdraw(stub, account_id, amount))
            # calculate interest
            elif operation == 'Calculate Interest':
                account_id = input("Please enter your account id: ")
                annual_interest_rate = float(
                    input("Please enter the annual interest rate: "))
                print(calculate_interest(stub, account_id, annual_interest_rate))
            elif operation == 'Exit':
                print("Thank you for using our service! Goodbye!")
                break
            else:
                print("Invalid operation selected.")


if __name__ == '__main__':
    run()
