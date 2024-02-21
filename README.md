# Loan Management

### To start the app run the following steps.

1. Run the services from docker-compose.yaml file:

`docker compose up -d --build`

2. Check if both the service are up and running:

`docker ps`

3. Now when the application is running we need to go inside the application to make migrations and migrate the modals for creation of the table. Run the following command to go inside the `web` container.

`docker exec -it <container-id> bash`

NOTE: here `container-id` means the `ID` which you got from step 2.

4. A bash will load on the command-line then run the following commands to make migrations and migrate.

`python manage.py makemigrations`

`python manage.py migrate`

5. Exit from the bash with `ctrl + d` on your keyboard.

6. Open Postman and start using the APIs. The app is listening to port 8000 so your API will look like:

`http://localhost:8000/api/register`

7. Your app is up and running 