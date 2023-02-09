FROM openeuler/openeuler:22.03-lts
WORKDIR /app
COPY *  /app/
RUN dnf install aops-zeus -y --setopt=reposdir=/app
# ENTRYPOINT ["nohup","python3","/usr/lib/python3.9/site-packages/zeus/manage.py","&"]
CMD ["/bin/bash","/app/start.sh"]