FROM python:3.11.0-alpine3.17
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache curl=8.5.0-r0 \
    openssl-dev=3.0.12-r4 \
    libffi-dev=3.4.4-r0 \
    jq=1.6-r2 \
    build-base=0.5-r3 \ 
    bash=5.2.15-r0 && \
    addgroup -g 1001 sslcheck && \
    adduser \
    --disabled-password \
    --gecos "" \
    --home "/sslcheck" \
    --ingroup "sslcheck" \
    --uid "1001" \
    "sslcheck"

COPY ./script /sslcheck
RUN chown sslcheck:sslcheck /sslcheck
ENV PATH="${PATH}:/sslcheck/.local/bin"
RUN pip3 install --no-cache-dir -r /sslcheck/requirements.txt
USER sslcheck
WORKDIR /sslcheck
CMD ["/sslcheck/check_ssl.sh"]
