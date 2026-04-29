from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import io, base64
import uvicorn
matplotlib.use("Agg")

app = FastAPI()

def generate_circle(percent: float, size: int = 4) -> bytes:
  fig, ax = plt.subplots(figsize=(size, size))
  ax.set_aspect('auto')
  bg = plt.Circle((0, 0), 1, color="#333333", fill=False, linewidth=15)
  ax.add_artist(bg)
  ax.pie(
    [percent, 100 - percent],
    radius=1,
    startangle=90,
    colors=["#00ccff", (0, 0, 0, 0)],
    wedgeprops=dict(width=0.15, edgecolor="none")
  )
  ax.text(
    0, 0, f"{percent:.0f}%",
    ha="center", va="center",
    fontsize=40, color="white", fontweight="bold"
  )
  fig.patch.set_alpha(0)
  ax.set_facecolor("none")
  buf = io.BytesIO()
  plt.savefig(buf, format="png", transparent=True, bbox_inches="tight", pad_inches=0)
  plt.close(fig)
  buf.seek(0)
  img = Image.open(buf)
  img = img.convert("P", palette=Image.ADAPTIVE, colors=64)
  output_buf = io.BytesIO()
  img.save(
      output_buf,
      format="PNG",
      optimize=True,   
      compress_level=9,  
  )
  return output_buf.getvalue()

@app.get("/progress")
def get_progress(percent: float = Query(..., ge=0, le=100)):
  image_bytes = generate_circle(percent)
  base64_str = base64.b64encode(image_bytes).decode("utf-8")
  return JSONResponse(content={"percent": percent, "base64": base64_str})

if __name__ == "__main__":
  print("[Server] 画像出力サーバーが起動しました。")
  uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")