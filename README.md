### FastAPI project

Ref:

https://realpython.com/fastapi-python-web-apis/

Using databases with fastapi:
https://fastapi.tiangolo.com/tutorial/sql-databases

Full app with database:
https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend


https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/#the-heropublic-data-model



### ON using alembic to generate migrations
* Run `alembic init alembic`
* To setup autogeneration for models:
  * Comment out `sqlalchemy.url` option in `alembic.ini`
  * In alembic/env.py, update `target_metadata` to point to `SQLModel.metadata`
  * import the postgresql url and use it in `run_migrations_offline` and `run_migrations_online`

* Run `alembic revision --autogenerate -m "MESSAGE" to detect and create the migrations based on existing model fields....

* Run `alembic upgrade head` to run migrations


#### RUN LOCALY

```
docker compose -f compose.yml up
```

#### Installing ruff

Ref:
https://docs.astral.sh/ruff/tutorial/#rule-selection

```
uv add --dev ruff


```