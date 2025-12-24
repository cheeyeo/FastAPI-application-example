### FastAPI project

This repo hosts a FastAPI application that generates random numbers between a min and max value.

It is also an experiment in using OAuth2 for API authentication and authorization via AWS Cognito.

### Run on localhost

Create a AWS Cognito User Pool with an optional PreToken Generation Lambda trigger.

Get the app client ID and secret; user pool ID and region.

Generate a SECRET_KEY value using:
```
openssl rand -hex 32
```

Create .env file with following values:
```
export RDS_USERNAME="xxx"
export RDS_DB_NAME="xxx"
export RDS_PASSWORD="xxx"
export RDS_HOSTNAME="localhost"
export RDS_PORT=5432
export ENV_TYPE="dev"
export SECRET_KEY="XXXXXX"
export AWS_REGION="eu-west-2"
export AWS_COGNITO_APP_CLIENT_ID="XXXXX"
export AWS_COGNITO_APP_CLIENT_SECRET="XXXXX"
export AWS_USER_POOL_ID="XXXX"
```

Run docker-compose with watch enabled:
```
docker compose -f compose.yml up
```

Go to http://localhost:4000/docs to view the Swagger UI



#### Installing ruff

Ref:
https://docs.astral.sh/ruff/tutorial/#rule-selection

```
uv add --dev ruff

uv run ruff check --fix app/

uv run ruff format app/
```

https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile


### Ref

https://realpython.com/fastapi-python-web-apis/


Full app with database:
https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend


### TUTORIAL
- [ ] https://fastapi.tiangolo.com/tutorial/testing
- [x] https://fastapi.tiangolo.com/tutorial/bigger-applications/
- [ ] https://sqlmodel.tiangolo.com/tutorial/fastapi/
- [x] https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- [x] https://fastapi.tiangolo.com/tutorial/security/first-steps/
- [x] https://fastapi.tiangolo.com/tutorial/middleware/
- [x] https://fastapi.tiangolo.com/tutorial/cors/
- [x] https://fastapi.tiangolo.com/tutorial/sql-databases/
- [x] https://fastapi.tiangolo.com/tutorial/background-tasks/
- [x] https://fastapi.tiangolo.com/tutorial/metadata
- [x] https://fastapi.tiangolo.com/tutorial/static-files


### OAUTH2 
- [ ] https://heeki.medium.com/understanding-oauth2-and-implementing-identity-aware-mcp-servers-221a06b1a6cf
- [ ] https://dev.to/composiodev/mcp-oauth-21-a-complete-guide-3g91
- [ ] https://hackernoon.com/oauth-20-for-dummies
- [ ] https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#authentication
- [ ] https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-auth


### ON using alembic to generate migrations

* Run `alembic init alembic`

* To setup autogeneration for models:
  * Comment out `sqlalchemy.url` option in `alembic.ini`
  * In alembic/env.py, update `target_metadata` to point to `SQLModel.metadata`
  * Import the postgresql url and use it in `run_migrations_offline` and `run_migrations_online`

* Run `alembic revision --autogenerate -m "MESSAGE" to detect and create the migrations based on existing model fields....

* Run `alembic upgrade head` to run migrations


### On running tests via pytest

From root folder:


Start the test database passing in the env file

Note: by default compose uses `.env` as the default env file; using a different env filename will not get the new values to be read by the container from compose...
hence need to pass it in cli rather than the compose config file:


```
docker compose --env-file .env.test -f compose.test.yml up
```


In another terminal:
```
uv run -m pytest -p no:cacheprovider -s -v
```