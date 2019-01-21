# urlshortener
Provide an api for shortening an URL

Docker build -f Dockerfile -t urlshortener .

docker save urlshortener > urlshortener.tar You will see this in your directory where you execute docker build command.

Then you can load it anywhere else as

docker load < urlshortener.tar


Reference:- https://docs.docker.com/engine/reference/commandline/export/#options
