import os
import glob
import threading
import grpc
import frequencyCalculator_pb2_grpc
import frequencyCalculator_pb2
import logging

def calculate(stub, filename):
    with open(filename, 'r') as file:
        text = file.read()
    request = frequencyCalculator_pb2.Text(input=text)

    try:
        # Using RPC method
        response = stub.Calculate(request)
        return response
    except grpc.RpcError as e:
        print(f"RPC failed with error: {e}")
        return None

def combine(stub, results):
    try:
        combined_result = []        # Prepare a list to hold the combined results

        for response in results:    # Iterate through the response messages in results
            combined_result.extend(response.pair)

        word_count = {}
        for pair in combined_result:
            if pair.word in word_count:
                word_count[pair.word] += pair.count
            else:
                word_count[pair.word] = pair.count

        return word_count
    except grpc.RpcError as e:
        print(f"RPC failed with error: {e}")
        return None

def worker(threadname, filename, results, stub, lock):
    thread_result = calculate(stub, filename)
    with lock:
        results.append(thread_result)

def run():
    allwords = []
    channel = grpc.insecure_channel('localhost:50051')
    stub = frequencyCalculator_pb2_grpc.frequencyCalculatorStub(channel)
    threads = []
    numberOfFiles = len(glob.glob('input/*.txt'))
    filenames = glob.glob('input/*.txt')
    results = []
    lock = threading.Lock()

    for i in range(numberOfFiles):
        filename = filenames[i]
        thread = threading.Thread(target=worker, args=(f"Thread-{i+1}", filename, results, stub, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Combine all the results after all threads finish
    combined_result = combine(stub, results)

    sorted_result = dict(sorted(combined_result.items(), key=lambda item: item[1], reverse=True))

    print(f"Sorted Combined Result: {sorted_result}")

if __name__ == '__main__':
    logging.basicConfig()
    run()