# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest


def send_sms(phone, code):
    client = AcsClient('你的密钥ID', '你的密钥', '你的位置')
    # // 创建API请求并设置参数
    request = SendSmsRequest()
    request.set_SignName("你的签名")
    request.set_TemplateCode('你的模板代码')
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
    result = send_sms('测试手机号', '999888')
    print(result)
