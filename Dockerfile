FROM python:3.5-onbuild

RUN python /usr/src/app/manage.py collectstatic

CMD ["/usr/src/app/docker-entrypoint.sh"]
