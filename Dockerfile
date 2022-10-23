FROM ubuntu:18.04 as refal_host

RUN apt-get update
RUN apt-get install -y git dos2unix curl unzip sed g++

# fetch refal-5-lambda
WORKDIR /usr/src
RUN git clone https://github.com/bmstu-iu9/simple-refal-distrib.git

# install refal-5-lambda
WORKDIR /usr/src/simple-refal-distrib
RUN ./bootstrap.sh

ENV PATH="/usr/src/simple-refal-distrib/bin:${PATH}"
ENV RL_MODULE_PATH="/usr/src/simple-refal-distrib/lib:$RL_MODULE_PATH"

COPY . /app
WORKDIR /app

# install python3 and requared properties
RUN apt-get update && apt-get install -y \
 software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
 python3.7 \
 python3-pip
RUN python3.7 -m pip install pip
RUN apt-get update && apt-get install -y \
 python3-distutils \
 python3-setuptools
RUN python3.7 -m pip install networkx

RUN rlc test_count.ref
RUN rlc test_gen.ref
RUN rlc total_count.ref
RUN rlc test_check_log.ref

RUN dos2unix run_test.sh
RUN chmod +x run_test.sh
ENTRYPOINT ["./run_test.sh"]
