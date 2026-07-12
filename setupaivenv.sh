sudo apt-get install python3.11 python3.11-venv
python3.11 -m venv aivenv
source aivenv/bin/activate
pip install -r airequirements.txt
cd localimagebot
./installmodel.sh
