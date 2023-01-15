
import requests
import time
import os
import json

config_path = "seewo_config.json"
cache_path = "seewo_cache.json"

# config.json
def _init():
    if not os.path.exists(config_path):
        with open(config_path, "w") as config:
            json.dump({
                "accessToken": "",
                "connect_magick": "",
                "x_csrf_token": "",
                "upload_type": "tencent",
                "img_folder": ""}, config
            )
        print("请修改 config.json")
        return None

    with open(config_path) as config:
        try:
            config_json = json.load(config)
            for conf in config_json:
                if config_json[conf] == "":
                    print(f'config.json 中 {conf} 不能为空')
                    return None
            else:
                return config_json
        except:
            return None

# # 上传图片的对象存储策略 tencent 或 qiniu
# upload_type = "tencent"

# # 打开 F12 获取 Cookie
# accessToken = ""
# connect_magick = ""

# # x_csrf_token 为 F12 从 Network 中任意 https://care.seewo.com/app/apis.json 请求的 Headers 中获取
# x_csrf_token = ""

# 获取鉴权 token
def get_token_from_seewo(accessToken: str ,connect_magick: str, x_csrf_token: str):
    headers = {"Cookie": f"accessToken={accessToken}; connect.magick={connect_magick}",
               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54",
               "x-csrf-token": x_csrf_token}
    res = requests.post(url=f'https://care.seewo.com/app/apis.json?action=UPLOAD_GET_TOKEN_V3&timestamp={time.time()}&isAjax=1',
                        headers=headers, json={"action": "UPLOAD_GET_TOKEN_V3", "params": {"originKey": "easicare-web"}})
    if res.status_code == 200:
        return res.json()

# 上传图片
def upload_img(config: dict, path: str):
    accessToken = config["accessToken"]
    connect_magick = config["connect_magick"]
    x_csrf_token = config["x_csrf_token"]
    upload_type = config["upload_type"]

    upload_info = get_token_from_seewo(accessToken=accessToken, connect_magick=connect_magick, x_csrf_token=x_csrf_token)
    if upload_info is not None:
        if upload_info["code"] == 200 and upload_info["success"] == True:
            policy_list = upload_info["data"]["policyList"]
            for policy in policy_list:
                if policy["type"] == upload_type:
                    with open(path, "rb") as f:
                        form_fields = {}
                        for form in policy["formFields"]:
                            form_fields[form["key"]] = form["value"]
                        headers = {"Referer": "https://care.seewo.com/"}

                        if path.endswith(".jpg"):
                            img_content_type = "image/jpeg"
                        elif path.endswith(".png"):
                            img_content_type = "image/png"
                        else:
                            return None  # 不支持的图片格式

                        files = {
                            'filename': path,
                            'Content-Disposition': 'form-data;',
                            'Content-Type': img_content_type,
                            'file': (path, f, img_content_type)
                        }

                        upload_img_res = requests.post(
                            url=policy["uploadUrl"], data=form_fields, files=files, headers=headers)

                        # 验证上传是否成功
                        if upload_img_res.status_code == 200:
                            upload_img_res_json = upload_img_res.json()
                            return upload_img_res_json
                        else:
                            return upload_img_res.text

# 遍历目录包括子目录
def walk(path):
    image_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] in (".jpg", ".jpge", ".png"):
                image_paths.append(os.path.join(root, file))
        for dir in dirs:
            walk(os.path.join(root, dir))

    return image_paths


if __name__ == "__main__":
    config = _init()
    if config is None: # 判断 config 加载是否成功
        os.system("pause")
        exit()

    with open(cache_path, "w") as cache:
        cache_info = {}
        walk_result = walk(config["img_folder"])
        if len(walk_result) > 0:
            for img_path in walk_result:
                upload_info = upload_img(config, img_path)
                # 验证上传是否成功
                if upload_info["code"] == 0 and upload_info["message"] == "Ok":
                    cache_info[img_path] = upload_info["data"]["downloadUrl"]
                    print(f'{img_path} -> {upload_info["data"]["downloadUrl"]}')
            # 保存到 cache.json
            json.dump(cache_info, cache)
            print(f'已保存到 {cache_path}')
        else:
            print("当前目录下没有文件")
    os.system("pause")