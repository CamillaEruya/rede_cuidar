FROM mariadb:11.4
COPY database-entrypoint.sh /opt/rede-cuidar/database-entrypoint.sh
RUN sed -i 's/\r$//' /opt/rede-cuidar/database-entrypoint.sh \
    && chmod 755 /opt/rede-cuidar/database-entrypoint.sh
