from flask import make_response, session
from flask_mail import Message, Mail
import random
import string
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageFilter

from . import mail

#验证码类
class ImageCode():
    #生成随机颜色
    def __randomColor(self):
        return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

    #随机划线
    def __drawLine(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=1)
    
    #生成验证码图片
    def __getVerifyCode(self):
        code = generateCode()
        width, height = 120, 50
        image = Image.new('RGB', (width, height), 'white')
        font = ImageFont.truetype('app/static/arial.ttf', 40)
        draw = ImageDraw.Draw(image)

        for item in range(4):
            draw.text((5+random.randint(-3,3)+23*item, 5+random.randint(-3,3)),
                  text=code[item], fill=self.__randomColor(), font=font)
        
        self.__drawLine(draw, 2, width, height)
        image = image.filter(ImageFilter.GaussianBlur(radius=1.5))
        return image, code

    #生成向前端的反馈
    def getImageCode(self):
        image, code = self.__getVerifyCode()
        buffer = BytesIO()
        image.save(buffer, 'jpeg')
        bufferStr = buffer.getvalue()
        response = make_response(bufferStr)
        response.headers['Content-Type'] = 'image/gif'
        session['imageCode'] = code
        return response

#生成随机字母数字
def generateCode():
    return ''.join(random.sample(string.ascii_letters + string.digits, 4))

def sendMail(app, desemail, captcha):
    with app.app_context():
        message = Message(subject = '论坛验证码', recipients=[desemail], body='您的验证码是 %s 请在五分钟内进行验证' % captcha)
        mail.send(message)
