.PHONY: clean build-linux build-deb all

all: clean build-linux build-deb

clean:
	sudo rm -rf build dist

build-linux:
	python3 -m PyInstaller --clean -y fzbgptools.spec

build-deb:
	./build_deb.sh
