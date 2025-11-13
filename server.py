# server.py
import time
from concurrent import futures
import grpc
import banking_pb2
import banking_pb2_grpc
import uuid
from datetime import datetime

# in-memory storage
ACCOUNTS = {
    'Harshit': 1000.0,
    'BITS': 500.0,
}
TRANSACTIONS = []

class AccountServiceServicer(banking_pb2_grpc.AccountServiceServicer):
    def GetBalance(self, request, context):
        user_id = request.user_id
        if user_id not in ACCOUNTS:
            return banking_pb2.GetBalanceResponse(balance=0.0, error=f"user '{user_id}' not found")
        return banking_pb2.GetBalanceResponse(balance=ACCOUNTS[user_id], error="")

    def UpdateBalance(self, request, context):
        user_id = request.user_id
        new_balance = request.new_balance
        if user_id not in ACCOUNTS:
            return banking_pb2.UpdateBalanceResponse(success=False, error=f"user '{user_id}' not found")
        if new_balance < 0:
            return banking_pb2.UpdateBalanceResponse(success=False, error="balance cannot be negative")
        ACCOUNTS[user_id] = new_balance
        return banking_pb2.UpdateBalanceResponse(success=True, error="")

class TransactionServiceServicer(banking_pb2_grpc.TransactionServiceServicer):
    def InitiateTransfer(self, request, context):
        fr = request.from_user_id
        to = request.to_user_id
        amt = request.amount
        if amt <= 0:
            return banking_pb2.InitiateTransferResponse(success=False, error="amount must be positive", transaction_id="")
        if fr not in ACCOUNTS:
            return banking_pb2.InitiateTransferResponse(success=False, error=f"from user '{fr}' not found", transaction_id="")
        if to not in ACCOUNTS:
            return banking_pb2.InitiateTransferResponse(success=False, error=f"to user '{to}' not found", transaction_id="")
        if ACCOUNTS[fr] < amt:
            return banking_pb2.InitiateTransferResponse(success=False, error="insufficient funds", transaction_id="")
        ACCOUNTS[fr] -= amt
        ACCOUNTS[to] += amt
        tx_id = str(uuid.uuid4())
        tx = {
            'transaction_id': tx_id,
            'from_user_id': fr,
            'to_user_id': to,
            'amount': amt,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        TRANSACTIONS.append(tx)
        return banking_pb2.InitiateTransferResponse(success=True, error="", transaction_id=tx_id)

    def GetTransactionHistory(self, request, context):
        user = request.user_id
        if user not in ACCOUNTS:
            return banking_pb2.GetTransactionHistoryResponse(transactions=[], error=f"user '{user}' not found")
        user_txs = []
        for t in TRANSACTIONS:
            if t['from_user_id'] == user or t['to_user_id'] == user:
                user_txs.append(banking_pb2.Transaction(
                    transaction_id=t['transaction_id'],
                    from_user_id=t['from_user_id'],
                    to_user_id=t['to_user_id'],
                    amount=t['amount'],
                    timestamp=t['timestamp']
                ))
        return banking_pb2.GetTransactionHistoryResponse(transactions=user_txs, error="")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    banking_pb2_grpc.add_AccountServiceServicer_to_server(AccountServiceServicer(), server)
    banking_pb2_grpc.add_TransactionServiceServicer_to_server(TransactionServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Server started on port 50051')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
