import aiosqlite
import json

class Collection:
  def __init__(self,DB_PATH:str=f"main/.user_data.db") -> None:
    self.DB_PATH = DB_PATH
  
  async def save(self,key:any,value:any) -> None:
    key = json.dumps(key,ensure_ascii=False,indent=2) if not isinstance(key,(str,int)) else key
    value = json.dumps(value,ensure_ascii=False,indent=2) if not isinstance(value,(str,int)) else value
    async with aiosqlite.connect(self.DB_PATH) as db:
      await db.execute(
        "INSERT OR REPLACE INTO user_data (key, value) VALUES (?, ?)",
        (key, value)
      )
      await db.commit()
  
  async def delete(self,key:any) -> None:
    key = json.dumps(key, ensure_ascii=False, indent=2) if not isinstance(key, (str, int)) else key
    async with aiosqlite.connect(self.DB_PATH) as db:
      await db.execute("DELETE FROM user_data WHERE key = ?", (key,))
      await db.commit()
  
  async def load(self) -> dict:
    async with aiosqlite.connect(self.DB_PATH) as db:
      cursor = await db.execute("SELECT * FROM user_data")
      rows = await cursor.fetchall()
      result = {}
      if rows and len(rows[0]) > 2:
        for index,key,value in rows:
          result[index] = (key,value)
      else:
        for key, value in rows:
          if isinstance(value, str) and len(value) > 0 and value[0] in ["{", "["]:
            try:
              result[key] = json.loads(value)
              continue
            except json.JSONDecodeError:pass
          result[key] = value
      return result
  
  async def fetch(self,key:any) -> any:
    async with aiosqlite.connect(self.DB_PATH) as db:
      cursor = await db.execute("SELECT key, value FROM user_data WHERE key = ?", (key,))
      row = await cursor.fetchone()
      if not row:return None
      _,v = row
      if isinstance(v, str) and len(v) > 0 and v[0] in [r"{", r"["]:
        try:v = json.loads(v)
        except json.JSONDecodeError:pass
      return v

  async def create_table(self):
    async with aiosqlite.connect(self.DB_PATH) as db:
      await db.execute("""
          CREATE TABLE IF NOT EXISTS user_data (
              key TEXT PRIMARY KEY,
              value TEXT
          )
      """)
      await db.commit()