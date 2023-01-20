import random
import json
import requests
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse


app = FastAPI()
with open("config.json") as config:
    conf = json.load(config)

def get_image_list_from_github_repo(owner: str ,repo: str, path: str):
    repo_dirs_resp = requests.get(f'https://api.github.com/repos/{owner}/{repo}/contents/')
    if repo_dirs_resp.status_code == 200:
        for dir_info in repo_dirs_resp.json():
            if dir_info["type"] == "dir" and dir_info["path"] == path:
                dir_git_url = dir_info["git_url"]

                cache_dir_info_resp = requests.get(dir_git_url)
                cache_image_results = []
                if cache_dir_info_resp.status_code == 200:
                    for file_info in cache_dir_info_resp.json():
                        if file_info["type"] == "blob":
                            cache_image_results.append(f'https://cdn.jsdelivr.net/gh/{owner}/{repo}@raw/main/{[path]}/{file_info["path"]}')
    return cache_image_results
    
def get_image_list_from_seewo(cache_path: str):
    image_url_list = []
    with open(cache_path) as seewo_cache_f:
        seewo_cache = json.load(seewo_cache_f)
        for img_path in seewo_cache:
            image_url_list.append(seewo_cache[img_path])

    return image_url_list

def walk(path: str):
    file_list = []
    for root, dirs, files in os.walk(path, topdown=False):
        for file_name in files:
            if os.path.splitext(file_name)[1] in [".png", ".jpg", ".jpeg"]:
                file_list.append(os.path.join(root, file_name))
        for dir_name in dirs:
            file_list.extend(walk(os.path.join(root, dir_name)))
    return file_list

def get_image_list_from_local_disk(file_list: list):
    url_list = []
    for file in file_list:
        url_list.append("https://cf-cdn.img.z0z0r4.top/{img_path}".format(img_path=file.replace("\\", "/")))
    return url_list

@app.get("/")
async def root():
    return {"message": "这里是为 Xinger 的涩图准备的 API", "connect": {"QQ": "3531890582", "email": "z0z0r4@outlook.com"}, "warning": "谁创谁死妈"}

# app.mount("/cache", StaticFiles(directory="cache"), name="cache")

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse("https://xinger.vip/wp-content/themes/H-Siren/images/favicon.ico")

@app.get("/image")
async def image(type: str = None):
    global img_url_list

    if len(img_url_list) != 0:
        img_url = random.choice(img_url_list)
        if type is None:
            return RedirectResponse(img_url)
        elif type == "json":
            return {"url": img_url}
    return {"message": "暂时还没有图片"}

# @app.get("/image/{hash}")
# async def image_hash(hash: str):
#     return FileResponse(path=os.path.join(conf["img_cache_folder"], f'{hash}.png'), media_type="image/png")

if __name__ == "__main__":
    if not os.path.exists(conf["img_cache_folder"]):
        os.makedirs(conf["img_cache_folder"])

    # from format_img import walk
    # walk(conf["format_img_folder"])
  
    # img_url_list = get_image_list_from_local_disk(walk(conf["img_cache_folder"]))
    img_url_list = get_image_list_from_seewo("seewo_cache.json")

    host, port = conf["api_host"], conf["api_port"]
    uvicorn.run(app, host=host, port=port)
