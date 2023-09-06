# power10tools
python tools to manage IBM power systems
this project includes several scripts written using python to manage IBM power systems
#### miglpar.py
this script performs a Live Partition movility to migrate a LPAR from one system to other. 

***
python3 ./miglpar.py -h
usage: miglpar.py [-h] [--system SYSTEM] [--destino DESTINO] [--lpar LPAR] [--lparid LPARID] [--hmc HMC] [--fcadapter FCADAPTER]
                  [--red RED] [--preview PREVIEW]

Moves LPAR from one IBM POWER system to other

optional arguments:
  -h, --help            show this help message and exit
  --system SYSTEM, -s SYSTEM
                        Source POWER System
  --destino DESTINO, -d DESTINO
                        Target POWER System
  --lpar LPAR, -l LPAR  lpar name to be moved
  --lparid LPARID, -i LPARID
                        new LPAR id after being moved. Default is to maintaing id
  --hmc HMC, -H HMC     HMC used to move the LPAR
  --fcadapter FCADAPTER, -f FCADAPTER
                        physical FC adapters used by virtual FC adapters. Default is same as original system
  --red RED, -r RED     Network used by mover partitions
  --preview PREVIEW, -p PREVIEW
                        Performs migration if preview values is 'no|NO|No|nO'

***
-> physical FC adapter are specified as a list like "adap#:vio#,adap#:vio#" where adap is the adapter name (i.e. fcs0) and vio# is the id from the vio where the adapter resides.
-> At this version, remote lpar migration is not supported
