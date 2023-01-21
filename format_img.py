import os
import json
from shutil import copyfile
from PIL import Image
import hashlib
# from sqlalchemy import Column, MetaData, create_engine, Table, Integer, CHAR, insert
# from sqlalchemy.orm import Session
# from sqlalchemy.dialects.mysql import insert

with open("config.json") as config:
    conf = json.load(config)

# # SQL
# engine = create_engine(
#     f'mysql+pymysql://{conf["sql_user"]}:{conf["sql_password"]}@{conf["sql_host"]}:{conf["sql_port"]}/{conf["sql_database"]}?autocommit=1', pool_size=128, max_overflow=32, pool_pre_ping=True, pool_recycle=3600)
# metadata = MetaData(bind=engine)
# # init table
# table = Table("img_info", metadata,
#                                     Column(
#                                         "hash", CHAR(32), primary_key=True),
#                                     Column(
#                                         "width", Integer),
#                                     Column(
#                                         "height", Integer)
# )
                                    
# metadata.create_all()

def GetMD5FromLocalFile(filename):
    """
    Get local file's MD5 Info.
    @param filename:file path & file name
    @return:MD5 Info
    """
    with open(filename, 'rb') as file_object:
        file_content = file_object.read()
        file_md5 = hashlib.md5(file_content)
        return file_md5.hexdigest()

# def sql_replace(sess: Session, table, **kwargs):
#     insert_stmt = insert(table).values(kwargs)
#     on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(**kwargs)
#     sess.execute(on_duplicate_key_stmt)

def format_file(path):
    # img_file = Image.open(path)
    # img_width = img_file.size[0]
    # img_height = img_file.size[1]
    img_format = os.path.splitext(path)[1]
    img_md5 = GetMD5FromLocalFile(path)
    
    # with Session(bind=engine) as sess:
        # sql_replace(sess, table, hash=img_md5, width=img_width, height=img_height)
        # sess.commit()
    if not os.path.exists(os.path.join(conf["img_cache_folder"], f"{img_md5}{img_format}")):
        # if img_format == "jpg":

        copyfile(path, os.path.join(conf["img_cache_folder"], f"{img_md5}{img_format}"))
        # os.remove(path)

        # else:
        #     img = img_file.convert("RGB")
        #     img.save(os.path.join(conf["img_cache_folder"], f"{img_md5}.jpg"), format="JPEG", quality=95)
    print(f"{path} {img_md5} 已缓存")

def walk(path):
    for root, dirs, files in os.walk(path):            
        for file in files:
            if os.path.splitext(file)[1] in (".jpg", ".jpeg", ".png"):
                format_file(os.path.join(root, file))
        for dir in dirs:
            walk(os.path.join(root, dir))
            
if __name__ == "__main__":
    if not os.path.exists(conf["img_cache_folder"]):
        os.makedirs(conf["img_cache_folder"])

    walk(conf["format_img_folder"])
