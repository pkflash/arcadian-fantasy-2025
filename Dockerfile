FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT 8080
CMD ["gunicorn", "-b", ":8080", "app:app"] 