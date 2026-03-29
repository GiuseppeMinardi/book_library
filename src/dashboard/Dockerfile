FROM python:3.13-slim
ARG port
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE ${port}
# Start streamlit dashboard
CMD ["streamlit", "run", "dashboard.py", "--server.port=${port}", "--server.address=0.0.0.0"]