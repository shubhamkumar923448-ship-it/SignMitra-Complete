FROM python:3.10.13

# Yeh line MediaPipe ke liye missing OS graphics files install karegi
RUN apt-get update && apt-get install -y libgl1 libgles2-mesa-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tera purana start command
CMD ["python", "main.py"]