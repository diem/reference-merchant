FROM node:12.16.2-alpine3.11

WORKDIR /app
RUN npm install -g react-scripts --silent

COPY package.json yarn.lock tsconfig.json /app/
RUN yarn install

COPY public ./public
COPY src ./src

#RUN CI=true yarn test
RUN yarn build

ENTRYPOINT yarn start
