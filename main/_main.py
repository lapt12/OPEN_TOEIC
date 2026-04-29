import discord
from discord.app_commands import allowed_installs
from discord.ext import tasks
from dotenv import load_dotenv
import mani,setup,layout_setting,prosess,view_callback
import os,asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)

SETUP_FLAG = False
FRIST_LOOP = False

@client.event
async def on_ready():
  global SETUP_FLAG,FRIST_LOOP
  print(f'[Main] ログイン開始: {client.user} (ID: {client.user.id})')
  #await tree.sync()
  await setup.Setup(client).main()
  SETUP_FLAG = True
  await client.change_presence(status=discord.Status.online,activity=discord.CustomActivity(name=f"Ver : {setup.version} | 「 /test 」"))
  print(f'[Main] {client.user}が正常にdiscordに接続されました。')
  if not FRIST_LOOP:on_loop.start()

@tasks.loop(minutes=10)
async def on_loop():
  global SETUP_FLAG,FRIST_LOOP
  if not SETUP_FLAG:return
  if FRIST_LOOP:
    for user_id,point in setup.cache_user_act.items():await mani.Collection().save(user_id,point)
  FRIST_LOOP = True

@client.event
async def on_interaction(interaction: discord.Interaction):
  if interaction.type == discord.InteractionType.application_command or not SETUP_FLAG:return
  interaction_id = interaction.data.get("custom_id", "")
  if interaction_id.startswith("[word]"):
    await view_callback.Main_Callback(interaction).MAIN()

@tree.command(name='test', description='TOEICの単語テストボードを展開します。')
@setup.send_traceback_on_error
@allowed_installs(guilds=False, users=True)
async def test_command(interaction: discord.Interaction):
  user_data = await prosess.Main_Process(interaction).get_user_data()
  if not user_data.get("auth", False):
    modal = discord.ui.Modal(title="認証", timeout=None, custom_id="[word]auth-modal")
    text_input = discord.ui.TextInput(label="配布されたパスワードを入力してください", style=discord.TextStyle.short, required=True, placeholder="パスワードを入力")
    modal.add_item(text_input)
    await interaction.response.send_modal(modal);return
  layout,image = await layout_setting.Layout(interaction).start_display()
  if layout is None:await interaction.response.send_message("レイアウトの生成に失敗しました、少し待ってからもう一度お試しください。", ephemeral=True);return
  await interaction.response.send_message(view=layout, file=image, ephemeral=True)

async def main():
  try:
    await client.start(TOKEN)
  except (KeyboardInterrupt, asyncio.CancelledError):
    for user_id,point in setup.cache_user_act.items():
      await mani.Collection().save(user_id,point)
    print("[Main] player_activityを正常に保存しました。")

if __name__ == "__main__":
  asyncio.run(main())