### FastAPI project

### Ref

https://realpython.com/fastapi-python-web-apis/


Full app with database:
https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend


### TUTORIAL
- [x] https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- [x] https://fastapi.tiangolo.com/tutorial/security/first-steps/
- [x] https://fastapi.tiangolo.com/tutorial/middleware/
- [x] https://fastapi.tiangolo.com/tutorial/cors/
- [x] https://fastapi.tiangolo.com/tutorial/sql-databases/
- [ ] https://fastapi.tiangolo.com/tutorial/bigger-applications/#an-example-file-structure
- [ ] https://sqlmodel.tiangolo.com/tutorial/fastapi/


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
  * import the postgresql url and use it in `run_migrations_offline` and `run_migrations_online`

* Run `alembic revision --autogenerate -m "MESSAGE" to detect and create the migrations based on existing model fields....

* Run `alembic upgrade head` to run migrations


#### RUN LOCALY

Create .env file with following values:
```
export RDS_USERNAME="xxx"
export RDS_DB_NAME="xxx"
export RDS_PASSWORD="xxx"
export RDS_HOSTNAME="localhost"
export RDS_PORT=5432
export ENV_TYPE="dev"
```

```
docker compose -f compose.yml up
```

#### Installing ruff

Ref:
https://docs.astral.sh/ruff/tutorial/#rule-selection

```
uv add --dev ruff

uv run ruff check --fix app/

uv run ruff format app/
```

https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile