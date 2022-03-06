import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    db_conn = psycopg2.connect(host=os.environ['db_host'], database=os.environ['db_name'], user=os.environ['db_user'], password=os.environ['db_pw'])

    try:
        cursor = db_conn.cursor()
        cursor.execute('SELECT message,subject FROM public.notification WHERE id=%s',[notification_id])
        notification = cursor.fetchall()
        #cursor.execute("SELECT subject FROM public.notification WHERE id="+notification_id)
        #subject = cursor.fetchall()

        logging.info('notification: %s ', notification)

        # TODO: Get notification message and subject from database using the notification_id

        cursor.execute('SELECT email,first_name FROM public.attendee')
        attendees = cursor.fetchall()
        # TODO: Get attendees email and name

        for attendee in attendees:
            logging.info('attendee: %s ', attendee)
            subject = '{}: {}'.format(attendee[1], notification[0][1])
            send_email(attendee[0], subject, notification[0][0])
        # TODO: Loop through each attendee and send an email with a personalized subject

        status = 'Notified {} attendees'.format(len(attendees))
        #sql_statement = 'UPDATE public.notification SET completed_date=\'{}\' WHERE id={}'.format(datetime.utcnow(), notification_id)
        #cursor.execute(sql_statement)
        #sql_statement = 'UPDATE public.notification SET status=\'{}\', completed_date=\'{}\' WHERE id={}'.format(status, datetime.utcnow(), notification_id)
        cursor.execute("UPDATE public.notification SET status=(%s), completed_date=(%s)"
                       " WHERE id = (%s)", 
                       (status, datetime.utcnow(), notification_id,))
        db_conn.commit()
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if (db_conn):
                cursor.close()
                db_conn.close()

def send_email(email, subject, body):
    logging.info('send mail: %s  %s  %s', email, subject, body)
    if os.environ['sg_api_key'] != "":
        message = Mail(
            from_email=os.environ['sg_email'],
            to_emails=os.environ['sg_email'],#email,
            subject=subject,
            plain_text_content=body)

        sg = SendGridAPIClient(os.environ['sg_api_key'])
        response = sg.send(message)
        logging.info('response: %s', response.status_code)