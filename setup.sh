# Build and install netconf base server locally
cd netconf-extended && ./buildinstall.sh --user && cd ..

# Build the publisher docker container
cd publisher && ./build_docker_container.sh