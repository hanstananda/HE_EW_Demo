# HE Element-Wise Demo server

## Prerequisites
1. Python 3 (Tested on Python 3.7)
2. HE Element-Wise C++ Library

## Running the project

1.  Install the library requirements from pip
    ```bash
    pip install -r requirements.txt
    ```

2.  Install the "HE Element-Wise C++" Library
    ```bash
    cd library
    cmake --configure .
    cmake --build .
    ```
    For more details, please refer to the [library readme](https://github.com/hanstananda/HE_EW_CPP/blob/master/README.md)


3.  Run the python script
    ```
    python run_server.py
    ```

Alternatively, you can just run docker-compose to build this project: 
```bash
docker-compose up 
```

Currently, the server is set up to run at port `7000`.

## APIs 

The current APIs available in this server: 
*   GET `/get_params`
    Used to get the parameters for the PySEAL in json format.
    Example input: 
    ```
    localhost:7000/get_params 
    ``` 
    
    Example output: 
    ```json
    {
        "error_code": 0,
        "error_message": "",
        "result": {
            "coeff_modulus": [
                1152921504606748673,
                1099510890497,
                1099511480321,
                1152921504606830593
            ],
            "coeff_modulus_size": [
                60,
                40,
                40,
                60
            ],
            "plain_modulus": 0,
            "poly_modulus_degree": 8192,
            "scheme": "CKKS"
        },
        "success": true
    }
    ```
    
    
*   GET `/localhost:7000/get_saved_params`
    Used to get the parameters in a binary file that can be loaded into PySEAL. 
    
    Example input: 
    ```
    localhost:7000/get_saved_params 
    ```
        

*   GET `/`
    Used to test whether server is alive. It will return `Hello, World!` if invoked. 

*   GET `/get_model`
    Used to get the base model in `.h5` format. 
    Example input: 
    ```
    localhost:7000/get_model 
    ``` 

*   GET `/get_model_weights`
    Used to get the model weights in json format. 
    Example input: 
    ```
    localhost:7000/model_weights 
    ``` 
    
    Example output: 
    ```json
    {
        "error_code": 0,
        "error_message": "",
        "result": {
            "weights": [weights_1,..., weights_n]
        },
        "success": true
    }
    ```

*   POST `update_model_weights_enc`
    Used to update the model based on the encrypted weights. 
    Example input: 
    ```
    localhost:7000/update_model_weights_enc 
    ``` 
    Request input format: 
    ```json
    {
        "weights": [weights_1,..., weights_n],
        "num_party": n
    }
    ```
    Where 
    *   `weights` denotes the weights of each layer as a list of weights. 
    *   `num_party` denotes the number of workers that are participating in the aggregated value. 