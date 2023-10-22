FROM python:3.10
RUN pip install Flask
RUN pip install requests
RUN pip install flask-cors
WORKDIR app
ENV PYTHONPATH="/app/lib"
VOLUME /data
COPY . .
CMD ./netprobe_runner.sh