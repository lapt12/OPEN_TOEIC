import subprocess,os,sys

def get_path(path:list[str]) -> str:
  for p in path:
    if os.path.exists(p):
      return os.path.abspath(p)
  return None

main_paths = [r"main/_main.py",r"_main.py"]
create_config_paths = [r"main/create_per_figure_server.py",r"create_per_figure_server.py"]

try:
  p1 = subprocess.Popen([sys.executable, get_path(main_paths)])
  #p2 = subprocess.Popen([sys.executable, get_path(create_config_paths)])
  while True:
    if p1.poll() is not None:break
    try:p1.wait(timeout=1)
    except subprocess.TimeoutExpired:continue
except KeyboardInterrupt:
  print("\n[Starter] 処理に停止命令を実行しました。プロセスを終了中...")
  p1.terminate();p1.wait()
  print("[Starter] すべてのプロセスが終了。")
  sys.exit(0)