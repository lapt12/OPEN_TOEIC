import discord
import mani
import json,traceback,functools,aiohttp,aiofiles,os

bot:discord.Client = None

config:dict = {}

version:str = ""
owner_user_id:int = 0
emergency_webhook:str = ""

default_user_data:dict[str,dict] = {}
cache_user_act:dict = {}

word_data:dict[str,dict] = {}
list_all_word:list[str] = []
dict_all_word:dict[str,dict] = {}
index_from_word:dict[str,str] = {}

emojis:dict[str,str] = {}
layout_color:dict[str,bytes] = {}

def check_data_type(data):
    try:
        json.dumps(data, indent=4, ensure_ascii=False)
        return True
    except (KeyError,ValueError):
        return False

def get_path(path:list[str]) -> str:
  for p in path:
    if os.path.exists(p):
      return os.path.abspath(p)
  return None

async def send_error_to_discord(error_text: str):
  async with aiohttp.ClientSession() as session:
    await session.post(emergency_webhook, json={"content": f"<@{owner_user_id}>\n```\n{error_text}\n```"})

def send_traceback_on_error(func):
  @functools.wraps(func)
  async def wrapper(*args, **kwargs):
    try:
      return await func(*args, **kwargs)
    except Exception:
      error_text = traceback.format_exc()
      await send_error_to_discord(error_text)
  return wrapper

class Setup:
  def __init__(self,bot:discord.Client):
    self.bot = bot
  
  @send_traceback_on_error
  async def main(self) -> bool:
    global bot,cache_user_act,config,version,owner_user_id,emergency_webhook,default_user_data,word_data,list_all_word,dict_all_word,emojis,layout_color
    bot = self.bot
    await mani.Collection().create_table()
    print("[Setup] データベースの初期化が完了しました。")
    cache_user_act = await mani.Collection().load()

    path = get_path([r".config.json", r"main\.config.json",r"main/.config.json"])
    word_path = get_path([r".data.json", r"main\.data.json",r"main/.data.json"])
    if path is None or word_path is None:
      print(r"[\\ Setup ERROR //] 設定ファイルが見つかりません。`.config.json`を作成してください。")
      return False

    async with aiofiles.open(word_path, mode='r', encoding='utf-8') as f:
      word_data = json.loads(await f.read())
      list_all_word = [item for quiz in word_data.values() for item in quiz.keys()]
      dict_all_word = {k: v for quiz in word_data.values() for k, v in quiz.items()}
      for quiz_tag,words in word_data.items():
        for word in words.keys():index_from_word[word] = quiz_tag
      print("[Setup] 単語の読み込みが完了しました。")

    async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
      config = json.loads(await f.read())
      version = config["version"]
      emergency_webhook = config["emergency_webhook_url"]
      owner_user_id = config["owner_user_id"]
      default_user_data = config["default_datas"]["user_data"]
      emojis = config["emojis"]
      layout_color = {key: int(value, 16) for key, value in config["layout_color"].items()}
    print("[Setup] 設定の読み込みが完了しました。")
    return True
    

