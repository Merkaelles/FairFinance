# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest


def send_sms(phone, code):
    client = AcsClient('LTAI5tSpJZbucii7yKrS613b', 'xduX9iChJLyb9vXNHQFKNW0egAC1b2', 'cn-shanghai')
    # // 创建API请求并设置参数
    request = SendSmsRequest()
    request.set_SignName("mallmell")
    request.set_TemplateCode('SMS_465600208')
    params = "{\"code\":\"" + str(code) + "\"}"  # 发送的手机验证码格式
    request.set_TemplateParam(params)
    request.set_PhoneNumbers(str(phone))

    try:
        response = client.do_action_with_exception(request)
        response_x = str(response, encoding='utf-8')
        return response_x
    except ServerException as e:
        return e


if __name__ == '__main__':
    result = send_sms('18521021706', '999888')
    print(result)
