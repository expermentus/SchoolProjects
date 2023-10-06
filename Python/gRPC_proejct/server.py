from concurrent import futures
import grpc
import frequencyCalculator_pb2
import frequencyCalculator_pb2_grpc
import logging

class frequencyCalculatorServicer(frequencyCalculator_pb2_grpc.frequencyCalculatorServicer):

    def Calculate(self, request, context):
        counts = dict()
        words = request.input.split()

        for word in words:
            word = ''.join(letter for letter in word if letter.isalnum())
            word = word.lower()
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1

        # Create a KeyPairs response message and set the pair field
        key_pairs = [frequencyCalculator_pb2.KeyPair(word=word, count=count) for word, count in counts.items()]
        response = frequencyCalculator_pb2.KeyPairs(pair=key_pairs)
        return response

    def Combine(self, request, context):
        total_count = sum(pair.count for pair in request.pair)  # Calculate the total word count
        print(f"Combined Result on Server: {total_count}")
        result = frequencyCalculator_pb2.KeyPairs(pair=[frequencyCalculator_pb2.KeyPair(word="", count=total_count)])  # Use KeyPairs message
        return result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frequencyCalculator_pb2_grpc.add_frequencyCalculatorServicer_to_server(frequencyCalculatorServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server running")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
