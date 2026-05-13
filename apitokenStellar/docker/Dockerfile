FROM python:3.7

WORKDIR /usr/src/app


# Install linux dependencies
RUN apt-get update \
 && apt-get install -y libssl-dev curl

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - &&\
  apt-get install -y nodejs

RUN npm install n -g && npm install -g npm@latest
RUN npm install -g ganache-cli

RUN python3 -m pip install --upgrade pip
RUN pip install packaging==21.3
RUN python3 -m pip install --user pipx
# RUN python3 -m pipx ensurepath

RUN python3 -m pipx install eth-brownie
RUN /root/.local/bin/brownie pm install OpenZeppelin/openzeppelin-contracts@5.2.0


COPY network-config.yaml /root/.brownie/network-config.yaml

# RUN /root/.local/bin/brownie accounts new viverent

# COPY . .

VOLUME /usr/src/app

#ENTRYPOINT ["sh"]

CMD [ "scripts/deploy_Test1_development.sh" ]

