FROM ubuntu
ENV PTBT_WORKDIR="/opt/pyterrabacktyl"
ENV PTBT_DATADIR="${PTBT_WORKDIR}/data"
ENV PTBT_USER="tfbackendsvc"
COPY . "${PTBT_WORKDIR}"
RUN mkdir "${PTBT_DATADIR}"

# Patch for Git CVE - remove when git version >= 2.39
RUN apt-get update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:git-core/ppa -y

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install python3 python3-pip python3-setuptools net-tools openssh-client sudo git -y
RUN apt-get autoremove --purge -y
RUN adduser "${PTBT_USER}" --system
RUN chown -Rh $PTBT_USER: "${PTBT_WORKDIR}"
RUN chown -Rh $PTBT_USER: "${PTBT_DATADIR}"
RUN echo "${PTBT_USER} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER "${PTBT_USER}"
RUN pip3 install pyyaml jsonpath flask GitPython --user
EXPOSE 2442
WORKDIR "${PTBT_WORKDIR}"
CMD ["./ds.sh"]
