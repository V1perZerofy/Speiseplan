# Web Speiseplan München

## Instalation and setup 

```bash
git clone https://github.com/V1perZerofy/Speiseplan.git
cd Speiseplan
python -m venv .venv
source .venv/bin/activate
# or .venv/bin/activate.fish
# according to your shell

pip install -r requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload

cd frontend
npm install
npm run dev
