ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

ifndef APP_PORT
override APP_PORT = 8000
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

APPLICATION_NAME = app

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \


# Commands
env:  ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@cp .env.example .env

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

lint:  ##@Code Check code with ruff
	poetry run ruff check . --fix

format:  ##@Code Reformat code with ruff, isort, black
	poetry run isort .
	poetry run black .
	poetry run ruff check --fix .

db:  ##@Project Run server and database with docker-compose
	docker-compose -f docker-compose.yml up -d --remove-orphans

run:  ##@Application Run application server
	poetry run python -m $(APPLICATION_NAME)

migrate:  ##@Database Do all migrations in database
	alembic upgrade $(args)

revision:  ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
	alembic revision --autogenerate

upgrade:  ##@Database Upgrade database to the latest revision
	alembic upgrade head

open_db:  ##@Database Open database inside docker-image
	docker exec -it db psql -d $(POSTGRES_DB) -U $(POSTGRES_USER)

clean:  ##@Code Clean directory from garbage files
	rm -fr *.egg-info dist

%::
	echo $(MESSAGE)
