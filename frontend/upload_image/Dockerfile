# React 개발 서버를 실행하는 Dockerfile
FROM node:16

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .

EXPOSE 3000

# React 개발 서버 실행
CMD ["npm", "start"]
