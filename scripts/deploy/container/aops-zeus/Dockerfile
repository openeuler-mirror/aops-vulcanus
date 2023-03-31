FROM openeuler/openeuler:22.03-lts-sp1
WORKDIR /app
COPY *  /app/
RUN dnf install aops-zeus -y --setopt=reposdir=/app
CMD ["/bin/bash","/app/start.sh"]