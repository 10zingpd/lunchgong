module.tar.gz: module.py pyproject.toml uv.lock run.sh
	rm -f $@
	tar czf $@ $^

lint:
	ruff check module.py
