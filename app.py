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
        with open("logs.txt", 'r') as fr:
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
                                                           full_name="читаю логи Телеграмм Бота ",
                                                           priority="Высокий")
                    if info_mail:
                        logging.error(datetime.now(), "Ошибка SMTP, сообщения не отправляются ")

        if rewriting:
            with open("logs.txt", 'w') as fw:
                fw.write(rewriting)
        sleep(300)


if __name__ == '__main__':
    open("logs.txt", 'a').close()
    run()
