import subprocess
import re
import logging
from time import sleep
from datetime import datetime

from mail.send_mail import send_email_with_attachment


def run():
    while True:
        docker_cont = "in_support_1c"
        proc = subprocess.Popen([f"docker logs {docker_cont}"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        res = err.decode("utf-8")
        rewriting = ''
        with open("/home/makosov/bots/read_docker_logs/logs.txt", 'r') as fr:
            txt_file = fr.read()
            if len(txt_file) != len(res):
                rewriting = res
            if len(txt_file.split()) < len(res.split()):
                txt_for_parsing = res.replace(txt_file, "")
                if re.search('error', txt_for_parsing, re.IGNORECASE) or re.search('ошибка', txt_for_parsing,
                                                                                   re.IGNORECASE):
                    info_mail = send_email_with_attachment(e_mail="support@ininsys.ru",
                                                           firma="ИИС",
                                                           cont_telefon="+ 7 (495) 640 4074",
                                                           description=txt_for_parsing,
                                                           full_name="служба 'read_docker_logs.service' на сервере с Ботом",
                                                           priority="Высокий")
                    if info_mail:
                        logging.error(datetime.now(), "Ошибка SMTP, сообщения не отправляются ")

        if rewriting:
            with open("/home/makosov/bots/read_docker_logs/logs.txt", 'w') as fw:
                fw.write(rewriting)
        sleep(300)


if __name__ == '__main__':
    open("/home/makosov/bots/read_docker_logs/logs.txt", 'a').close()
    print("MAIN")
    run()
