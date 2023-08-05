all: clean
	SKIP_WRITE_GIT_CHANGELOG=1 SKIP_GENERATE_AUTHORS=1 python3 ./setup.py sdist bdist_wheel
	pip3 install --upgrade dist/*.whl --user -v

clean:
	rm dist build *.egg-info -rf

upload:
	twine upload dist/*
