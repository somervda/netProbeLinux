FROM python:3.10.6
RUN pip install Flask
RUN pip install requests
RUN pip install flask-cors
# RUN apt-get -y update
# RUN apt-get -y install nano
WORKDIR app
ENV PYTHONPATH="/app/lib"
VOLUME /data
COPY . .
CMD ./netprobe_runner.sh