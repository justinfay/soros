.PHONY: test
test:
	export PYTHONPATH=.:$$PYTHONPATH; py.test test/ -v --capture=no
