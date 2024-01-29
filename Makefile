install:
	python3 -m venv .venv
	. .venv/bin/activate && \
	python3 -m pip install -r requirements.txt

run:
	. .venv/bin/activate && \
	export PYTHONPATH=${PWD} && \
	uvicorn app.main:app --reload

debug:
	export DEBUG=True && \
	$(MAKE) run

test:
	. .venv/bin/activate && \
	export PYTHONPATH=${PWD} && \
	pytest . -v

clean-all:
	rm -rf .venv
	rm -rf .pytest_cache
