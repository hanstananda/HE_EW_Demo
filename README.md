# HE EW Library Aggregation Demo 

## Subproject division

This project is further divided to 3 different subproject to handle different party roles in the network. Namely: 
*   Server  
    Located under `server`. By default, the server will be hosted on port `7000`.
*   Workers  
    Located under `workers`. By default, it will spawn two workers with port `7101` and `7102`. 
*   Aggregator  
    Located under `Aggregator`. By default, the server will be hosted on port `7200`.

Please refer to the respective subprojects' readme for more information. 

## Setup Notes

This project requires the HE_EW_CPP library. The current working library is available at the `library` directory under `HE_lib` submodule. This submodule is currently available from [here](https://github.com/hanstananda/HE_EW_CPP)

## Usage guide 
1.  Start the `server`, followed by `workers` and `aggregator` respectively. 
2.  To start training, go to any worker endpoints and invoke the `/train` API.
    ```
    localhost:7101/train 
    ```
    The training is currently set to perform 1 training epoch. 
    Afterwards, it will automatically send the resulting encrypted weight to the Aggregator service. 
3.  After the workers have finished their training, you can invoke the `/agg_val` API on the Aggregator service 
    to aggregate the weights and transfer it to the server. 
    ```
    localhost:7200/agg_val 
    ```
4.  To check the current accuracy of the model stored in the server, we can use the `/evaluate_model` API. 
    ```
    localhost:7000/evaluate_model
    ```
    You will get a json response containing current test accuracy and loss value, which looks something like this: 
    ```json
    {
        "error_code": 0,
        "error_message": "",
        "result": {
            "accuracy": 0.9749000072479248,
            "loss": 0.08522004634141922
        },
        "success": true
    }
    ```
    

### Model Used
The model description is located under `server/model/` package. 
The current model is built based on the [Keras Simple MNIST Convnet](https://keras.io/examples/vision/mnist_convnet/) example, which is:
```
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d (Conv2D)              (None, 26, 26, 32)        320       
_________________________________________________________________
max_pooling2d (MaxPooling2D) (None, 13, 13, 32)        0         
_________________________________________________________________
conv2d_1 (Conv2D)            (None, 11, 11, 56)        16184     
_________________________________________________________________
max_pooling2d_1 (MaxPooling2 (None, 5, 5, 56)          0         
_________________________________________________________________
flatten (Flatten)            (None, 1400)              0         
_________________________________________________________________
dropout (Dropout)            (None, 1400)              0         
_________________________________________________________________
dense (Dense)                (None, 10)                14010     
=================================================================
Total params: 30,514
Trainable params: 30,514
Non-trainable params: 0
_________________________________________________________________
``` 

### Performance benchmarks 
The following is the result of model shown above:  
#### Full dataset baseline (without secure aggregation)
*   After 1 epoch:
    ```
    Test loss: 0.09053578227758408
    Test accuracy: 0.972599983215332
    ```
*   After 5 epochs: 
    ```
    Test loss: 0.04196620732545853
    Test accuracy: 0.9855999946594238
    ```
*   After 10 epochs: 
    ```
    Test loss: 0.02865796536207199
    Test accuracy: 0.9907000064849854
    ```
*   After 15 epochs: 
    ```
    Test loss: 0.025408869609236717
    Test accuracy: 0.991100013256073
    ```
#### Secure aggregation with full dataset distributed evenly for each worker 
We then started to test with 2 workers having 30000 datasets each, totalling 60000(size of MNIST Train dataset)
*   After 1 epoch:
    ```
    Test loss: 0.14280813932418823
    Test accuracy: 0.9613000154495239
    ```
*   After 2 epochs:
    ```
    Test loss: 0.08687152713537216
    Test accuracy: 0.9757000207901001
    ```
*   After 3 epochs: 
    ```
    Test loss: 0.07367851585149765
    Test accuracy: 0.9765999913215637
    ```
*   After 4 epochs: 
    ```
    Test loss: 0.07604873925447464
    Test accuracy: 0.9760000109672546
    ```
*   After 5 epochs: 
    ```
    Test loss: 0.054439812898635864
    Test accuracy: 0.9833999872207642
    ```

*   After 6 epochs: 
    ```
    Test loss: 0.05641406774520874
    Test accuracy: 0.9819999933242798
    ```

*   After 7 epochs: 
    ```
    Test loss: 0.04702882096171379
    Test accuracy: 0.9850000143051147
    ```

*   After 8 epochs: ^
    ```
    Test loss: 0.22553034126758575
    Test accuracy: 0.932699978351593
    ```

*   After 9 epochs: 
    ```
    Test loss: 0.04297580569982529
    Test accuracy: 0.9850999712944031
    ```

*   After 10 epochs: 
    ```
    Test loss: 0.04515307769179344
    Test accuracy: 0.9853000044822693
    ```

1.  The encryption performed on the layer weights after training took 0.8205s (0.0251s) 

    Samples (in seconds): 
    ```
    0.8200380000000003
    0.8351589999999973
    0.8198950000000025
    0.8413439999999923
    0.8148419999999987
    0.8542319999999961
    0.8411420000000192
    0.8340279999999893
    0.7856249999999818
    0.8258749999999964
    0.8273169999999936
    0.7947070000000167
    0.814047999999957
    0.7712189999999737
    0.8390849999999546
    0.7916490000000067
    0.8553169999999568
    0.8537789999999745
    0.807988000000023
    0.7819030000000566
    ```

2.  The aggregation performed on the layer weights from 2 workers took 2.1839s (0.0651s)

    Samples (in seconds): 
    ```
    2.243722 
    2.2302220000000004
    2.100588
    2.2430559999999993
    2.209754
    2.2294059999999973
    2.0473219999999976
    2.167800999999997
    2.1970270000000056
    2.1701869999999985
    ```
3.  The decryption performed on the layer weights took 0.7381s (0.0258s)

    Samples (in seconds): 
    ```
    0.7511620000000003
    0.758481999999999
    0.7262979999999999
    0.6881419999999991
    0.7315769999999979
    0.7610589999999995
    0.7517089999999982
    0.768806000000005
    0.7055100000000039
    0.738470999999997
    ```

### Additional Notes
*   After some trials, it is known that the maximum integer supported is around 32768. 
    Therefore, we need to map our floating values to integer within this range. 

*   ^: It is noted that sometimes the decryption occasionally returns a random number(possibly failure of decryption?) which causes accuracy drops. 
