# Build the wheel locally from source
cd ../netconf-extended/ && python3 setup.py sdist bdist_wheel && cd ~-

# Get move the wheel to current directory
cp ../netconf-extended/dist/*py3*.whl .

# Build the container
docker build -t publisher .

# Remove the wheel
rm -f *.whl