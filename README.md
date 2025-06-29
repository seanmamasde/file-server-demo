# File Server Demo

## Clone & Setup
```bash
git clone https://github.com/seanmamasde/fileserver-demo.git
cd fileserver-demo

# create virtualenv (any tool is fine)
python -m venv .venv && source .venv/bin/activate

# install deps
pip install poetry
poetry install
```

## Local Containers

```bash
# build and bring up fullstack (api + db)
docker compose up --build

# follow logs
docker compose logs -f
```

## CLI Usages

```bash
# default server = http://localhost:8000

echo "hello world" > hello.txt # or any file you want

./filesrv-cli upload ./hello.txt
./filesrv-cli list
./filesrv-cli download hello.txt -o ./downloads/
./filesrv-cli delete hello.txt
./filesrv-cli ping
```
