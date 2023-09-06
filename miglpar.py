#!/usr/bin/python
#
# DESC: Sript mover una LPAR de un sistema a otro conservando el equema de conexiones a FC y los IDs
# FECHA: 29-11-2017
#

import argparse
import subprocess
import command

def byte_to_str(msg):
  return str(msg)[1:0]


ARG = argparse.ArgumentParser(description='Moves LPAR from one IBM POWER system to other')  # declare parse Function

ARG.add_argument('--system','-s',default="",help="Source POWER System")
ARG.add_argument('--destino','-d',default="",help="Target POWER System")
ARG.add_argument('--lpar','-l',default="",help="lpar name to be moved")
ARG.add_argument('--lparid','-i',default="NONE",help="new LPAR id after being moved. Default is to maintaing id")
ARG.add_argument('--hmc','-H',default="",help="HMC used to move the LPAR")
ARG.add_argument('--fcadapter','-f',default='NONE',help="physical FC adapters used by virtual FC adapters. Default is same as original system" )
ARG.add_argument('--red','-r',default='10.0.0',help="Network used by mover partitions")
ARG.add_argument('--remoteHMC','-R',default='NONE',help="IP or name of remote HMC")
ARG.add_argument('--preview','-p',default='yes',help="Performs migration if preview values is \'no\' ")
options=ARG.parse_args()


HMC=options.hmc
SSH="ssh -l hscroot " +HMC
CEC=options.system
CEC_TGT=options.destino
lpar_name=options.lpar
new_lpar_id=options.lparid
list_fc=options.fcadapter
red_msp=options.red
PREVIEW=options.preview.upper()
remote_hmc=options.remoteHMC


if (remote_hmc=="NONE"):
   IP=""
else:
   IP="--ip "+remote_hmc

# Obtenemos el ID de la LPAR

CMD=SSH+" lssyscfg -m "+CEC+" -r lpar --filter \"lpar_names="+lpar_name+"\" -F lpar_id"
LPAR_ID=str(int(subprocess.check_output (CMD,shell=True)))
if ( LPAR_ID.find("result") > 0 ):
   print ("LPAR " + lpar_name + " does not exist in " + CEC)
   exit ()
else:
   ID=int(LPAR_ID)
if new_lpar_id != "NONE":
   ID=int (new_lpar_id)
#
# Obtenemos el nombre del perfil activo
CMD=SSH+" lssyscfg -m "+CEC+" -r lpar --filter \"lpar_names="+lpar_name+"\" -F curr_profile"
PROFILE=subprocess.check_output (CMD,shell=True)
PROFILE=PROFILE.split()[0]


# Obtenemos  el MSP de ORIGEN
CMD=SSH+" lssyscfg -m "+CEC+" -r lpar -F name,lpar_env|grep vio|tail -1|cut -d, -f 1|tail -1"
SRC_MSP=subprocess.check_output (CMD,shell=True)
SRC_MSP=str(SRC_MSP.split()[0]).replace('\'','')[1:]
CMD=SSH+" lssyscfg -m "+CEC+" -r lpar -F lpar_id,lpar_env|grep vio|tail -1|cut -d, -f 1|tail -1"
SRC_MSPID=subprocess.check_output (CMD,shell=True)
SRC_MSPID=str(SRC_MSPID.split()[0])[1:].replace('\'','')

CMD=SSH+" viosvrcmd -m "+CEC+" -p "+str(SRC_MSP)+" -c \\\'lstcpip -num\\\'|grep "+red_msp+"|awk '{print $4}'"
SRC_MSPIP=subprocess.check_output (CMD,shell=True)
SRC_MSPIP=str(SRC_MSPIP.split()[0]).replace('\'','')[1:]

print ("El MSP de origen es "+SRC_MSP+" con ID="+SRC_MSPID+" y direccion IP="+SRC_MSPIP)

# Obtenemos  el MSP de destino
CMD=SSH+" lssyscfg -m "+CEC_TGT+" -r lpar -F name,lpar_env|grep vio|tail -1|cut -d, -f 1|tail -1"
DEST_MSP=subprocess.check_output (CMD,shell=True)
DEST_MSP=str(DEST_MSP.split()[0]).replace('\'','')[1:]
CMD=SSH+" lssyscfg -m "+CEC_TGT+" -r lpar -F lpar_id,lpar_env|grep vio|tail -1|cut -d, -f 1|tail -1"
#subprocess.call (CMD,shell=True)
DEST_MSPID_CMD=subprocess.check_output (CMD,shell=True)
DEST_MSPID=str(int(DEST_MSPID_CMD.split()[0])).replace('\'','')
#SRC_MSPIP=SRC_MSPIP.split()[0]
CMD=SSH+" viosvrcmd -m "+CEC_TGT+" -p "+str(DEST_MSP)+" -c \\\'lstcpip -num\\\'|grep "+red_msp+"|awk '{print $4}'"
#subprocess.call (CMD,shell=True)
DEST_MSPIP=subprocess.check_output (CMD,shell=True)
#print DEST_MSPIP
DEST_MSPIP=str(DEST_MSPIP.split()[0]).replace('\'','')[1:]

print ("El MSP de destino es "+DEST_MSP+" con ID="+DEST_MSPID+" y direccion IP="+DEST_MSPIP)
# Obtenemos los adaptadores FiberChannel
CMD=SSH+" lssyscfg -m "+CEC+" -r prof -F virtual_fc_adapters --filter profile_names="+str(PROFILE)[1:]
p=subprocess.Popen (CMD,shell=True,stdout=subprocess.PIPE)
LPARDATA=p.communicate()[0]
FCDATA=str(LPARDATA)[1:].split('\",\"')
VFCMAP=""
if ( not(len(FCDATA)==len(list_fc.split(","))) and (list_fc!="NONE")):
   print ("Numero de adaptadores FC incorrecto: " + str (len(list_fc.split(',')))+"!="+str (len(FCDATA)))
   quit()
for cont in range (0,len(FCDATA)):
 CMD=SSH+" viosvrcmd -m "+CEC+" -p "+FCDATA[cont].split('/')[3]+" -c \\\"lsmap -npiv -all -fmt , -field physloc name fc clntid vfcclientdrc\\\"|grep C"+FCDATA[cont].split('/')[4]
 p=subprocess.Popen (CMD,shell=True,stdout=subprocess.PIPE)
 FCS=str(p.communicate()[0])[1:]
 if ( list_fc=="NONE" ): 
   FC=FCS.split(',')[3]
   VIO=FCDATA[cont].split('/')[2]
 else:
   FC=(list_fc.split(',')[cont]).split(':')[1]
   VIO=(list_fc.split(',')[cont]).split(':')[0]
 SLOT=FCDATA[cont].split('/')[4].replace("\'","")
 CMD=SSH+" \"lssyscfg -m  "+CEC_TGT+" -r prof -Fmax_virtual_slots --filter \"lpar_ids="+VIO+"\"\"|head -1"
 p=subprocess.Popen (CMD,shell=True,stdout=subprocess.PIPE)
 MAX_SLOT=str(p.communicate()[0])[2:].split('\\n')[0]
 if int(SLOT) > int(MAX_SLOT):
    SLOT=str(ID).replace('\'','')
 VFCMAP=VFCMAP+","+FCDATA[cont].split('/')[0].replace("\"","")+"//"+VIO+"/"+SLOT+"/"+FC
VFCMAP=VFCMAP[2:]
DEST_MSP=DEST_MSP.replace('\'','')
DEST_MSPID=DEST_MSPID.replace('\'','')
SRC_MSP=SRC_MSP.replace('\'','')
SRC_MSPID=SRC_MSPID.replace('\'','')


# VALIDAMOS la migracion de la LPAR
print ("Validating migration\n")
CMD=SSH+"  \"migrlpar "+IP+" -o v -m "+CEC+" -t "+CEC_TGT+" -p "+lpar_name+" --vlanbridge 1 --uuid 1  -i \\\"\\\\\\\"virtual_fc_mappings="+VFCMAP+"\\\\\\\",dest_lpar_id="+str(ID)+",source_msps="+SRC_MSP+"/"+SRC_MSPID+"/"+SRC_MSPIP+",dest_msps="+DEST_MSP+"/"+DEST_MSPID+"/"+DEST_MSPIP+",dest_msp_id=1"+DEST_MSPID+",source_msp_id="+SRC_MSPID+"\\\"\""
subprocess.call (CMD,shell=True)
CMD=SSH+"  \"migrlpar "+IP+" -o m -m "+CEC+" -t "+CEC_TGT+" -p "+lpar_name+" --vlanbridge 1 --uuid 1  -i \\\"\\\\\\\"virtual_fc_mappings="+VFCMAP+"\\\\\\\",dest_lpar_id="+str(ID)+",source_msps="+SRC_MSP+"/"+SRC_MSPID+"/"+SRC_MSPIP+",dest_msps="+DEST_MSP+"/"+DEST_MSPID+"/"+DEST_MSPIP+",dest_msp_id=1"+DEST_MSPID+",source_msp_id="+SRC_MSPID+"\\\"\""
print ("\n Command to execute: ")
print (CMD)
if (PREVIEW=='NO'):
   # Ejecutamos la migracion de la LPAR
   print ("\nMoving LPAR "+lpar_name+" to "+CEC_TGT+"\n")
   subprocess.call (CMD,shell=True)
else:
   print ("\nPreview operation.Migration of LPAR "+lpar_name+" not performed")
