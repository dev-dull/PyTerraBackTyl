FROM ubuntu
ENV PTBT_WORKDIR="/opt/pyterrabacktyl"
ENV PTBT_DATADIR="${PTBT_WORKDIR}/data"

RUN set -ex \
    && apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install -y python3 python3-pip python3-setuptools python3-venv net-tools openssh-client sudo git \
    && apt-get autoremove --purge -y

RUN set -ex\
    && python3 -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir "pyyaml<=5.3" jsonpath flask GitPython

COPY . "${PTBT_WORKDIR}"
RUN mkdir "${PTBT_DATADIR}"

EXPOSE 2442
WORKDIR "${PTBT_WORKDIR}"
CMD ["./ds.sh"]
