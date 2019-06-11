all:

build: clean
	python3 setup.py sdist --formats=gztar,zip bdist_wheel

upload: build
	twine upload dist/*

clean:
	rm -rf build/ dist/ *.egg-info/
