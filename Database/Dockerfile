FROM postgres:latest

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password

COPY init-user.sql /docker-entrypoint-initdb.d/

EXPOSE 5432