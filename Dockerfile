FROM python:3-slim
ENV PTBT_WORKDIR="/opt/pyterrabacktyl"
ENV PTBT_DATADIR="${PTBT_WORKDIR}/data"
ENV PTBT_USER="tfbackendsvc"
COPY . "${PTBT_WORKDIR}"
RUN mkdir "${PTBT_DATADIR}"

RUN adduser "${PTBT_USER}" --system --home /home/${PTBT_USER}
RUN chown -Rh $PTBT_USER: "${PTBT_WORKDIR}"
RUN chown -Rh $PTBT_USER: "${PTBT_DATADIR}"
USER "${PTBT_USER}"
RUN pip3 install pyyaml jsonpath flask GitPython --user
EXPOSE 2442
WORKDIR "${PTBT_WORKDIR}"
CMD ["./ds.sh"]
