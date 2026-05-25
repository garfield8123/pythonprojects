# Custom chatbot

## Install Model
hugging face
```shell 
curl -LsSf https://hf.co/cli/install.sh | bash
hf download distilbert/distilbert-base-cased-distilled-squad
```

Git clone
```shell
git clone https://huggingface.co/distilbert/distilbert-base-cased-distilled-squad
git lfs pull
```

## Install Virtual Environment
**Note:** Works only with python 3.11
```shell
sudo apt-get install python3.11 python3.11-venv
python3.11 -m venv 3.911venv
source 3.911venv/bin/activate
pip install -r requirements.txt
```

## Install git lfs
```shell
sudo apt-get install git-lfs
```