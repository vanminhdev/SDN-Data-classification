docker build -t my-ubuntu-image -f ./controllers/Dockerfile .
docker run -it --rm --name my-ubuntu -p 80:80 my-ubuntu-image