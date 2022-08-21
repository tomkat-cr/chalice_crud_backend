# Chalice CRUD Backend

Serverless CRUD Backend based on the AWS Chalice framework, AWS DynamDb database, and Auth0 for API security.

AWS Chalice is a serverless Python framework developed by Amazon.
It shares so many similarities in syntax and semantics with Flask.
Like other serverless technology, Chalice allows the developer to be able to concentrate on application development without having to deal with managing servers.
It uses AWS Lambda and the Amazon API Gateway.

## INSTRUCTIONS

## Prepare the environment

### 1. Configure AWS Credentials

You need to set up your AWS credentials on the AWS CLI. This will allow you to use the Amazon API Gateway and AWS Lambda.
If you installed AWS CLI successfully, then you can use the command below to configure your AWS credentials:

`aws configure`

You should get a prompt for the AWS Access Key ID, AWS Secret Access Key, and default region name. Supply your AWS Access keys and a chosen region. You can use any available AWS region. Finally, you can skip the default output format to use the default option: None:

```
AWS Access Key ID [None]: ****************ABCD
AWS Secret Access Key [None]: ****************abCd
Default region name [None]: us-east-1
Default output format [None]:
```

If you don't have AWS credentials yet, you will need to set up an IAM user in the IAM Console. Visit Creating IAM users for a guide on how to create IAM Users. Once you have created the IAM user, you can then go through the instructions for setting up the AWS Access keys.

To check whether you set up your credentials correctly, run the following command:

`aws ec2 describe-regions`

You should see the list of all regions where EC2 is available.

### 2. Install Project Dependencies

Use the following commands to activate the Python virtual environment and install the requirements:

`python3 -m venv env`

`source env/bin/activate`

`pip install -r requirements.txt`

### 3. Database Configuration and Deployment Setup

There are 2 files inside the `chalice-api/.chalice` directory:

- `dynamodb_cf_template.yaml`: It's the template that CloudFormation will use to create the database. CloudFormation is a tool for specifying the resources and dependencies for your AWS project. It also helps you set them up. The CloudFormation template, in a JSON or YAML format, contains resources that make up your stack. CloudFormation uses that template to set up and configure the resources specified in it.

- `policy-dev.json`: contains the policy for reading and writing from the DynamoDB database. In that file there's the provision for your user to create log groups and log events, DynamoDB actions for reading, creating, updating, scanning, and query operations on database items, and assigning the DynamoDB table name as `my-demo-table`.

To create the stack `my-stack` on Cloudformation and the DynamoDB database, use the following command:

`aws cloudformation deploy --template-file chalice-api/.chalice/dynamodb_cf_template.yaml --stack-name "my-stack"`

### 4. Run the local server

Now, you may run and test the setup on the localhost. Run the commands below:

`cd chalice-api`

`chalice local`

You should get a terminal output as follows:

```
Serving on http://127.0.0.1:8000
Found credentials in shared credentials file: ~/.aws/credentials
```

### 5. Test the CRUD Features

There are some pre-configured tests for [Postman](https://www.postman.com/downloads/) in the file `Chalice-CRUD-Practice.postman_collection.json` you can use to test the API.

### 6. Deploy to AWS

Before you deploy your code to AWS, make sure you have the necessary permissions set for your IAM account as defined in the AWS user guide. Now, with a single command `chalice deploy`, you can deploy your Chalice application to AWS.

`chalice deploy`

You should get the API URL endpoint and a Lambda ARN on your terminal, which you can use to interact with the API.

```
Creating deployment package.
Creating IAM role: chalice-api-dev-api_handler
Creating lambda function: chalice-api-dev
Creating Rest API
Resources deployed:
    - Lambda ARN: arn:aws:lambda:us-west-2:xxxxxxxxxxxx:function:chalice-api-dev
    - Rest API URL: https://dv2zde7gnj.execute-api.us-west-2.amazonaws.com/api/
```

Now, If you look at the folder structure, you will notice a few new, automatically generated files to accommodate the deployment changes under the `.chalice` sub-folder:

```
chalice-api
├── app.py
├── .chalice
|   ├── deployed
|   ├── deployments
│   └── config.json
├── .gitignore
└── requirements.txt
```

### 7. Testing the Deployed Chalice API

Now, you can test the REST API URL generated by Chalice:

http GET https://dv2zde7gnj.execute-api.us-west-2.amazonaws.com/api/

The output would look like the following:

```
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 73
Content-Type: application/json
Date: Sun, 02 May 2021 00:32:35 GMT
Via: 1.1 xxxxxxxxxx.cloudfront.net (CloudFront)
X-Amz-Cf-Id: xxxxxxxxxxxxxxxx==
X-Amz-Cf-Pop: AMS1-C1
X-Amzn-Trace-Id: Root=1-xxxxxxxxx-xxxxxxxxxxxxxx;Sampled=0
X-Cache: Miss from cloudfront
x-amz-apigw-id: xxxxxxxxxxxxxx=
x-amzn-RequestId: xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxx

{
    "data": [
        {
            "author": "Carlos J. Ramirez",
            "id": "123",
            "title": "Chalice Book"
        }
    ]
}
```

Congratulations! You have built and tested your REST API with AWS Chalice.

### 8. Adding authentication | Auth0

You could add authentication and authorization features to your application by enabling Auth0 in the API.
Auth0 enables you to authenticate your users. It also enables you to provide authorized access to the endpoints in your REST APIs.
To use Auth0 authentication, you need an Auth0 account. If you don't have an account yet, you can sign up for a free Auth0 account [here](https://auth0.com/signup).

After signing up or signing in, go to your dashboard and locate the Accounts tab.<br>
Select Create Application. Supply a name for your app and select Regular Web Applications.<br>
After creating the app, navigate to the Settings tab to see the parameters needed to connect your Chalice API application with Auth0.

To enable Auth0 in the API, create a `.env` file by copying the `.env.example` file and add the values for the Auth0 parameters:

`cp .env.example .env`

```
# .env

AUTH0_ENABLED=1

AUTH0_MAPI_CLIENT_ID=XXXXXX
AUTH0_MAPI_CLIENT_SECRET=XXXXXX
AUTH0_MAPI_API_TOKEN=XXXXXX

AUTH0_CLIENT_ID=XXXXXX
AUTH0_CLIENT_SECRET=XXXXXX
AUTH0_DOMAIN=XXX

AUTH0_API_AUDIENCE=https://XXXXXX/
AUTH0_ALGORITHMS=RS256
```

To set the AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET environment variables in the `.env` file:

* Go to the Auth0 dashboard, then go to option `Applications > Applications` and click on your App.
Copy the values for `Domain`, `Client ID`, and `Client Secret` and paste them into the corresponding variables.

To get valid tokens, the AUTH0_MAPI_CLIENT_ID and AUTH0_MAPI_CLIENT_SECRET, and AUTH0_MAPI_API_TOKEN environment variables must be set.

- Go to the Auth0 dashboard, then go to option `Applications > API > Auth0 Management API > Test`. Copy the `client_id` and `client_secret` parameter values on the API calls and paste them into the corresponding `AUTH0_MAPI_*` variables.

- Go to the Auth0 dashboard, then go to option `Applications > API > Auth0 Management API > API Explorer`. Enable the option and copy the `Token` parameter value and paste it in the `AUTH0_MAPI_CLIENT_SECRET` variable.

Now, all the calls to the API must include an `Authorization` header of type `Bearer Token` with an Auth0 valid token.

Therefore, if a user is not signed in, Auth0 cannot have Access tokens that enable Auth0 to verify the user. So, they can't use those endpoints protected by the @requires_auth decorator.

To get a valid token, make a call to `http://127.0.0.1/login` endpoint on your Chalice app.

It will return something like this:

```
{
    "access_token": "eyJhbGciOiJ...",
    "scope": "read:client_grants create:client_grants...",
    "expires_in": 86400,
    "token_type": "Bearer"
}
```

Copy the value of the `access_token` element and paste it into the Authorization header token on all the API calls.

### 9. Cleaning up the AWS resources created

If you would like to delete your application, you can use the following command:

`chalice delete`

Don't forget to delete the DynamoDB table that you created too:

`aws cloudformation delete-stack --stack-name my-stack`
