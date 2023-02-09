FROM openeuler/openeuler:22.03-lts as OS
COPY . /app
WORKDIR /app
RUN dnf install aops-hermes -y --setopt=reposdir=/app

FROM nginx:1.20.0
COPY --from=OS /opt/aops/web/dist /app
WORKDIR /app
RUN chmod -R 755 /app
COPY --from=OS /app/default.conf /etc/nginx/conf.d/
ENV RUN_USER nginx
ENV RUN_GROUP nginx
EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]
