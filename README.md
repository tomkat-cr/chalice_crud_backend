# soa_crud_backend
Serverless CRUD Backend based on the AWS Chalice framework, DynamDb, Auth0, and SOA architecture

## INSTRUCTIONS

## Prepare the environment

### 1. Configure AWS Credentials

You need to set up your AWS credentials on the AWS CLI. This will allow you to use the Amazon API Gateway and AWS Lambda.
If you installed AWS CLI successfully, then you can use the command below to configure your AWS credentials:

`aws configure`

You should get a prompt for the AWS Access Key ID, AWS Secret Access Key, and default region name. Supply your AWS Access keys and a chosen region. You can use any available AWS region. Finally, you can skip the default output format to use the default option: None:

AWS Access Key ID [None]: ****************ABCD<br/>
AWS Secret Access Key [None]: ****************abCd<br/>
Default region name [None]: us-east-1<br/>
Default output format [None]:<br/>

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

    Serving on http://127.0.0.1:8000
    Found credentials in shared credentials file: ~/.aws/credentials

### 5. Test the CRUD Features

There are some pre-configured tests for [Postman](https://www.postman.com/downloads/) in the file `Chalice-CRUD-Practice.postman_collection.json` you can use to test the API.

### 6. Adding authentication | Auth0

You could add authentication and authorization features to your application by enabling Auth0 in the API.
Auth0 enables you to authenticate your users. It also enables you to provide authorized access to the endpoints in your REST APIs.
To use Auth0 authentication, you need an Auth0 account. If you don't have an account yet, you can sign up for a free Auth0 account [here](https://auth0.com/signup).

After signing up or signing in, go to your dashboard and locate the Accounts tab.<br>
Select Create Application. Supply a name for your app and select Regular Web Applications.<br>
After creating the app, navigate to the Settings tab to see the parameters needed to connect your Chalice API application with Auth0.

To enable Auth0 in the API, create a `.env` file by copying the `.env.example` file and add the values for the Auth0 parameters:

`cp .env.example .env`

AUTH0_CLIENT_ID=XXXXX<br/>
AUTH0_CLIENT_SECRET=XXXXX<br/>
AUTH0_DOMAIN=XXX<br/>

Now all the calls to the API must include an Authorization header of type `Bearer Token` with an Auth0 valid token.

To get a token example, go to the Auth0 dashboard, then go to option `Applications > API > Auth0 Management API > Test`.<br>
In the Response section, copy the value on `access_token` and paste it into the Bearer's token.

Therefore, if a user is not signed in, Auth0 cannot have Access tokens that enable Auth0 to verify the user. So, they can't use those endpoints protected by the @requires_auth decorator.

### 7. Cleaning up the AWS resources created

If you would like to delete your application, you can use the following command:

`chalice delete`

Don't forget to delete the DynamoDB table that you created too:

`aws cloudformation delete-stack --stack-name my-stack`
