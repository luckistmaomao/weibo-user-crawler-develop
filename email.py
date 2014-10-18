#coding:utf-8

import smtplib
from email.mime.text import MIMEText

#邮件用户列表
mailto_list=['907677421@qq.com']

#设置服务器，用户名、口令以及邮箱的后缀
mail_host="smtp.126.com"
mail_user="yzt112233"
mail_pass="yuzhenting"
mail_postfix="126.com"

def send_mail(to_list,sub,content):
    '''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("aaa@126.com","sub","content")
    '''
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content)
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == '__main__':
    if send_mail(mailto_list,"subject","content"):
        print "发送成功"
    else:
        print "发送失败"
