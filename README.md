## Assignment 1

### 1. gRPC Server (server.py)

- Use the following command line to generate the corresponding `bank_pb2_grpc.py` and `bank_pb2.py` from `bank.proto`.

  ```shell
  python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. bank.proto
  ```

- The server should listen on port 50051. 

  ```python
   # ...
   bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(), server)
   server.add_insecure_port('localhost:50051')
   #..
  ```

- The server exposes the following RPC methods:

  > These functions are implemented in the `BankService` class within `server.py`, each with built-in error handling.

  1. CreateAccount / 2. GetBalance /3. Deposit / 4. Withdraw / 5. CalculateInterest

- Handle errors : See "5. Error Handling"

### 2. Redis Integration

This project uses Redis to store a hash structure. The structure is as follows:

```lua
Key: "001" (account_id)
--------------------------
| Field         | Value   |
|--------------|---------|
| balance      | 0       |
| account_type | savings |
--------------------------
```

### 3. Client Application

- `client.py`  provides following functions that interact with the gRPC server

  - create_account (account_id: str, account_type: str) -> str / get_balance(account_id: str) -> float / ...(5 methods)
  - Successful operations have corresponding `confirmation messages` (response.message).
  - Failed operations have corresponding `error codes` and `error messages`.

  ```python
  # For example: 
  def deposit(stub, account_id: str, amount: float):
      try:
          response = stub.Deposit(bank_pb2.DepositRequest(
              account_id=account_id, amount=amount))
          return (response.message, "The new balance is >>", response.balance)
      except grpc.RpcError as e:
          return f"❌Error:\n error code: {e.code()},\nerror message: {e.details()}"
  ```


- Implementation: See "6. Results Display"

### 4. Concurrency Handling

- [x] Design the server to handle multiple clients simultaneously.

  ```python
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  ```

​		 This line creates a thread pool with a maximum of **10 worker threads**.

- [x] Implement locking mechanisms to ensure data consistency, especially during updates to account balances.

  In server.py,  "**Lock**"is used to **synchronize access** to a shared resource, ensuring that only one thread can execute the critical section at a time.

  ```python
   def __init__(self):
      		# 1️⃣ This creates a lock, preventing multiple threads from modifying shared resources simultaneously
          self.lock = threading.Lock()
  
      def CreateAccount(self, request, context):
          r = redis.Redis(host='localhost', port=6379, db=0)
          # 2️⃣ This acquires the lock before executing the critical section.
          with self.lock:
          	 #... 
             # ...
             # ... 
  ```

### 5. Error Handling 

1. Define each error message's `message` through an `Enum` class. This eliminates the need to repeatedly write long messages.

   ```python
   class MESSAGE(Enum):
       SUCCESS = '✅ Success! '
       ACCOUNT_ALREADY_EXISTS = 'Account already exists'
       ACCOUNT_NOT_FOUND = 'Account not found. Please check the account ID.'
       NEGATIVE_DEPOSIT = 'Transaction amount must be positive.'
       INSUFFICIENT_FUNDS = 'Insufficient funds for the requested withdrawal.'
       INVALID_INREREST_RATE = 'Annual interest rate must be a positive value.'
   ```

   In each function:

   ```python
   def Deposit(self, request, context):
           # ...
       		# ...
               #   Negative deposit
               if request.amount <= 0:
                   context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                   context.set_details(MESSAGE.NEGATIVE_DEPOSIT.value)
                   # ...
   				# ...
       		# ...
   ```

   |                                             | CreateAccount             | GetBalance | Deposit | Withdraw | CalculateInterest |
   | ------------------------------------------- | ------------------------- | ---------- | ------- | -------- | ----------------- |
   | ⚠️**Account not found**                      | (Account already  exists) | ✅          | ✅       | ✅        | ✅                 |
   | **⚠️Negative deposit or withdrawal amounts** |                           |            | ✅       | ✅        |                   |
   | **⚠️Insufficient funds for withdrawals**     |                           |            |         | ✅        |                   |
   | **⚠️ Invalid interest rate values**          |                           |            |         |          | ✅                 |



### 6. Results Display


| Welcome message                                                                                                                                                                                                                                                                   | Exit Message                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <img src="https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=NDkxZTdjYmMwYzRjOTVjMDBjZWJlYjQzODVlZWIxNmFfMmFLRVZ6QmpyQndtTzdFYWFOVE1mNmFFMld6Z2RUY2JfVG9rZW46VUM1MGJkWEVtb3c4Z3V4ZmJ4U2NHTXA4bjVTXzE3MzgzNzc3ODg6MTczODM4MTM4OF9WNA" style="zoom:30%;" /> | <img src="https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=OTIwZDdjZWUzNDYwMmVkMDU2MTUwZWY1NzA1NDViNWJfVkdrY2RuaVNEcW9SUnNwRDdQN2FqUjUwbE5KOUluNHRfVG9rZW46QXB1cGJzSjR3bzQzOVl4NjE1MmN0VXNJbmliXzE3MzgzNzg1NDc6MTczODM4MjE0N19WNA" style="zoom:30%;" /> |


|         | Create a new account                                                                                                                                                                                                                                                                                                     | Get Balance                                                                                                                                                                                                                                                                 | Deposit                                                                                                                                                                                                                                                                           | Withdraw                                                                                                                                                                                                                                                                           | Caculate Interest                                                                                                                                                                                                                                                                      |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Success | <img src="https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=MmNlN2VmN2FkODExZmJlMzBjM2Y2ZmY4NGVhMDIwOTZfUnBwODI1ejRCS0E1cFN4NFpLNXY4V3p4WXFiMWdrOXBfVG9rZW46UjAyZmI3SzJ1b214Mm94TDhOUGM2TTBZbmJkXzE3MzgzNzY2MzA6MTczODM4MDIzMF9WNA" alt="img" style="zoom:30%;" />                              | ![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=MzA5YTMxMjRlZWRmYjk4ZjVlOTNhNGY0OGZjMjU5YmJfUGpFTzBvT1BURDRRbUZjdm1UODZicXJGa1lNN2c4UXBfVG9rZW46Tk1BTmJEczdlb21FWmd4ZllERmMzY2txbktRXzE3MzgzNzc4ODk6MTczODM4MTQ4OV9WNA)                      | ![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=ZWY1YTliZWJlYWY1M2UwZDllNTI4NTExMTA4YjdjNmZfWW9YRllsd0tWeFFiQ01jcWFtQUNZajcxYTBEcUEzZ0NfVG9rZW46THR4OWJ2aVpCb216YVh4WVBXV2NrYzlabkVmXzE3MzgzNzgwNDk6MTczODM4MTY0OV9WNA)                            | ![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=YzRiYjQwOWI5ZjBmY2UxYmFlY2U4ZTdlMTZhYzJmZDdfbElPRnI2WlVMUm1TWmhEZDlOblhaOHpYcUxKV1VvaG1fVG9rZW46VEk2MWIxTmhKbzZCQ1F4Rm54RWNFM0pJbkhiXzE3MzgzNzgzMzg6MTczODM4MTkzOF9WNA)                             | ![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGI2ZjdmODJmNDQxMjhlZWMzZTU5MjEwY2YyYjk1MmNfVk12Q044RFRlUlFiMHlmT2thM3ZmQ0xad0wyRzBWSmJfVG9rZW46QXBWbmJHaEVlb1JSWW94S2hTTmNwZEtjblc0XzE3MzgzNzgzNzQ6MTczODM4MTk3NF9WNA)                                 |
| Fail    | Account  Already Exists<br /><img src="https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=OTUwYjVmNzE0ZmQ5Nzg2ODQ5NjRhZjliMTI3Mjc0Y2FfbTI1cDlOb2psaWhJaXc1V1N1VzBGTFMwNW1SZG5UZVVfVG9rZW46VGxxQWJBc25lb0ZVdFR4WHNWT2M2Z2RjbkxnXzE3MzgzNzY2NjA6MTczODM4MDI2MF9WNA" alt="img" style="zoom:30%;" /> | Account not found<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=NzlhYjRkMmNiOTI4Mjc5MmZiMzQ4ZDU2YWZlZGVjMzlfcTNBZXFnVHFrRkN6eW1mdG5sUUJ2amtNQmF4VEc1TTdfVG9rZW46Tk03dWJQZVBVb0RaaG14ekhCd2NKYkF4bkh3XzE3MzgzNzc5MDU6MTczODM4MTUwNV9WNA) | Account not Found<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=NjYzZjdiOTczZDEyNTgyZTFmNzkzMzRhNTgxYTgyZDBfWTB1ZE5sSmNSOERMMDBoU3QzRTVhOEdCbDBxdGlJRklfVG9rZW46VHhBcWJBNUJpbzhCQk54SnlscGM5OFVCblZlXzE3MzgzNzgwNjM6MTczODM4MTY2M19WNA)       | Account not Found<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=OGZmYzExNjU4ZTlhYTc2NmJmOGI3YTMzNDM4NWQxOWFfY3F2NVk3MVRqMk9YQU5SdFNhSlh2TXlzMmZIeGtsRkRfVG9rZW46SHpwOGJqdHN5bzlxcW54Ujd4NGMweXdDblFjXzE3MzgzNzgyODE6MTczODM4MTg4MV9WNA)        | Account not Found<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTYxYTBiMGFkMjVmMjExOTcwYWI4MmFiMmI4MzVkM2NfRXVOeHdPWVF0a0hwTm85bUZRYkFkdjFCR01JNmJDUFFfVG9rZW46UEdBV2JDYjVxbzBLTWV4bGlOVWM1OHVQbmRkXzE3MzgzNzg0MDM6MTczODM4MjAwM19WNA)            |
|         |                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                             | Negative Deposit Amount<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGUyOTczNmE4ZjRhMDMzMjdmN2NlYzZhNzY0MmNmYjBfYkQwVkFOeTV3THpXeUFHQXdoQXNBd2pjcHdSRGVzZ3dfVG9rZW46RDgyR2JRTUNNb0xQV3B4VlQzRGNDM0JlbktoXzE3MzgzNzgxMTI6MTczODM4MTcxMl9WNA) | Negative Withdraw Amount<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=NGYyNTg1ZmM4MzllZjI2OGQxYmY0NjM4ZTBlZGE1ZGVfc0k2SW5FYmh4OUFLYmZoVk5vSDdrQlZHek9JQWpGT2dfVG9rZW46V2Q4a2JtMXJCb0wzN1d4Y0dYNGNCZ3VqbmdjXzE3MzgzNzgyOTM6MTczODM4MTg5M19WNA) | Invalid interest rate values<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTA3Y2ZlZTBkOWQ2NWU4NzI5MGI2YTNhNWQxYjkxYmFfRGlZZFpKWnk4SThnVFcxdG0wcnpJZjN2bTdUYTR5bnpfVG9rZW46UEdYV2J4SGlUbzB4cmF4c2xhT2NIdzV0bjhmXzE3MzgzNzg0ODM6MTczODM4MjA4M19WNA) |
|         |                                                                                                                                                                                                                                                                                                                          |                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                                   | Insufficient fund<br>![](https://dbmnb2zb74.feishu.cn/space/api/box/stream/download/asynccode/?code=YWFjM2Y4MGNhYjUxZDk2N2NkZjliYjkzZGQwMDBkYWZfM2xtZk1QZWRDdHJubnVCbFRkQUwwT0lNQ055dFh1NUNfVG9rZW46SW5ud2Iya2sxb1piRlZ4R0piRGNNaFVMblhjXzE3MzgzNzgzMTc6MTczODM4MTkxN19WNA)        |                                                                                                                                                                                                                                                                                        |

