# Use the official Ubuntu image as the base
FROM ubuntu:20.04
USER root
# Update the package lists and install curl
RUN apt-get update && \
    apt-get install -y curl net-tools iputils-ping

# Command to run when the container starts
CMD ["tail", "-f", "/dev/null"]