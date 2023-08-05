import requests
import os
import re
import zipfile
import io
from .utils import walkpath

PATH_CHECK=[
    r'^assets(\.extra|)\/',
    r'^variables\/(variables\.(index$|data-\d{5}-of-\d{5})$|$)',
    r'^saved_model\.pb$'
]

def model_upload(
    url:str="",
    model_uid:str="",
    model_key:str="",
    file=None)->None:
    """model_upload

    Upload your model to server. You can get your model_uid and model_key from server Model Center.\n
    Get upload url by doc, or default read environment "MODEL_UPLOAD_URL" if you are using the jupyter notebook.
    """
    url=url or os.environ.get("MODEL_UPLOAD_URL")
    print("Model Uploading!")
    r=requests.post(url,data={
        "ModelUID":model_uid,
        "ModelKey":model_key,
    },files={
        "model":file
    })
    r=r.json()
    if r.get("code")==0:
        print("Model Upload Success! Detail: "+r.get("message",""))
    else:
        print("Model Upload Error: "+r.get("message",""))

def model_upload_zip(model_uid:str,model_key:str,file_path:str,**kwargs):
    """model_upload_zip

    args:model_uid,model_key,file_path,[url]
    Upload your model to server. You can get your model_uid and model_key from server Model Center.\n
    Get upload url by doc, or default read environment "MODEL_UPLOAD_URL" if you are using the jupyter notebook.\n
    Make sure the the file_path point to a model zip file.
    """
    print("Model Checking!")
    if not zipfile.is_zipfile(file_path):
        raise Exception("please check if it is a zip file!")
    if os.path.getsize(file_path)/1024/1024>32:
        raise Exception("you can't upload file more than 32mb!")
    with zipfile.ZipFile(file_path) as zf:
        for p in zf.namelist():
            if not check_path(p):
                raise Exception("zip file not accordance with specification: "+p)
    with open(file_path,"rb") as f:
        model_upload(model_uid=model_uid,model_key=model_key,file=f,**kwargs)

def model_upload_dir(model_uid:str,model_key:str,dir_path:str,**kwargs):
    """model_upload_dir

    args:model_uid,model_key,dir_path,[url]
    Upload your model to server. You can get your model_uid and model_key from server Model Center.\n
    Get upload url by doc, or default read environment "MODEL_UPLOAD_URL" if you are using the jupyter notebook.\n
    Make sure the the dir_path point to a model dir.
    """
    print("Model Checking!")
    for i in walkpath(dir_path):
        if not check_path(i):
            raise Exception("file not accordance with specification: "+i)
    zipData=io.BytesIO()
    with zipfile.ZipFile(zipData,mode="w") as zf:
        for i in walkpath(dir_path):
            zf.write(os.path.abspath(os.path.join(dir_path,i)),arcname=i,compress_type=zipfile.ZIP_DEFLATED)
    if zipData.tell()/1024/1024>32:
        raise Exception("After zipped but those files also bigger than 32mb!")
    zipData.seek(0,0)
    model_upload(model_uid=model_uid,model_key=model_key,file=zipData.getvalue(),**kwargs)
    

def check_path(path:str)->bool:
    for i in PATH_CHECK:
        if re.match(i,path)!=None:
            return True
    return False
