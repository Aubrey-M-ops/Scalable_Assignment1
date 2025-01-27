from concurrent import futures
import threading

import grpc
from protos import bank_pb2, bank_pb2_grpc
import redis
from enum import Enum

# Define the messages that will be returned to the client
# This corresponds to " 5. Error Handling"
class MESSAGE(Enum):
    SUCCESS = '✅ Success! '
    ACCOUNT_ALREADY_EXISTS = 'Account already exists'
    ACCOUNT_NOT_FOUND = 'Account not found. Please check the account ID.'
    NEGATIVE_DEPOSIT = 'Transaction amount must be positive.'
    INSUFFICIENT_FUNDS = 'Insufficient funds for the requested withdrawal.'
    INVALID_INREREST_RATE = 'Annual interest rate must be a positive value.'


class BankService(bank_pb2_grpc.BankServiceServicer):
    def __init__(self):
        self.lock = threading.Lock()

    def CreateAccount(self, request, context):
        r = redis.Redis(host='localhost', port=6379, db=0)
        with self.lock:
            # make sure the account doesn't already exist
            if r.exists(request.account_id):
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(MESSAGE.ACCOUNT_ALREADY_EXISTS.value)
                return bank_pb2.AccountResponse(
                    account_id=request.account_id,
                    message=MESSAGE.ACCOUNT_ALREADY_EXISTS.value
                )
            else:
                # initialize the account
                r.hset(request.account_id, 'balance', 0)
                r.hset(request.account_id, 'account_type', request.account_type)
                return bank_pb2.AccountResponse(
                    account_id=request.account_id,
                    message=MESSAGE.SUCCESS.value
                )

    def GetBalance(self, request, context):
        r = redis.Redis(host='localhost', port=6379, db=0)
        # make sure the account exists
        if not r.exists(request.account_id):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(MESSAGE.ACCOUNT_NOT_FOUND.value)
            return bank_pb2.BalanceResponse(
                account_id=request.account_id,
                balance=0,
                message=MESSAGE.ACCOUNT_NOT_FOUND.value
            )
        balance = float(r.hget(request.account_id, 'balance').decode('utf-8'))
        return bank_pb2.BalanceResponse(
            account_id=request.account_id,
            balance=int(balance),
            message=MESSAGE.SUCCESS.value
        )

    def Deposit(self, request, context):
        r = redis.Redis(host='localhost', port=6379, db=0)
        with self.lock:
            if not r.exists(request.account_id):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(MESSAGE.ACCOUNT_NOT_FOUND.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=0,
                    message=MESSAGE.ACCOUNT_NOT_FOUND.value
                )
            #   Negative deposit
            if request.amount <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(MESSAGE.NEGATIVE_DEPOSIT.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=0,
                    message=MESSAGE.NEGATIVE_DEPOSIT.value
                )
            #   Deposit the amount successfully
            balance = float(r.hget(request.account_id, 'balance').decode('utf-8'))
            new_balance = balance + request.amount
            r.hset(request.account_id, 'balance', new_balance)
            return bank_pb2.TransactionResponse(
                account_id=request.account_id,
                balance=new_balance,
                message=MESSAGE.SUCCESS.value
            )

    def Withdraw(self, request, context):
        r = redis.Redis(host='localhost', port=6379, db=0)
        with self.lock:
            if not r.exists(request.account_id):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(MESSAGE.ACCOUNT_NOT_FOUND.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=0,
                    message=MESSAGE.ACCOUNT_NOT_FOUND.value
                )
            balance = float(r.hget(request.account_id, 'balance').decode('utf-8'))
            #   Negative withdrawal
            if request.amount <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(MESSAGE.NEGATIVE_DEPOSIT.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=balance,
                    message=MESSAGE.NEGATIVE_DEPOSIT.value
                )
           #   Insufficient funds
            if balance < request.amount:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details(MESSAGE.INSUFFICIENT_FUNDS.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=balance,
                    message=MESSAGE.INSUFFICIENT_FUNDS.value
                )
            #   Withdraw the amount successfully
            new_balance = balance - request.amount
            r.hset(request.account_id, 'balance', new_balance)
            return bank_pb2.TransactionResponse(
                account_id=request.account_id,
                balance=new_balance,
                message=MESSAGE.SUCCESS.value
            )

    def CalculateInterest(self, request, context):
        r = redis.Redis(host='localhost', port=6379, db=0)
        with self.lock:
            if not r.exists(request.account_id):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(MESSAGE.ACCOUNT_NOT_FOUND.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=0,
                    message=MESSAGE.ACCOUNT_NOT_FOUND.value
                )
            balance = float(r.hget(request.account_id, 'balance').decode('utf-8'))
            #  Invalid interest rate
            if request.annual_interest_rate <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(MESSAGE.INVALID_INREREST_RATE.value)
                return bank_pb2.TransactionResponse(
                    account_id=request.account_id,
                    balance=balance,
                    message=MESSAGE.INVALID_INREREST_RATE.value
                )
            #  Calculate the interest and update the balance
            interest = balance * (request.annual_interest_rate / 100)
            new_balance = balance + interest
            r.hset(request.account_id, 'balance', new_balance)
            return bank_pb2.TransactionResponse(
                account_id=request.account_id,
                balance=new_balance,
                message=MESSAGE.SUCCESS.value
            )


def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(), server)
    server.add_insecure_port('localhost:50051')
    print("gRPC starting")
    server.start()
    server.wait_for_termination()
    exit()


if __name__ == '__main__':
    server()
