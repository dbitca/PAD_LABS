FROM python:3.8-slim
COPY . .
RUN pip install flask expiringdict requests
EXPOSE 8001
CMD ["python", "app.py"]