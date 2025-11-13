# client.py
import grpc
import banking_pb2
import banking_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    account_stub = banking_pb2_grpc.AccountServiceStub(channel)
    tx_stub = banking_pb2_grpc.TransactionServiceStub(channel)

    print("------ NORMAL OPERATIONS ------")

    # check initial balance for Harshit
    resp = account_stub.GetBalance(banking_pb2.GetBalanceRequest(user_id='Harshit'))
    print('Harshit balance:', resp.balance, 'error:', resp.error)

    # perform transfer from Harshit to BITS
    tx_resp = tx_stub.InitiateTransfer(
        banking_pb2.InitiateTransferRequest(
            from_user_id='Harshit', to_user_id='BITS', amount=200
        )
    )
    print('Transfer success:', tx_resp.success, 'error:', tx_resp.error, 'txid:', tx_resp.transaction_id)

    # check updated balances
    print('Harshit balance after:', account_stub.GetBalance(banking_pb2.GetBalanceRequest(user_id='Harshit')).balance)
    print('BITS balance after:', account_stub.GetBalance(banking_pb2.GetBalanceRequest(user_id='BITS')).balance)

    # retrieve Harshit transaction history
    hist = tx_stub.GetTransactionHistory(banking_pb2.GetTransactionHistoryRequest(user_id='Harshit'))
    print('Harshit transactions count:', len(hist.transactions))
    for t in hist.transactions:
        print(f"{t.transaction_id} {t.from_user_id} -> {t.to_user_id} {t.amount} {t.timestamp}")

    print("\n------ ERROR HANDLING TESTS ------")

    # non existent user test
    resp = account_stub.GetBalance(banking_pb2.GetBalanceRequest(user_id='Charlie'))
    print("Error for non existent user 'Charlie':", resp.error)

    # insufficient funds test
    tx_resp = tx_stub.InitiateTransfer(
        banking_pb2.InitiateTransferRequest(
            from_user_id='BITS', to_user_id='Harshit', amount=5000
        )
    )
    print("Error for insufficient funds transfer:", tx_resp.error)

    # invalid amount test
    tx_resp = tx_stub.InitiateTransfer(
        banking_pb2.InitiateTransferRequest(
            from_user_id='Harshit', to_user_id='BITS', amount=-50
        )
    )
    print("Error for negative amount transfer:", tx_resp.error)


if __name__ == '__main__':
    run()
