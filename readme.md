## MVP Store Order Projects
---
### Use cases
· Baristas can register their coffee shop

· Customers can submit their name, order type and time of arrival to a specific coffee shop

· Baristas can see the orders organized by pickup time for their coffee shop 

### Know issues / To do lists
1. The order API (on get) only return the drinks by latest pickup time, this is due to the old redis API we are user. The latest redis API as the `nx=True` parameter to add new item instead of updating existing one in the sorted set, which will meet this requirement. The signature change of the API causes some issues thus I kept using the old API to get the MVP implemented first
2. With the same reason as #1, I haven't implement the API for users to get all the orders they placed. Also stores can get the order history (total count of each item on menu) once #1 is fixec
3. Data verification is not implemented yet, there's no verification on the payload at the moment, planning to use decorator to valid the payload
4. Unit tests needs to be added

### Data base & Data models
I used redis for this use case for a few reasons
1. It's more flexible for stores to add extra data when they register, e.g: promotions, since there's no schema limitation (structured data
2. It's quick for a PoC purpose without setting up migration scripts for DB / ingest with temp data, since I'm planning to only spend 4 hours on this PoC
3. We can easily implement score board like top selling items, user with most orders without any joins

#### Data models
1. Store order data :
   - Key `stores:order:histories:{store-name}`
   - Type: Sorted set
   - Value: float(pickup_time), order_item 
2. Stores with menus
   - Key `"store:{store_name}`
   - Type: Hashmap
   - Value: same as the payload for store API (register)
3. Stores
   - Key `stores`
   - Type: set
   - Value: non duplicated list of store names


### API Docs
#### Store API 
- /v1/store
   - GET (status 200 on success) :
        Return all the registered stores with their menus
   - POST (status 201 on success):
        Register a store with name and menus
          - Request Payload
          
            ```
            {
                "store_name": "store-a",
                "menus": {
                    "drink1": 7
                }
            }
            ```
#### Order API 
- GET (status 200 on success) : 
        - Parameter: ?store=${store-name}
        Return the orders of the store with pick up time (timestamp)
    
- POST (status 201 on success) :
      Place are store with details, payload see below:
      
        ```json
        {
            "username": "user-a",
            "store_name": "store-a",
            "pickup_time": 1591241347,
            "orders": {
                "drink1": 5,
                "drink2": 2
            }
        }
        ```


### Build and Run
- Docker Compose
  This API is packaged in docker image, to run it, please issue the command below in the project root folder 
  `docker-compose up -d`
  once it's running, you can access the API via your browser / API test tool (postman, etc) by the url 
   - `localhost:5000/v1/store` 
   - `localhost:5000/v1/order`
   - `localhost:5000/v1/health`
  
- Gunicorn:
  If you want to make code changes and run it, you can directly run with command below
  `gunicorn -b 0.0.0.0:5000 app:app`
  
  
### Tests
##### Stores API 
-  register store:
    ```
    curl --location --request POST 'localhost:5000/v1/store' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "store_name": "store-a",
        "menus": {
            "drink1": 7
        }
    }'
    ```

- get list of stores with their menu:
    ```json
    curl --location --request GET 'localhost:5000/v1/store'
    ```
  
  if you follow the steps, you can expect the response like 
    ```json
    [{"menus": "{'drink1': 7}", "store_name": "store-a"}]
    ```
  
##### Orders API
- place order:
    ```json
    curl --location --request POST 'localhost:5000/v1/order' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "username": "user-a",
        "store_name": "store-a",
        "pickup_time": 1591241348,
        "orders": {
            "drink1": 7,
            "drink2": 8
        }
    }'
    ```

- list order (by store):
  ```json
    curl --location --request GET 'localhost:5000/v1/order?store=store-a' 
   ```
  if you follow the steps, you can expect the result 
  ```json
    [
        [
            "drink1",
            1591241348.0
        ],
        [
            "drink2",
            1591241348.0
        ]
    ]
  ```