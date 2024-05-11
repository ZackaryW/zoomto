import os
import shutil

curr = os.getcwd()
os.chdir("src/video-sharing-ui")
os.system("npm run build")

os.chdir(curr)

shutil.rmtree("src/zoomto/static/build", ignore_errors=True)
shutil.move("src/video-sharing-ui/build", "src/zoomto/static/build")

print("Done")