all-tests: check tests

check:
	python3 -m unittest -v test_fork.py

tests:
	python3 -m unittest -v functional-tests/test_clonemachine.py

clean:
	rm -rf functional-tests/tmp
