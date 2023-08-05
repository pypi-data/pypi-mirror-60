FROM python:3.8.1-alpine

COPY dist/*.whl /

# hadolint ignore=DL3013
RUN pip --no-cache-dir install /*.whl

ENTRYPOINT ["tuxbuild"]
