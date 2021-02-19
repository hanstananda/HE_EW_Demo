import requests
import pandas as pd

WORKER1_HOST = "http://localhost:7101/"
WORKER2_HOST = "http://localhost:7102/"
AGGREGATOR_HOST = "http://localhost:7200/"
SERVER_HOST = "http://localhost:7000/"
WORKER_TRAIN_ENDPOINT = "train"
AGGREGATOR_ENDPOINT = "agg_val"
SERVER_EVALUATE_ENDPOINT = "evaluate_model"

encryption_time_worker1 = []
encryption_time_worker2 = []
aggregation_time = []
decryption_time = []
test_accuracy = []
test_loss = []

for i in range(20):
    resp_worker1 = requests.get(WORKER1_HOST + WORKER_TRAIN_ENDPOINT)
    resp_worker1_json = resp_worker1.json()
    encryption_time_worker1.append(resp_worker1_json['result']['encryption_time'])

    resp_worker2 = requests.get(WORKER2_HOST + WORKER_TRAIN_ENDPOINT)
    resp_worker2_json = resp_worker2.json()
    encryption_time_worker2.append(resp_worker2_json['result']['encryption_time'])

    resp_aggregator = requests.get(AGGREGATOR_HOST + AGGREGATOR_ENDPOINT)
    resp_aggregator_json = resp_aggregator.json()
    aggregation_time.append(resp_aggregator_json['result']['aggregation_time'])
    decryption_time.append(resp_aggregator_json['result']['decryption_time'])

    resp_server = requests.get(SERVER_HOST + SERVER_EVALUATE_ENDPOINT)
    resp_server_json = resp_server.json()
    test_accuracy.append(resp_server_json['result']['accuracy'])
    test_loss.append(resp_server_json['result']['loss'])

df = pd.DataFrame(data={
    'encryption time of worker1': encryption_time_worker1,
    'encryption time of worker2': encryption_time_worker2,
    'aggregation time': aggregation_time,
    'decryption time': decryption_time,
    'test accuracy': test_accuracy,
    'test loss': test_loss,
})
df.index += 1

df.to_csv('test_results_he_ew.csv', index_label="Epochs")
