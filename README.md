# [SnapShot Exchange](https://snapshotexchange.onrender.com/) <span><img align="right" width="32px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"/><span> </span><img align="right" width="32px" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg"/></span>

The project is available online at [https://snapshotexchange.onrender.com/views/dashboard](https://snapshotexchange.onrender.com/views/dashboard)

<img src="./images/QR.png" alt="drawing" width="100"/>



![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)


## Table of contents

  * [Using Technologies](#using-technologies)
  * [Description](#description)
  * [Project Installation](#project-installation)
    + [Local Installation](#local-installation)
    + [DockerHub](#dockerhub)
  * [Implementation](#implementation)
    + [API routes](#api-routes)
    + [Server side rendering](#server-side-rendering)
    + [Chat](#chat)
  * [Information for Developers](#information-for-developers)
  * [License](#license)
    + [MIT License](#mit-license)

## Using Technologies

![Language](https://img.shields.io/badge/Language-Python_3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-blue.svg)
![Pydantic](https://img.shields.io/badge/Pydantic-2.3-blue.svg)
![Jinja2](https://img.shields.io/badge/jinja2-3.1.2-blue.svg)
![Language](https://img.shields.io/badge/Language-JavaScript-blue.svg)
![asyncio](https://img.shields.io/badge/asyncio-included-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.20-blue.svg)
![Alembic](https://img.shields.io/badge/Alembic-1.7.3-blue.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![Redis](https://img.shields.io/badge/Database-Redis-blue.svg)

## Description

Our app allows users to upload, edit and delete their photos, as well as interact with each other by commenting and rating photos. Users also have the ability to create unique QR codes for their photos and share them with other community members, making photo sharing even more convenient and fun. They can also chat and discuss each other's photos and share the experience of processing photos with the help of [Cloudynary](https://cloudinary.com) service.

## Project Installation

### Local Installation

To manage project dependencies, `pipenv` is used.

* Make sure you have `pipenv` installed

* Clone the repository `git clone https://github.com/sergiokapone/SnapshotExchange.git`

* To install the dependencies, use the `pipenv install` or `pipenv sync` command.

Detailed steps in your terminal a following:

```bash
git clone https://github.com/sergiokapone/SnapshotExchange.git
cd SnapshotExchange
pipenv install
python main.py

```

### DockerHub

Our project can also be found at [DockerHub](https://hub.docker.com/repository/docker/sergiokapone/snapshopexchange). To launch the application, you can 
use the command:

```bash
docker run -p 8000:8000 sergiokapone/snapshopexchange
```

## Implementation

Once the application is running *locally*, you can browse to run it on your local host using the following links:

* To view detailed information on our project [http://localhost:8000/views/info](http://localhost:8000/views/info)

* To view detailed information on our project in `JSON` format  [http://localhost:8000/](http://localhost:8000)

* To test the connection to the database and server time information [http://localhost:8000/api/healthchecker](http://localhost:8000/api/healthchecker)

For comfortable viewing of `JSON` respone in your browser we recommend to install the extension for Google Chrome
[JSON Viewer](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh/related?hl=ru) or
[JSON Formatter](https://chrome.google.com/webstore/detail/json-formatter/bcjindcccaagfpapjjmafapmmgkkhgoa?hl=ru) (according to your taste)

### Admin Dashboard

We also tried to implement an Admin Dashboard for our application to conveniently manage and control its content, settings and users.

* The Admin Dashboard is available at [http://localhost:8000/views/dashboard](http://localhost:8000/views/dashboard)

### API routes

The main goal of application is primarily designed to implement a REST API, which plays a key role in ensuring efficient interaction between frontend developers (React, View, Angular) and our service.

All documentation on interacting with our API is available at the following links:

* To view `swagger` documentation [http://localhost:8000/docs](http://localhost:8000/docs)

* To view `redoc` documentation [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Chat

Also our app is equipped with a chat for short messaging via websocket. The chat is available at the link:

* [http://localhost:8000/views/chat](http://localhost:8000/views/chat)

## Information for Developers

Our project is equipped with Sphinx documentation, which you can find at [https://sergiokapone.github.io/SnapshotExchange/](https://sergiokapone.github.io/SnapshotExchange/). The documentation may be useful to other developers who
can use it to develop our project.

## License

This project is licensed under the terms of the [MIT License](LICENSE).

### MIT License

Copyright © [FastTrack Codes]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
