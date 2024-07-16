# kikl.co

_Who could forget **awkward-puffin**?_

**[kikl.co](https://kikl.co)** is a different kind of link shortener. Instead of making URLs as **short** as possible, it makes them as **memorable** as possible.

By default, each link only lasts 24 hours, perfect for quickly transferring a long URL from one device to another 💻📲 or telling people verbally. 😮💬

## Stack

- [Django web framework](https://www.djangoproject.com/)
- [SQLite](https://www.sqlite.org/)
- [Vue.js](https://vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)

## Setup

Prerequisite: [Install Docker](https://docs.docker.com/engine/install/).

1. `cp .env.example .env`
2. In `.env`, fill in the required enviornment variables.
3. `docker compose up`

## Resources

- [Postman collection](kikl.postman_collection.json)

### Nginx config

```Nginx
server {

    server_name kikl.co;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```