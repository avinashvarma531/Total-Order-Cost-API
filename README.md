<h1 style="text-align: center">Django API for calculating Total Order Price</h1>

This django project provides an API service to calculate the total order price for the list of items purchased, including offer(if any). The input to the API should be sent as a **JSON** payload in the body of a **POST** request to '/' URL (home page). The total order cost is then sent back in JSON format.

<br/>

## **Installation**

1. Clone this Git repo using Git CLI / directly download as a zip file and extract the **Total-Order-Cost-API** folder.

    ```shell
    $ git clone https://github.com/avinashvarma531/Total-Order-Cost-API
    ```

2. The project is built using Django framework. So, ensure you have installed the Django 3.2.5. if not, run the following command in the command prompt or terminal.

    ```shell
    $ pip install django==3.2.5
    ```

<br/>

## **Technical Decisions made**

1. **The API only supports GET and POST requests on the '/' end point.**
    
    1. The GET request to the server returns HTML page containing a form which when submitted initiates a POST request to the server.
    2. The body of the POST request is of **form-data** type having **JSON** file attached under **'payload'** key.
    3. In general, POST method is used to create a resource. The reason for choosing POST instead of GET is that though it is possible for GET request to have a body, it is not a standard to have body attached to GET method because GET method is memory limited while POST is not.

2. **CSRF Token Authentication is included.**
    
    1. For the security reason, that a browser can be tricked to send re-submission request without user's consent, the csrf token is included in the form which is submitted to the server.
    2. The token is explicitly appended in the HTML form. So, when requesting the API through *curl* or *Postman* include the CSRF token from cookies into header with key as 'X-CSRFToken'.

3. **So many *'assert'* statements.**
    
    1. The *get_price* view of the *Main* app in the project contains many assert statements which clutters the actual code.
    2. But, these asserts were implemented for detailed description of the error(if occurred).
    3. They can be removed and a common error message
    can be returned in case of any exception.

4. **HTTP 400 is the most used client error**
    
    1. Because it is the most common mistake that a potential user can make.
    2. Other supported HTTP errors that the server could return are 500 and 501.

5. **Hash table is used to represent the *DELIVERY_COST_SLAB* in Main.views.**
    
    1. The key represents a tuple with a range of 10kms.
    2. The value represents cost in paisa for the distance belonging to a particular range.
    3. It takes O(n) time, where 'n' is the number of slabs in the hash table, to search for valid cost for the delivery distance.

<br/>

## **Execution**
1. Using command prompt or terminal, *cd* into the ***Total-Order-Cost-API*** project folder cloned above.
    
    ```shell
    $ cd [PATH TO 'Total-Order-Cost-API' folder]
    ```

2. Start the Django server on localhost:8000.
   
   ```shell
    $ python manage.py runserver
    ```

3. The GET request to the server will render a HTML form where we can upload the JSON file which contains order details.

4. Open the https://localhost:8000/ link in the browser and upload the json file containing order details.

5. The server will respond with appropriate data.
