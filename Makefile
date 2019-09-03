all:

build: clean
	python3 setup.py sdist --formats=zip bdist_wheel

upload: build
	twine upload dist/*

install: build
	python3 setup.py install

clean:
	rm -rf build/ dist/ *.egg-info/
