import random
import string
from typing import Optional

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models

from core.config import settings


class SMSService:
    """
    阿里云短信服务类
    """

    def __init__(self):
        """
        初始化短信服务客户端
        """
        if settings.ALIYUN_ACCESS_KEY_ID_SMS and settings.ALIYUN_ACCESS_KEY_SECRET_SMS:
            config = open_api_models.Config(
                access_key_id=settings.ALIYUN_ACCESS_KEY_ID_SMS,
                access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET_SMS
            )
            # 短信API产品域名（接口地址固定，无需修改）
            config.endpoint = f'dysmsapi.aliyuncs.com'
            self.client = Dysmsapi20170525Client(config)
        else:
            self.client = None

    def send_verification_code(self, phone_number: str, code: Optional[str] = None) -> bool:
        """
        发送短信验证码

        Args:
            phone_number: 接收短信的手机号
            code: 验证码，如果不提供则自动生成6位数字验证码

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        if not self.client:
            print("阿里云短信服务未配置")
            return False

        # 如果没有提供验证码，则生成一个6位随机数字验证码
        if not code:
            code = ''.join(random.choices(string.digits, k=6))

        # 创建短信发送请求
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone_number,
            sign_name='杭州翱锐医学检验实验室',  # 这里需要替换为你在阿里云配置的短信签名
            template_code=settings.SMS_TEMPLATE_CODE,
            template_param=f'{{"code":"{code}"}}'
        )

        # 创建运行时选项
        runtime = util_models.RuntimeOptions()

        try:
            # 发送短信
            response = self.client.send_sms_with_options(send_sms_request, runtime)
            print(f"短信发送结果: {response.body}")
            
            # 判断发送是否成功
            if response.body.code == 'OK':
                return True
            else:
                print(f"短信发送失败: {response.body.message}")
                return False
        except Exception as error:
            print(f"短信发送异常: {error}")
            return False

    def generate_verification_code(self, length: int = 6) -> str:
        """
        生成指定长度的数字验证码

        Args:
            length: 验证码长度，默认为6

        Returns:
            str: 生成的验证码
        """
        return ''.join(random.choices(string.digits, k=length))


# 全局实例
sms_service = SMSService()