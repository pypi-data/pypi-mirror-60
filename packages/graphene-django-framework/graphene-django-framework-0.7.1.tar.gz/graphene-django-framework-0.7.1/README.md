# graphene-django-framework

Don't want to use Relay with Graphene? You are not alone. All other packages for django implement the Relay interface. 😞

[Graphene-Django](https://github.com/graphql-python/graphene-django) adds the ability to filter and paginate but you must follow the Relay specification which requires the use of Nodes, Edges, Connections, and Global IDs.

Apollo is a great GraphQL client and can still be used with Relay but has its downsides. 


## Install

    pip install graphene-django-framework

## Hacking

You must have docker and docker-compose

    # setup the docker env with your uid and gid
    echo -e "UID=$(id -u)\nGID=$(id -g)" > .env

    # first migrate the database
    docker-compose run web python manage.py migrate
    
    # create a superuser to login with
    docker-compose run web python manage.py createsuperuser
    
    # run the server
    docker-compose run web python manage.py runserver
    # or tests
    docker-compose run web python manage.py test
