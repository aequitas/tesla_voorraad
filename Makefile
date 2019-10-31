host = hydra.

venv ?= ~/Library/Caches/virtualenvs/$(shell basename $$PWD)
python = ${venv}/bin/python3
pip = ${venv}/bin/pip
black = ${venv}/bin/black

run: | ${venv}/.setup
	${python} tesla.py

${venv}/.setup:
	python3 -mvenv ${venv}
	${pip} install -r requirements.txt
	@touch $@

lint: | ${venv}/.setup
	${black} *.py

build:
	env DOCKER_HOST=tcp://${host} docker build -t tesla_voorraad .

deploy:
	env DOCKER_HOST=tcp://${host} docker rm -f tesla_voorraad
	env DOCKER_HOST=tcp://${host} docker run -d --name tesla_voorraad -p 1337:8000 tesla_voorraad

mrproper:
	rm -rf ${venv}
