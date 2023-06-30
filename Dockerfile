FROM python:3.8

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

ENV MPLCONFIGDIR /tmp
ENV NUMBA_CACHE_DIR /tmp

CMD ["panel", "serve", "/code/rome-in-transit.py", "--address", "0.0.0.0", "--port", "7860", "--allow-websocket-origin", "ivn888-rome-in-transit.hf.space", "--allow-websocket-origin", "0.0.0.0:7860"]
