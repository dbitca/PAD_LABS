FROM python:3.8-slim
COPY . .
RUN pip install flask expiringdict requests
EXPOSE 5000
CMD ["python", "app.py"]