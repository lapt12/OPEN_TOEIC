import discord
import setup,copy,layout_setting

class Main_Callback:
  def __init__(self,interaction:discord.Interaction) -> None:
    self.inter = interaction
    self.funcs = {
      "auth-modal": self.auth_modal,
      "select_range": self.select_range,
      "start_test":self.start_test_callback,
      "quiz":self.select_quiz,
      "mode_change":self.mode_change,
      "return_board":self.start_board
    }
  
  @setup.send_traceback_on_error
  async def MAIN(self) -> None:
    self.custom_id = self.inter.data.get("custom_id", "").replace("[word]", "")
    try:await [func for name,func in self.funcs.items() if self.custom_id.startswith(name)][0]()
    except IndexError:await self.inter.response.send_message("[word]の中に有効なcallbackが見つかりませんでした。", ephemeral=True)

  async def start_board(self):
    quiz_number = None if "all" in self.custom_id else int(self.custom_id.split("_")[-1].replace("Quiz",""))
    layout,image = await layout_setting.Layout(self.inter).start_display(quiz_number)
    if layout is None:await self.inter.response.send_message("レイアウトの生成に失敗しました、少し待ってからもう一度お試しください。", ephemeral=True)
    await self.inter.response.edit_message(view=layout, attachments=[image])

  async def mode_change(self) -> None:
    quiz_number = [in_data for in_data in list(self.inter.message.components)[0].to_dict()["components"] if in_data["type"] == 9][0]["components"][0]["content"].split("\n")[0].replace("### TOEICテスト / [ ","").replace(" ]","").replace("Quiz","")
    layout,image = await layout_setting.Layout(self.inter).english_quiz_display(quiz_number if "all" not in quiz_number else None,"ja" not in self.custom_id)
    if layout is None:await self.inter.response.send_message("レイアウトの生成に失敗しました、少し待ってからもう一度お試しください。", ephemeral=True)
    else:await self.inter.response.edit_message(view=layout, attachments=[image])

  async def select_quiz(self) -> None:
    layout,image = await layout_setting.Layout(self.inter).ending_layout()
    await self.inter.response.edit_message(view=layout, attachments=[image])

  async def start_test_callback(self) -> None:
    quiz_number = None if "all" in self.custom_id else int(self.custom_id.split("_")[-2].replace("Quiz",""))
    layout,image = await layout_setting.Layout(self.inter).english_quiz_display(quiz_number=quiz_number,reverse=("ja" in self.custom_id))
    if layout is None:await self.inter.response.send_message("レイアウトの生成に失敗しました、少し待ってからもう一度お試しください。", ephemeral=True)
    else:await self.inter.response.edit_message(view=layout, attachments=[image])
  
  async def select_range(self) -> None:
    selected_value = self.inter.data["values"][0]
    quiz_number = int(selected_value.replace("Quiz","")) if selected_value != "all" else None
    layout,image = await layout_setting.Layout(self.inter).start_display(quiz_number)
    if layout is None:await self.inter.response.send_message("レイアウトの生成に失敗しました、少し待ってからもう一度お試しください。", ephemeral=True)
    else:await self.inter.response.edit_message(view=layout, attachments=[image])

  async def auth_modal(self) -> None:
    password = self.inter.data["components"][0]["components"][0]["value"]
    if password == setup.config["password"]:
      import _main
      if str(self.inter.user.id) not in setup.cache_user_act:
        setup.cache_user_act[str(self.inter.user.id)] = copy.deepcopy(setup.default_user_data)
      setup.cache_user_act[str(self.inter.user.id)]["auth"] = True
      await _main.test_command.callback(self.inter)
      await self.inter.followup.send("認証に成功しました！", ephemeral=True)
    else:
      await self.inter.response.send_message("認証に失敗しました。少し待ってから、再度入力してください。", ephemeral=True)