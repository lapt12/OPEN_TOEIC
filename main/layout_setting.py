import discord
from discord import ui
import prosess,setup,io,random,mani

class Layout(prosess.Main_Process):
  def __init__(self, interaction: discord.Interaction):
    super().__init__(interaction)
    self.inter = interaction
    self.banner_url = setup.config["banners"]["word"]["default"]
  
  @setup.send_traceback_on_error
  async def info_container(self,quiz_number:int,user_data:dict) -> tuple[ui.Container, discord.File]:
    quiz_number = quiz_number if quiz_number is not None and quiz_number != "all" else None
    container = ui.Container(accent_color=setup.layout_color.get(f"Quiz{quiz_number}", 0x000000))
    gallery = ui.MediaGallery()
    gallery.add_item(media=self.banner_url)
    container.add_item(gallery)

    achieve_num, sum_answer_count = self.get_sum_achieve(user_data, quiz_number)
    per, achieve_total_words = self.get_per(user_data, quiz_number)
    weak_total_words = self.get_weak_words_per(user_data, quiz_number)[2]
    content  = f"### TOEICテスト / [ {f'Quiz{quiz_number}' if quiz_number is not None else 'all'} ]\n"
    content += f"> **Status**\n\
  **全ての合計週数** : ` {achieve_num} 週 `\n\
  **進捗** : ` {round(per,2)} % ({achieve_total_words} / 125{'0' if quiz_number is None else ''}) `\n\
  **総合回答数** : ` {sum_answer_count} 回 `\n\
  **正答率** : ` {round(self.get_correct_per(user_data),2)} % `\n\
  **苦手登録単語数** : ` {weak_total_words} 単語 `\n\
-# ({self.inter.user.id})"
    figure_base64 = await mani.Collection(r"main/.image.db").fetch(str(round(per)))
    image_bytes = self.decode_figure_base64(figure_base64)
    image = discord.File(io.BytesIO(image_bytes),filename="image.png")
    container.add_item(ui.Section(ui.TextDisplay(content),accessory=ui.Thumbnail("attachment://image.png")))
    return container, image
  
  @setup.send_traceback_on_error
  async def start_display(self,quiz_number:int=None) -> tuple[ui.LayoutView,discord.File] | None:
    quiz_tag = f'Quiz{quiz_number}' if quiz_number is not None else 'all'
    user_data = await self.get_user_data()
    layout = ui.LayoutView()
    container, image = await self.info_container(quiz_number, user_data)
    action_row,select_row = ui.ActionRow(),ui.ActionRow()
    
    start_button = ui.Button(emoji=setup.emojis["hikouki"],label="Start",style=discord.ButtonStyle.blurple,custom_id=f"[word]start_test_{quiz_tag}_en")
    #myword_button = ui.Button(emoji=setup.emojis["file"],label="My Words",style=discord.ButtonStyle.gray,custom_id="[word]my_words_display")
    select_values = list(setup.word_data.keys()) + ["all"]
    select_values.remove(quiz_tag)
    select_options = [discord.SelectOption(label=f"{i+1}. {word_id}",description=f"{word_id if word_id != 'all' else '全て'}の範囲で単語テストを行います。",value=word_id) for i,word_id in enumerate(select_values)]
    start_select = ui.Select(options=select_options,placeholder=f"テスト範囲を選択 / [現在 : {quiz_tag}]",custom_id="[word]select_range")

    container.add_item(ui.Separator())
    select_row.add_item(start_select)
    action_row.add_item(start_button)
    #action_row.add_item(myword_button)
    container.add_item(select_row)
    container.add_item(ui.Separator())
    container.add_item(action_row)
    layout.add_item(container)
    return layout,image
  
  @setup.send_traceback_on_error
  async def english_quiz_display(self,quiz_number:int,reverse:bool=False) -> tuple[ui.LayoutView,discord.File] | None:
    user_data = await self.get_user_data()
    questions = self.get_quiz_questions(user_data, quiz_number)
    if questions is None:return await self.start_display()
    
    layout = ui.LayoutView()
    container, image = await self.info_container(quiz_number, user_data)
    config_row,action_row = ui.ActionRow(),ui.ActionRow()
    if not reverse:mode_button = ui.Button(emoji=setup.emojis["system"],label="英 -> 日",style=discord.ButtonStyle.blurple,custom_id="[word]mode_change_en")
    else:mode_button = ui.Button(emoji=setup.emojis["system"],label="日 -> 英",style=discord.ButtonStyle.green,custom_id="[word]mode_change_ja")
    quiz_container = ui.Container(accent_color=setup.layout_color.get(f"Quiz{quiz_number}", 0x000000))
    
    content = f"> **{questions[3]['word' if not reverse else 'meaning']}**\n"
    random.shuffle(questions)
    for i, quiz in enumerate(questions):content += f"{i+1}. 「{quiz['meaning' if not reverse else 'word']}」\n"
    quiz_buttons = [ui.Button(label=str(i+1),style=discord.ButtonStyle.gray,custom_id=f"[word]quiz_{i+1}_{questions[i]['word']}_{questions[i]['answer']}") for i in range(4)]
    quiz_container.add_item(ui.TextDisplay(content))
    for button in quiz_buttons:action_row.add_item(button)
    config_row.add_item(mode_button)
    container.add_item(ui.Separator())
    container.add_item(config_row)
    quiz_container.add_item(action_row)
    layout.add_item(container)
    layout.add_item(quiz_container)
    return layout,image
  
  @setup.send_traceback_on_error
  async def ending_layout(self):
    quiz_tag = [in_data for in_data in list(self.inter.message.components)[0].to_dict()["components"] if in_data["type"] == 9][0]["components"][0]["content"].split("\n")[0].replace("### TOEICテスト / [ ","").replace(" ]","")
    quiz_index,_,quiz_answer_flag = self.inter.data["custom_id"].replace("[word]quiz_","").split("_")
    quiz_answer_flag = True if "True" in quiz_answer_flag else False
    com_data = [in_data for in_data in list(self.inter.message.components)[1].to_dict()["components"] if in_data["type"] == 10][0]
    mode_button_data = [in_data for in_data in list(self.inter.message.components)[0].to_dict()["components"] if in_data["type"] == 1][0]["components"][0]
    raw_button_data = [in_data for in_data in list(self.inter.message.components)[1].to_dict()["components"] if in_data["type"] == 1][0]["components"]
    button_data = [in_data["custom_id"] for in_data in raw_button_data]
    answer_word = [word.split("_")[2] for word in button_data if "True" in word][0]
    await self.chenge_user_status(quiz_answer_flag,answer_word)
    user_data = await self.get_user_data()
    
    layout = ui.LayoutView()
    container, image = await self.info_container(quiz_tag.replace("Quiz",""), user_data)
    config_row,action_row = ui.ActionRow(),ui.ActionRow()
    next_button = ui.Button(emoji=setup.emojis["hikouki"],label="次へ",style=discord.ButtonStyle.blurple,custom_id=f"[word]start_test_{quiz_tag}_{'ja' if mode_button_data['label'][0] == '日' else 'en'}")
    return_button = ui.Button(emoji=setup.emojis["back"],label="タイトルへ",style=discord.ButtonStyle.gray,custom_id=f"[word]return_board_{quiz_tag}")
    mode_button = ui.Button(emoji=setup.emojis["system"],label=mode_button_data["label"],style=discord.ButtonStyle.blurple if mode_button_data["custom_id"] == "[word]mode_change_en" else discord.ButtonStyle.green,custom_id="[word]mode_change_en",disabled=True)
    quiz_container = ui.Container(accent_color=setup.layout_color.get(quiz_tag, 0x000000))
    set_color = lambda index,in_data:discord.ButtonStyle.green if ((index + 1) == int(quiz_index) and quiz_answer_flag) or "True" in in_data else discord.ButtonStyle.red if (index + 1) == int(quiz_index) else discord.ButtonStyle.gray
    quiz_buttons = [ui.Button(label=str(i+1),style=set_color(i,_d),custom_id=f"[word]quiz_{i+1}",disabled=True) for i,_d in enumerate(button_data)]
    
    quiz_container.add_item(ui.TextDisplay(com_data["content"]))
    for button in quiz_buttons:action_row.add_item(button)
    config_row.add_item(next_button);config_row.add_item(return_button);config_row.add_item(mode_button)
    container.add_item(ui.Separator())
    container.add_item(config_row)
    quiz_container.add_item(action_row)
    layout.add_item(container)
    layout.add_item(quiz_container)
    return layout,image
