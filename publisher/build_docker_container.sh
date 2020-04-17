# Build the wheel locally from source
cd ../netconf-extended/  

wheel=$(python3 setup.py sdist bdist_wheel 2> /dev/null | grep "whl" | cut -d " " -f 2 | cut -c 2- | rev | cut -c 2- | rev) 
echo $wheel
cd ~-
# Get move the wheel to current directory
cp $wheel .

# Build the container
sudo docker build -t publisher .

# Remove the wheel
rm -f *.whl
