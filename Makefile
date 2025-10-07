install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt || true
	pip install -r requirements.txt

enrich:
	python scripts/ai_enrich.py

tts:
	python scripts/tts.py

deck:
	python scripts/build_deck.py

all: enrich tts deck
