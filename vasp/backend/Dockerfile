FROM python:3.7-slim as backend-base

WORKDIR /vasp-backend

RUN apt-get update && apt-get install -y gcc git netcat
RUN pip install pipenv

#-------------------------------------------------------------------
FROM node:12.16.2-alpine3.11 as frontend-builder

WORKDIR /frontend
RUN npm install -g react-scripts --silent

COPY vasp/backend/pay_with_diem/package.json ./
COPY vasp/backend/pay_with_diem/yarn.lock ./
COPY vasp/backend/pay_with_diem/tsconfig.json ./
RUN yarn install

COPY vasp/backend/pay_with_diem/public ./public
COPY vasp/backend/pay_with_diem/src ./src

ARG REACT_APP_BACKEND_URL
RUN echo "REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL"
RUN yarn build

#-------------------------------------------------------------------
FROM backend-base

RUN mkdir pay_with_diem
COPY --from=frontend-builder /frontend/build ./pay_with_diem/build
COPY thirdparty/ /thirdparty/
COPY vasp/backend/ ./
RUN pipenv install --deploy --system


