import os
import json
import asyncio
import httpx
from sqlalchemy import Column, MetaData, create_engine, Table, Integer, CHAR, insert, func, distinct
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
import time
import hashlib

with open("config.json") as config:
    conf = json.load(config)

# SQL
engine = create_engine(
    f'mysql+pymysql://{conf["sql_user"]}:{conf["sql_password"]}@{conf["sql_host"]}:{conf["sql_port"]}/{conf["sql_database"]}?autocommit=1', pool_size=128, max_overflow=32, pool_pre_ping=True, pool_recycle=3600)
metadata = MetaData(bind=engine)
# init table
table = Table("img_info", metadata,
                                    Column(
                                        "image_url", CHAR(74), primary_key=True),
                                    Column(
                                        "image_width", Integer),
                                    Column(
                                        "image_height", Integer))
                                    
metadata.create_all()

bili_csrf = conf["bili_csrf"]
bili_sessdata = conf["bili_sessdata"]

def sql_replace(sess: Session, table, **kwargs):
    insert_stmt = insert(table).values(kwargs)
    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(**kwargs)
    sess.execute(on_duplicate_key_stmt)

def CalcSha1(filepath):
    with open(filepath,'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
        return hash

async def upload_file(path: str, semaphore: asyncio.Semaphore):
    with Session(bind=engine) as sess:
        image_sha1 = CalcSha1(path)
        image_extensions = os.path.splitext(path)[1]
        if (check_img := sess.query(table.c.image_url).filter(table.c.image_url == f'http://i0.hdslb.com/bfs/album/{image_sha1}.{image_extensions[1:]}').first()) is None:
            
            async with semaphore:
                with open(path, "rb") as file:
                    async with httpx.AsyncClient(timeout=60) as session:
                        body = {"biz": "new_byn", "category": "daily", "csrf": bili_csrf}
                        
                        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54", "cookie": f"SESSDATA={bili_sessdata}"}
                        resp = await session.post("https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs", data=body, headers=headers, files={"file_up": file})
                        if resp.status_code == 200:
                            resp_json = resp.json()
                            if resp_json["code"] == 0:
                                resp_json = resp_json["data"]
                                sql_replace(sess, table, image_url=resp_json["image_url"], image_width=resp_json["image_width"], image_height=resp_json["image_height"])
                                sess.commit()
                                print(f'Success upload {path} {resp_json["image_url"]}')
                        elif resp.status_code == 412:
                            print(f'412 response status_code {path}')
                        return 1
        else:
            print(f"{path} {check_img[0]} already exists")
            return 0


def walk(path):
    image_paths = []
    for root, dirs, files in os.walk(path):            
        for file in files:
            if os.path.splitext(file)[1] in (".jpg", ".jpge", ".png"):
                image_paths.append(os.path.join(root, file))
        for dir in dirs:
            walk(os.path.join(root, dir))

    return image_paths

async def main():
    if not os.path.exists(conf["img_cache_folder"]):
        os.makedirs(conf["img_cache_folder"])

    image_paths = walk(conf["format_img_folder"])
    
    semaphore = asyncio.Semaphore(4)
    # await asyncio.gather(*[upload_file(path, semaphore) for path in image_paths]) 412
    for path in image_paths:
        return_code = await upload_file(path, semaphore) # 1 success 0 already exists
        if return_code == 1:
            time.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
