import os
DATABASE_URL=os.getenv("DATABASE_URL","postgresql+psycopg://mix:mix-demo@db/mix")
REDIS_URL=os.getenv("REDIS_URL","redis://redis:6379/0")
JWT_SECRET=os.getenv("JWT_SECRET","mix-contribution-development-secret-replace")
SEED_DEMO=os.getenv("SEED_DEMO","true").lower()=="true"
