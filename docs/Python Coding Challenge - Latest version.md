#

# Python Coding Challenge: Rest API on FastAPI

Implement a Restful API on FastAPI using the following tech stack, including unit tests and **at least one integration test**:

* Python
* FastAPI
* AWS DynamoDB
* AWS API Gateway
* AWS Lambda
* [Serverless Framework](https://www.serverless.com/)

The API should accept the following JSON requests and produce the corresponding HTTP responses:

**Request 1:**
HTTP POST
URL: https://\<api-gateway-url\>/api/books
Body (application/json):
{
  "id": "/books/id1",
  "author": "/authors/id1",
  "name": "Fancy Tech",
  "note": "Awesome book for beginners in Fancy.",
  "serial": "C040102"
}

**Response 1 \- Success:**
HTTP 201 Created

**Response 1 \- Failure 1:**
HTTP 400 Bad Request
If any of the payload fields are missing. Response body should have a descriptive error message for the client to be able to detect the problem.

**Response 1 \- Failure 2:**
HTTP 500 Internal Server Error
If any exceptional situation occurs on the server side.

**Request 2:**
HTTP GET
URL: https://\<api-gateway-url\>/api/books/{id}
Example: GET https://api123.amazonaws.com/api/books/id1

**Response 2 \- Success:**
HTTP 200 OK
Body (application/json):
{
  "id": "/books/id1",
  "author": "/authors/id1",
  "name": "Fancy Tech",
  "note": "Awesome book for beginners in Fancy.",
  "serial": "C040102"
}

**Response 2 \- Failure 1:**
HTTP 404 Not Found
If the request id does not exist.

**Response 1 \- Failure 2:**
HTTP 500 Internal Server Error
If any exceptional situation occurs on the server side.

—---------------------------—---------------------------—---------------------------—---------------------------—---------------------------

Evaluation criteria for the coding challenge is as follows:

* Proper use of Git for source control
* Working solution (not necessarily with best practices but good to have)
* Good unit test coverage
* At least one integration test
* Good code structure and naming
* Basic documentation on how to run and test your code in a README.md file

**Bonus:** API being directly accessible from a web application **running in a browser** (not just using curl or postman)
