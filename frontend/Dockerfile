#Build VITE Proyect
FROM node:20 as build

WORKDIR /tmp/build

COPY package.json /tmp/package.json
RUN npm install --omit-dev

COPY . . 
RUN npm run build

#Deploy VITE Proyect
FROM nginx

#Support relative routes
RUN echo '\
server {\
    listen       80;\
    server_name  localhost;\
    root   /usr/share/nginx/html;\
    index  index.html;\
    location / {\
        try_files $uri $uri/ /index.html;\
    }\
}' > /etc/nginx/conf.d/default.conf

COPY --from=build /tmp/build/dist /usr/share/nginx/html

COPY app.config.sh /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/app.config.sh 

EXPOSE 80