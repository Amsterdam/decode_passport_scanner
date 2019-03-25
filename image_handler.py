from PIL import Image
import qrcode
from qrcode.image.pure import PymagingImage
from cStringIO import StringIO
from shutil import copyfileobj
import os, base64

def convert_jp2(img_data, output_name, output_format, output=True):
    with open('tmp.jp2', 'wb') as input:
        input.write(img_data)
    
    main_img = Image.open('tmp.jp2')
    os.remove('tmp.jp2')
    
    main_img = main_img.resize(((main_img.size[0] / 2), (main_img.size[1] / 2)), Image.ANTIALIAS)

    # output_format = 'jpeg'
    buffer = StringIO()
    main_img.save(buffer, format=output_format)
    base64_image = base64.b64encode(buffer.getvalue())

    if output:
        output_folder = 'output'
        file = '{0}/{1}.{2}'.format(output_folder, output_name, output_format)

        with open(file, 'w') as output:
            buffer.seek(0)
            copyfileobj(buffer, output)
        
    buffer.close()
    return base64_image

def qr_image(input):
    qr_img = qrcode.make(input, image_factory=PymagingImage)

    with open('qr.png', 'wb') as output:
        qr_img.save(output)

    qr = Image.open('qr.png')
    qr.show()
