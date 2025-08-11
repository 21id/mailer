![21ID Mailer Service](./misc/images/banner.png)

## About

Mailer is a service for sending service notifications, such as:

- student verification
- authorization
- 2FA codes

Mailer service is a part of [21ID](https://21id.uz) ecosystem, which is an identification service for [School 21](https://21-school.uz) students.

## Quick setup

1. Install Docker and Docker Compose
    - [Docker install documentation](https://docs.docker.com/install/)
    - [Docker Compose install documentation](https://docs.docker.com/compose/install/)
2. Create a docker-compose.yml file similar to this:
    ```yml
    services:
        rabbitmq:
            image: docker.io/rabbitmq:latest
            volumes:
                - rabbitmq:/var/lib/rabbitmq
                - rabbitmq_conf:/etc/rabbitmq
        mailer:
            image: ghcr.io/21id/mailer:latest
            restart: unless-stopped
            environment:
                - SMTP_HOST=smtp.example.com
                - SMTP_PORT=465
                - SMTP_FROM="Example Sender"
                - SMTP_USER=no-reply@example.com
                - SMTP_PASSWORD=example_pass
                - SMTP_USE_TLS=True
                - SMTP_VERIFY_CERT=False
                - AMQP_HOST=rabbitmq
                - AMQP_PORT=5672
                - AMQP_USER=guest
                - AMQP_PASSWORD=guest
                - AMQP_QUEUE=mailer/requests
                - AMQP_VHOST=/
                - SECRET_KEY=verysecretkey
    volumes:
        rabbitmq:
        rabbitmq_conf:
    ```

    This is the minimum configuration required.
3. Bring up your stack by running
    ```
    docker compose up -d
    ```
4. Test it out via `amqp-tools` or REST API (see `localhost:8000/redoc` for documentation)

## Data structures
By default, AMQP consumer listens to the queue specified in the .env file (`AMQP_QUEUE`) and expects a message with the EmailRequest structure:
```json
{
    "to": "string",
    "subject": "string",
    "template": "string",
    "context": {
        "key": "string"
    }
}
```

The consumer is also duplicated by the REST server for debugging and use in environments where sending messages via the AMQP is not possible.

For an extended description of the fields, visit the Swagger/Redoc documentation (Schemas section)

## Contributing
We'd love for you to create pull requests for this project from the development branch. Latest releases are created from the main branch.

## Contact us
- [21ID Telegram Channel](https://t.me/ident21)
- [Emil aka. lunnaholy aka. kristana](https://t.me/lunnaholy)
- [Aleksey aka. megaplov aka. daemonpr](https://t.me/megaplov)

Made with ❤️ at School 21