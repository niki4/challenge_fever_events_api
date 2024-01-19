install:
	python3 -m venv .venv
	. .venv/bin/activate && \
	python3 -m pip install -r requirements.txt

run:
	. .venv/bin/activate && \
	export PYTHONPATH=${PWD} && \
	uvicorn app.main:app --reload

clean-all:
	rm -rf .venv
