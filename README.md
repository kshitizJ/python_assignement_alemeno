# Loan Management

### To start the app run the following steps.

We will run each service one by one.

1. Run the DB service:

`docker compose up -d --build db`

2. Once the DB service is up and running then run the WEB service:

`docker compose up -d --build web`

3. Check if both the service are up and running:

`docker ps`

4. Now when the application is running we need to go inside the application to make migrations and migrate the modals for creation of the table. Run the following command to go inside the `web` container.

`docker exec -it <container-id> bash`

NOTE: here `container-id` means the `ID` which you got from step 3.

5. A bash will load on the command-line then run the following commands to make migrations and migrate.

`python manage.py makemigrations`

`python manage.py migrate`

6. Exit from the bash with `ctrl + d` on your keyboard.

7. Open Postman and start using the APIs. The app is listening to port 8000 so your API will look like:

`http://localhost:8000/api/register`

8. Your app is up and running 