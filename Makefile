module.tar.gz: module.py pyproject.toml uv.lock run.sh meta.json
	rm -f $@
	tar czf $@ $^

lint:
	ruff check module.py
