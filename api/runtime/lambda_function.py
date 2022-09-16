# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Any, Dict, Optional

from aws_lambda_powertools.event_handler import api_gateway
from aws_lambda_powertools.event_handler import exceptions

import helpers  # isort: skip

app = api_gateway.ApiGatewayResolver(
    proxy_type=api_gateway.ProxyEventType.APIGatewayProxyEventV2
)


def lambda_handler(event: Dict[str, Any], context: object) -> Dict[str, Any]:
    return app.resolve(event, context)


@app.post("/users")  # type: ignore
def create_user() -> Dict[str, Any]:
    user_attributes = app.current_event.json_body
    username = user_attributes["username"]
    del user_attributes["username"]
    users_repository = helpers.init_users_repository()
    user = users_repository.get_user(username)
    if user is not None:
        raise exceptions.BadRequestError(f"User {username} already exists")
    created_user: Dict[str, Any] = users_repository.create_user(
        username, user_attributes
    )
    return created_user


@app.put("/users/<username>")  # type: ignore
def update_user(username: str) -> Dict[str, Any]:
    user_attributes = app.current_event.json_body
    users_repository = helpers.init_users_repository()
    user = users_repository.get_user(username)
    if user is None:
        raise exceptions.NotFoundError(f"User {username} does not exist")
    updated_user: Dict[str, Any] = users_repository.update_user(
        username, user_attributes
    )
    return updated_user


@app.get("/users/<username>")  # type: ignore
def get_user(username: str) -> Dict[str, Any]:
    users_repository = helpers.init_users_repository()
    user: Optional[Dict[str, Any]] = users_repository.get_user(username)
    if user is None:
        raise exceptions.NotFoundError(f"User {username} does not exist")
    return user


@app.delete("/users/<username>")  # type: ignore
def delete_user(username: str) -> Dict[str, Any]:
    users_repository = helpers.init_users_repository()
    user = users_repository.get_user(username)
    if user is None:
        raise exceptions.NotFoundError(f"User {username} does not exist")
    users_repository.delete_user(username)
    return {"message": f"User {username} was deleted"}
