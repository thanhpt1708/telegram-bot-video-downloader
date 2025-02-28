FROM python:3.12-bullseye

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"
RUN apt-get update && apt-get install -y python3-dev
ADD https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz /tmp/
WORKDIR /tmp
RUN tar -xJf ffmpeg-master-latest-linux64-gpl.tar.xz \
    && mv ffmpeg-master-latest-linux64-gpl/bin/* /usr/local/bin/ \
    && rm -rf ffmpeg-master-latest-linux64-gpl
RUN groupadd appgroup && useradd -g appgroup appuser

WORKDIR /home/app
COPY --chown=appuser:appgroup pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY --chown=appuser:appgroup . .

USER appuser
CMD ["python", "-m", "main"]
