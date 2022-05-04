FROM python:3.10.2

#setup workdir
WORKDIR /simulation

#install pip deps
COPY requirement.txt /
RUN pip install --no-cache-dir -r /requirement.txt && rm -rf /requirement.txt

#put src code in
COPY src /src/