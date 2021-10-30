
import time
import re
import chardet
import sys
import codecs
import argparse

# Script's Info
__author__ = "Vinicius Dias"
__date__ = 20210622
__description__ = "Script used to parse logs from hikvision DVRs"


ASSINATURA_HIK="532c000000000000000000000000000048494b564953494f4e4048414e475a484f55"
systemlog_types = {
  1 : "Alarm",
  2 : "Exception",
  3 : "Operation",
  4 : "Information",
}

#Descobrir o disco físico
#TODO!

def main (file_path: str):
    #Abrir o disco físico como arquivo
    try:
        #arquivo = open(r'\\.\PHYSICALDRIVE5', 'rb')
        arquivo = open(file_path, 'rb')
    except:
        print("Não consegui abrir o arquivo!")
        exit()

    # Seek no arquivo para o inicio do master sector, aonde fica a assinatura (0x210 ou 528 decimal)
    arquivo.seek(512, 0)

    #Lendo informacoes a partir do 528

    #Certificando que a assinatura eh de um hikvision, senao sai do programa
    assinatura_disco = arquivo.read(34).hex()

    if ASSINATURA_HIK == assinatura_disco:
        #pegando a capacidade do disco rígido gravado internamente pela hikvision
        arquivo.seek(584, 0)
        capacidade_disco = int.from_bytes(arquivo.read(8), byteorder='little')
        capacidade_disco_giga = round(((capacidade_disco/1024)/1024)/1024, 2)
        
        #pegando o offset e o tamanho dos logs
        arquivo.seek(608, 0)
        offset_logs = int.from_bytes(arquivo.read(8), byteorder='little')
        #tamanho dos logs
        arquivo.seek(616, 0)
        tamanho_log = int.from_bytes(arquivo.read(8), byteorder='little')

        #Pegando a data de inicialização do sistema
        arquivo.seek(752, 0)
        dataepoch = int.from_bytes(arquivo.read(4), byteorder='little')
        local_time = time.ctime(dataepoch)

        #extraindo os logs para um arquivo
        try:
            #arquivo = open(r'\\.\PHYSICALDRIVE4', 'rb')
            logfile = open("C:\\Users\\vinicius\\Desktop\\logfile_hikvision.txt", 'wb')
        except:
            print("Não consegui abrir o arquivo!")
            exit()
        arquivo.seek(offset_logs, 0)
        logfile.write(arquivo.read(tamanho_log))
        logfile.close()

        #abrindo o arquivo para parseamento dos logs
        parsefile = open(b'C:\\Users\\vinicius\\Desktop\\logfile_hikvision.txt', 'rb')
        #parsefile = open(b'C:\\Users\\vinicius\\Desktop\\Pedaco_rats_2', 'rb')
        log_chunk = parsefile.read()
        log_chunk_limpo = log_chunk.split(b'RATS\x01\x00\x00\x00')
        parsefile.close()
        
        #removendo o primeiro e o ultimo elemento da lista pois estao vazios
        del log_chunk_limpo[0]
        del log_chunk_limpo[len(log_chunk_limpo)-1]
        
        #contador para formar meu dicionario indexado
        counter = 0
        dictlog = {}

        for log in log_chunk_limpo:
            date_log_epoch = int.from_bytes(log[:4], byteorder='little')
            local_time = time.ctime(date_log_epoch)
            tipo_log = int.from_bytes(log[4:6], byteorder='little')
            description = log[6:].replace(b'\x00', b'')
            #print(type(description))
            dictlog[counter] = [local_time,systemlog_types.get(tipo_log),description.decode('ascii','ignore')]
            #print(dictlog.get(counter)[2])
            counter+=1
        
        #Abrindo arquivo para escrita do relatorio final
        relatorio_final = open('C:\\Users\\vinicius\\Desktop\\Relatorio_Final.txt', 'w', encoding='ascii')

        #escrevendo o relatorio
        relatorio_final.write('############# Relatorio dos logs do DVR Hickvision #############\n\n\n')

        for i in dictlog:
            relatorio_final.write('Data: '+dictlog.get(i)[0]+'\n')
            relatorio_final.write('Tipo de Log: '+dictlog.get(i)[1]+'\n')
            relatorio_final.write('Descricao: '+dictlog.get(i)[2]+'\n')
            relatorio_final.write('-----------------------------------\n')
            #print(dictlog.get(i))
        relatorio_final.write('################ FIM DO RELATORIO ###################')
        relatorio_final.close()

    else:
        arquivo.close()
        print("Esse disco não parece um Hikvision, favor verificar!")
        exit() 

    arquivo.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__, epilog='Build by {}. Version {}'.format(__author__, __date__),formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file', help='Evidence file used to parse logs. File format must be dd raw image', type=str, required=True, nargs='*')
    arguments = parser.parse_args()

    main(arguments.file)
