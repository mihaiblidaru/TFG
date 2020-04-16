rm -rf ./netconf-extended/ 
cp -r ../netconf-extended/ ./netconf-extended/
docker build -t publisher .
rm -rf ./netconf-extended/ 