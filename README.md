# wangfu-register
![demo1](https://i.imgur.com/8SoOIfi.jpeg)

## Development
Create virtual environment and install dependencies
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```
Debug the code
```
# frontend
cd web
npm install --save-dev
npx parcel src/index.html

# backend
cd server
python3 -m fastapi dev
```

## Deployment
```
# frontend
cd web
npx parcel build src/index.html

# backend
cd server
python3 -m fastapi run --host "127.0.0.1" --port 10010 --proxy-headers main.py
```

## Todo
- password reset
- add more tests
