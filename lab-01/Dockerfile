FROM python:3.12 AS build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN useradd --create-home --uid 10001 app \
 && mkdir -p /data && chown app:app /data
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY app.py .
USER app
EXPOSE 8080
CMD ["python", "app.py"]
