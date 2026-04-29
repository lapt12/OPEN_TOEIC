import discord
import mani,setup
import aiohttp,asyncio,copy,base64,random

DEFAULT_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="

class Main_Process(mani.Collection):
  def __init__(self,interaction:discord.Interaction) -> None:
    super().__init__()
    self.inter = interaction

  def decode_figure_base64(self,figure_base64) -> bytes:
    if isinstance(figure_base64,dict):
      return base64.b64decode(DEFAULT_IMAGE_BASE64)
    if isinstance(figure_base64,bytes):
      return base64.b64decode(figure_base64)
    if isinstance(figure_base64,str):
      return base64.b64decode(figure_base64)
    return base64.b64decode(DEFAULT_IMAGE_BASE64)

  @setup.send_traceback_on_error
  async def get_figure(self,per:float):
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/progress", params={"percent":per},timeout=aiohttp.ClientTimeout(total=10)) as resp:
          if resp.status != 200:return {"error": f"サーバーエラー : {resp.status}"}
          in_data = await resp.json()
          return in_data["base64"]
    except aiohttp.ClientConnectorError:return {"error": "サーバーに接続できません"}
    except asyncio.TimeoutError:return {"error": "サーバーがタイムアウトしました"}

  @setup.send_traceback_on_error
  async def get_user_data(self) -> dict[str,dict]:
    user = self.inter.user
    default_data = copy.deepcopy(setup.default_user_data)
    if str(self.inter.user.id) not in setup.cache_user_act:setup.cache_user_act[str(user.id)] = default_data
    setup.cache_user_act[str(user.id)]["user_name"] = user.name
    return copy.deepcopy(setup.cache_user_act[str(user.id)])
  
  def get_sum_achieve(self,data:dict[str,dict],quiz_number:int=None) -> int:
    achieve_num,sum_answer_count = 0,0
    if quiz_number is None:
      for quiz_data in data["words"].values():
        achieve_num += (quiz_data["correct"] + quiz_data["wrong"]) // 125
        sum_answer_count += (quiz_data["correct"] + quiz_data["wrong"])
    else:
      in_qiuz_data = data["words"].get(f"Quiz{quiz_number}")
      if in_qiuz_data:
        achieve_num += (in_qiuz_data["correct"] + in_qiuz_data["wrong"]) // 125
        sum_answer_count += (in_qiuz_data["correct"] + in_qiuz_data["wrong"])
    return achieve_num, sum_answer_count

  def get_per(self,data:dict[str,dict[str,dict]],quiz_number:int=None) -> tuple[float, int]:
    per,achieve_total_words = 0.0,0
    if quiz_number is None:
      achieve_total_words = sum(len(quiz_data["progress"]) for quiz_data in data["words"].values())
      per = (achieve_total_words / 1250) * 100
    else:
      quiz_data = data["words"].get(f"Quiz{quiz_number}")
      if quiz_data:
        achieve_total_words += len(quiz_data["progress"])
        per = (len(quiz_data["progress"]) / 125) * 100
    return per,achieve_total_words
  
  def get_correct_per(self,data:dict[str,dict[str,dict]],quiz_number:int=None) -> float:
    correct_per = 0.0
    if quiz_number is None:
      total_correct = sum(quiz_data["correct"] for quiz_data in data["words"].values())
      total_answers = sum(quiz_data["correct"] + quiz_data["wrong"] for quiz_data in data["words"].values())
      correct_per = (total_correct / total_answers) * 100 if total_answers > 0 else 0.0
    else:
      quiz_data = data["words"].get(f"Quiz{quiz_number}")
      if quiz_data:
        total_correct = quiz_data["correct"]
        total_answers = quiz_data["correct"] + quiz_data["wrong"]
        correct_per = (total_correct / total_answers) * 100 if total_answers > 0 else 0.0
    return correct_per
  
  def get_weak_words_per(self,data:dict[str,dict[str,dict]],quiz_number:int=None) -> tuple[float, int]:
    per,achieve_total_words,clear_total_words = 0.0,0,0
    if quiz_number is None:
      achieve_total_words = sum(len(quiz_data) for quiz_data in data["weak_words"].values())
      clear_total_words = sum(sum(v is True for v in quiz_data.values()) for quiz_data in data["words"].values())
      per = (clear_total_words / achieve_total_words) * 100 if achieve_total_words > 0 else 0.0
    else:
      quiz_data = data["weak_words"].get(f"Quiz{quiz_number}")
      if quiz_data:
        achieve_total_words += len(quiz_data)
        clear_total_words += sum(v is True for v in quiz_data.values())
        per = (clear_total_words / achieve_total_words) * 100 if achieve_total_words > 0 else 0.0
    return per,clear_total_words,achieve_total_words
  
  def get_quiz_questions(self,user_data:dict[str,dict[str,dict]],quiz_number:int=None) -> list[dict,dict,dict,dict] | None:
    user_have_word_range:list = user_data["words"].get(f"Quiz{quiz_number}").get("progress",[]) if quiz_number is not None else [item for quiz in user_data["words"].values() for item in quiz["progress"]]
    default_range:list = setup.word_data.get(f"Quiz{quiz_number}") if quiz_number is not None else setup.list_all_word
    all_dict = setup.dict_all_word
    co_selected_words = list(set(default_range) - set(user_have_word_range))
    if len(co_selected_words)== 0:return None
    correct_answer = random.choice(co_selected_words)
    selected_words = random.sample([w for w in all_dict.keys() if w != correct_answer], 3)
    questions = [{"word": word, "meaning":all_dict.get(word, "不明"),"answer":False} for word in selected_words]
    questions += [{"word": correct_answer, "meaning": all_dict.get(correct_answer, "不明"), "answer": True}]
    return questions
  
  async def chenge_user_status(self,correct:bool,word:str) -> None:
    quiz_tag = setup.index_from_word.get(word,None)
    if quiz_tag is None:return
    progress = setup.cache_user_act[str(self.inter.user.id)]["words"][quiz_tag]["progress"]
    if not word in progress:progress.append(word)
    if len(progress) >= 125:progress = []
    setup.cache_user_act[str(self.inter.user.id)]["words"][quiz_tag]["correct" if correct else "wrong"] += 1