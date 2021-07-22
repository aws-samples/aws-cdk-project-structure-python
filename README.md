# Recommended AWS CDK project structure for Python applications
The project implements a *user management backend* component that uses 
Amazon API Gateway, AWS Lambda and Amazon DynamoDB to provide basic CRUD operations 
for managing users. The project also includes a continuous deployment pipeline.

![diagram](https://user-images.githubusercontent.com/4362270/128627707-fe646837-7c5d-403e-828e-33142383d121.png)
\* Diagram generated using https://github.com/pistazie/cdk-dia

## Create a new repository from aws-cdk-project-structure-python
This project is a template. Click “Use this template” (see the screenshot below) in 
the repository [main page](https://github.com/aws-samples/aws-cdk-project-structure-python)
to create your own repository based on aws-samples/aws-cdk-project-structure-python. 
This is optional for deploying the component to the development environment, but 
**required** for deploying the pipeline.

![template](https://user-images.githubusercontent.com/4362270/128629234-31cd275e-6a3f-4a6a-9010-028a0a279950.png)

The instructions below use the aws-cdk-project-structure-python repository.

## Create development environment
See [Getting Started With the AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
for additional details and prerequisites

### Clone the code
```bash
git clone https://github.com/aws-samples/aws-cdk-project-structure-python
cd aws-cdk-project-structure-python
```

### Create Python virtual environment and install the dependencies
```bash
python3.7 -m venv .venv
source .venv/bin/activate
# [Optional] Needed to upgrade dependencies and cleanup unused packages
pip install pip-tools==6.1.0
./scripts/install-deps.sh
./scripts/run-tests.sh
```

### [Optional] Upgrade AWS CDK Toolkit version
**Note:** If you are planning to upgrade dependencies, first push the upgraded AWS CDK Toolkit version.
See [(pipelines): Fail synth if pinned CDK CLI version is older than CDK library version](https://github.com/aws/aws-cdk/issues/15519) 
for more details.

```bash
vi package.json  # Update "aws-cdk" package version
./scripts/install-deps.sh
./scripts/run-tests.sh
```

### [Optional] Upgrade dependencies (ordered by constraints)
Consider [AWS CDK Toolkit (CLI)](https://docs.aws.amazon.com/cdk/latest/guide/reference.html#versioning) compatibility 
when upgrading AWS CDK packages version.

```bash
pip-compile --upgrade api/runtime/requirements.in
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
./scripts/install-deps.sh
# [Optional] Cleanup unused packages
pip-sync api/runtime/requirements.txt requirements.txt requirements-dev.txt
./scripts/run-tests.sh
```

## Deploy the component to development environment
The `UserManagementBackend-Dev` stage uses your default AWS account and region.
It consists of two stacks - stateful (database) and stateless (API and monitoring) 

```bash
npx cdk deploy "UserManagementBackend-Dev/*"
```

Example outputs for `npx cdk deploy "UserManagementBackend-Dev/*"`:
```text
 ✅  UserManagementBackendDevStateful7B33C11B (UserManagementBackend-Dev-Stateful)

Outputs:
UserManagementBackendDevStateful7B33C11B.ExportsOutputFnGetAttDatabaseTableF104A135ArnDAC15A6A = arn:aws:dynamodb:eu-west-1:111111111111:table/UserManagementBackend-Dev-Stateful-DatabaseTableF104A135-1LVXRPCPOKVZQ
UserManagementBackendDevStateful7B33C11B.ExportsOutputRefDatabaseTableF104A1356B7D7D8A = UserManagementBackend-Dev-Stateful-DatabaseTableF104A135-1LVXRPCPOKVZQ
```
```text
 ✅  UserManagementBackendDevStateless0E5B7E4B (UserManagementBackend-Dev-Stateless)

Outputs:
UserManagementBackendDevStateless0E5B7E4B.APIHandlerArn = arn:aws:lambda:eu-west-1:111111111111:function:UserManagementBackend-Dev-Stateless-APIHandler-PJjw0Jn7Waq0
UserManagementBackendDevStateless0E5B7E4B.APIHandlerName = UserManagementBackend-Dev-Stateless-APIHandler-PJjw0Jn7Waq0
UserManagementBackendDevStateless0E5B7E4B.EndpointURL = https://zx5s6bum21.execute-api.eu-west-1.amazonaws.com/v1/
UserManagementBackendDevStateless0E5B7E4B.RestAPIId = zx5s6bum21
```

## Deploy the pipeline
**Prerequisites**
- Create a new repository from aws-cdk-project-structure-python, if you haven't done 
  this already. See [Create a new repository from aws-cdk-project-structure-python](README.md#create-a-new-repository-from-aws-cdk-project-structure-python)
  for instructions
- Create AWS CodeStar Connections [connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html)
  for the pipeline
- Update the values in [constants.py](constants.py)
- Commit and push the changes: `git commit -a -m 'Update constants' && git push`

```bash
npx cdk deploy UserManagementBackend-Pipeline
```

## Delete all stacks
**Do not forget to delete the stacks to avoid unexpected charges**
```bash
npx cdk destroy "UserManagementBackend-Dev/*"
npx cdk destroy UserManagementBackend-Pipeline
npx cdk destroy "UserManagementBackend-Pipeline/UserManagementBackend-Prod/*"
```

Delete the AWS CodeStar Connections connection if it is no longer needed. Follow the instructions
in [Delete a connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-delete.html).

## Testing the web API
Below are examples that show the available resources and how to use them:

```bash
endpoint_url=$(aws cloudformation describe-stacks \
  --stack-name UserManagementBackend-Dev-Stateless \
  --query 'Stacks[*].Outputs[?OutputKey==`EndpointURL`].OutputValue' \
  --output text)

curl \
    -H "Content-Type: application/json" \
    -X POST \
    -d '{"username":"john", "email":"john@example.com"}' \
    "${endpoint_url}/users"

curl \
    -H "Content-Type: application/json" \
    -X GET \
    "${endpoint_url}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X PUT \
    -d '{"country":"US", "state":"WA"}' \
    "${endpoint_url}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X DELETE \
    "${endpoint_url}/users/john"
```

# Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

# License

This code is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
