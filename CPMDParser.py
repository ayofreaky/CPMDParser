import hashlib, glob, requests
from pathlib import Path

def calcSha256(fPath):
    sha256 = hashlib.sha256()
    with open(fPath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

rootDir = Path(input('Checkpoints directory: '))
exts = ['*.pt', '*.safetensors', '*.ckpt']
checkpoints = [f for ext in exts for f in glob.glob(str(rootDir/ext))]

i = 0
for checkpoint in checkpoints:
    i += 1
    chkptExt = Path(checkpoint).suffix
    chkptFname = Path(checkpoint).name
    if (rootDir/chkptFname.replace(chkptExt, '.md')).exists():
        print(f'[{i}/{len(checkpoints)}] [-] Skipping "{chkptFname}" (.md file already exists)')
    else:
        print(f'[{i}/{len(checkpoints)}] [~] Fetching metadata for "{chkptFname}"..')
        sha256 = calcSha256(checkpoint)

        r = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{str(sha256).upper()}').json()
        if len(r) > 1:
            modelId = r['modelId']
            modelName = r['model']['name']
            modelCover = r['images'][0]['url']

            chkptId = r['id']
            chkptName = r['name']
            chkptDesc = r['description']

            baseModel = r['baseModel']
            triggerWords = r['trainedWords']

            r = requests.get(f'https://civitai.com/api/v1/models/{modelId}').json()

            modelDesc = r['description']
            modelCreator = r['creator']['username']
            modelTags = r['tags']

            with open(rootDir/chkptFname.replace(chkptExt, '.md'), 'w') as f:
                f.write(
                    f'# **{modelName}** [{chkptName}]\n![cover]({modelCover})\n\nTags: {", ".join(modelTags)}\n\nTrigger words: {", ".join(triggerWords)}\n\n{modelDesc}\n-----\n{chkptDesc}\n\nUploaded by: {modelCreator}\n\nURL: https://civitai.com/models/{modelId}'
                )

            with open(rootDir/chkptFname.replace(chkptExt, '.png'), 'wb') as f:
                f.write(requests.get(modelCover).content)

            print(f'[{i}/{len(checkpoints)}] [+] Metadata for "{chkptFname}" was saved as "{chkptFname.replace(chkptExt, ".md")}"')
        else:
            print(f'[{i}/{len(checkpoints)}] [-] Skipping "{chkptFname}" (unable to find any model matching the specified sha256 hash: {sha256})')