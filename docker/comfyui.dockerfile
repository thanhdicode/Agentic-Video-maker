FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.11 python3-pip git wget libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app
RUN pip install -r requirements.txt

EXPOSE 8188
CMD ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
