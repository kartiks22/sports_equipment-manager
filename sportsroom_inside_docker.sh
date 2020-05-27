exit_func() {
        echo "SIGTERM detected"
        exit 1
}
trap exit_func SIGTERM SIGINT

./redis-server&
celery -A sportsroom worker -l info &
celery -A sportsroom beat -l info &
python manage.py makemigrations
python manage.py migrate
python manage.py $@
