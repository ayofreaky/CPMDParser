import hashlib, requests, os, glob
from pathlib import Path

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'authority': 'civitai.com'}

def computeSha256(fName):
    hashSha256 = hashlib.sha256()
    with open(fName, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashSha256.update(chunk)
    return hashSha256.hexdigest()

rootDir = input('Root path for LoRA checkpoints: ')
exts = ['*.pt', '*.safetensors', '*.ckpt']
checkpoints = [f for ext in exts for f in glob.glob(os.path.join(rootDir, ext))]

i = 0
for checkpoint in checkpoints:
    i += 1
    chkptExt = os.path.splitext(checkpoint)[1]
    chkptFname = os.path.basename(checkpoint)
    if os.path.exists(checkpoint.replace(chkptExt, '.txt')) or os.path.exists(checkpoint.replace(chkptExt, '.md')):
        print(f'[{i}/{len(checkpoints)}] Skipping "{chkptFname}" (metadata file already exists)')
    else:
        print(f'[{i}/{len(checkpoints)}] Fetching metadata for "{chkptFname}"..')# fName = Path(checkpoint).stem # no extension
        sha256hash = computeSha256(Path(checkpoint))

        r = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{str(sha256hash).upper()}', headers=headers).json()
        if len(r) > 1:
            modelId = r['modelId']
            modelName = r['model']['name']
            modelCover = r['images'][0]['url']

            chkptId = r['id']
            chkptName = r['name']
            chkptDesc = r['description']

            baseModel = r['baseModel']
            triggerWords = r['trainedWords']

            r = requests.get(f'https://civitai.com/api/v1/models/{modelId}', headers=headers).json()

            modelDesc = r['description']
            modelCreator = r['creator']['username']
            modelTags = r['tags']

            with open(checkpoint.replace(chkptExt, '.md'), 'w') as f:
                f.write(f'# **{modelName}** [{chkptName}]\n![cover]({modelCover})\n\nTags: {", ".join(modelTags)}\n\nTrigger words: {", ".join(triggerWords)}\n\n{modelDesc}\n-----\n{chkptDesc}\n\nUploaded by: {modelCreator}\nURL: https://civitai.com/models/{modelId}')
            
            with open(checkpoint.replace(chkptExt, '.png'), 'wb') as f:
                f.write(requests.get(modelCover, headers=headers).content)

            print(f'[{i}/{len(checkpoints)}] Metadata for "{chkptFname}" was saved as "{chkptFname.replace(chkptExt, ".md")}"\n')

        else:
            print(f'[{i}/{len(checkpoints)}] Skipping "{chkptFname}" (no model found with sha256: {sha256hash})')