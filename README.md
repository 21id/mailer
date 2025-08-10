<br> 
<div style="display: flex; width: 100%; background-color: #0C8CE9">
   <img src="misc/images/banner.png" alt="21ID Mailer service banner" width=70%>
</div>

## About
Mailer service is a service to send notifications for signup, login, authentication and 2-nd Factor authentication codes.

Mailer service is a part of [21ID](https://21id.uz) ecosystem, which is an identification service for [School 21](https://21-school.uz) students. 

## How to run locally

1. Firstly, copy .env.example to .env and edit it, filling all values (I used *nano* just as example).

    ```
    cp .env.example .env 
    nano .env
    ```

2. Then, you can run it via docker, commands for which I've packed in [dev.sh](dev.sh) bash script

    ```
    ./dev.sh
    ```

3. App is now running locally on port 8000, and is exposed to internet
