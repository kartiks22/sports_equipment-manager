# Another image is pre-created which contains all the dependencies. For build-time convenience. And that image is loaded.
FROM lalithkota/sportsroom_depend

# Copy the current directory contents into the container at /SportsRoom
ADD . /SportsRoom

# Just a remainder, to publish the actual port and ip while running.
EXPOSE 8000

# fully flush the database, while building the image itself. So that every next run starts with a clean database
RUN python manage.py flush --noinput

# create a superuser with username: 'admin' and password:'admin', allowing ease of management of database.
# It is suggested to immediately change the admin password after running container, to avoid misuse.
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell

# On the start of run-conatainer, run the server itself.
ENTRYPOINT ["/bin/bash","sportsroom_inside_docker.sh", "runserver 0.0.0.0:8000"]
