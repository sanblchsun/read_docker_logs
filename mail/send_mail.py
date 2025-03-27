import logging
import mimetypes
import os  # Функции для работы с операционной системой, не зависящие от используемой операционной системы
import smtplib  # Импортируем библиотеку по работе с SMTP
import sys
from configparser import ConfigParser
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from mail.html import get_html


# ----------------------------------------------------------------------
def send_email_with_attachment(e_mail,
                                     firma,
                                     full_name,
                                     cont_telefon,
                                     description,
                                     priority,
                                     number_from_1c=''):
    """
    Send an email with an attachment
    """
    val_error = 0
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "email.ini")

    # get the config
    if os.path.exists(config_path):
        cfg = ConfigParser()
        cfg.read(config_path)
    else:
        print("Config not found! Exiting!")
        sys.exit(1)

    # extract server and from_addr from config
    host = cfg.get("smtp", "server")
    FROM = cfg.get("smtp", "from")
    password = cfg.get("smtp", "passwd")
    to_addrs = cfg.get("smtp", "to_addrs")

    if not to_addrs:
        logging.info("Не указан основной адреса получателей в файле email.ini")
        val_error = 1
        return val_error

    to_addrs0 = to_addrs
    msg_To = f"{to_addrs}"

    # create the message
    msg = MIMEMultipart()
    msg["From"] = FROM
    msg["To"] = msg_To
    msg['Reply-To'] = e_mail
    msg["Subject"] = "Ошибки в работе Телеграмм Бота"
    msg["Date"] = formatdate(localtime=True)


    html = get_html(e_mail, firma, full_name, cont_telefon, description, priority, number_from_1c)

    if html:
        msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP(host)
    except Exception as e:
        logging.info(f"Ошибка при создании сервера SMTP: {e}")
        val_error = 2
        return val_error
    try:
        server.starttls()
        server.login(FROM, password)
        server.sendmail(FROM, to_addrs0, msg.as_string())
    except Exception as e:
        logging.info(f"Ошибка при отправке письма: {e}")
        val_error = 3
    finally:
        server.quit()

    return val_error
    # ==========================================================================================================================


def process_attachement(msg, files):  # Функция по обработке списка, добавляемых к сообщению файлов
    for f in files:
        if os.path.isfile(f):  # Если файл существует
            attach_file(msg, f)  # Добавляем файл к сообщению
        elif os.path.exists(f):  # Если путь не файл и существует, значит - папка
            dir = os.listdir(f)  # Получаем список файлов в папке
            for file in dir:  # Перебираем все файлы и...
                attach_file(msg, f + "/" + file)  # ...добавляем каждый файл к сообщению


def attach_file(msg, filepath):  # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)  # Получаем только имя файла
    ctype, encoding = mimetypes.guess_type(filepath)  # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:  # Если тип файла не определяется
        ctype = 'application/octet-stream'  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип

    with open(filepath, 'rb') as fp:
        file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
        file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
        fp.close()
        encoders.encode_base64(file)  # Содержимое должно кодироваться как Base64

    file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
    msg.attach(file)


if __name__ == '__main__':
    send_email_with_attachment(e_mail='dffdvfd@fd.ru',
                                           firma="ООО kjhdk",
                                           full_name='Иван',
                                           cont_telefon='49834889',
                                           description='Ура!',
                                           priority="Низкий")

