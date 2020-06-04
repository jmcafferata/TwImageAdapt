import telegram
from PIL import Image
from PIL import ImageFilter
import os
from io import BytesIO
import requests


def webhook(request):

    print('hey')

    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    print('creado el bot')

    if request.method == "POST":

        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id

        # Chequeamos que sea foto

        if update.message:

            if update.message.photo:

                print('es una foto')

                try:

                    # Agarramos el file_path que viene en la foto (necesitas el file_id). Es el 3ro del array, las otras dos son thumbs
                    path = bot.getFile(update.message.photo[2].file_id).file_path

                    # Buscamos la imagen con un http request
                    response = requests.get(path)

                    # Abrimos la imagen con PIL
                    img_original = Image.open(BytesIO(response.content))

                    # Resizeamos la imagen
                    multiplicador = 720/img_original.height

                    img_modificada = img_original.resize((int(img_original.width*multiplicador),720))               

                    # Creamos la imagen final
                    img_final = Image.new('RGB',(1280,720))

                    # Blureamos la original, la resizeamos y la pegamos en img_final
                    blurred = img_original.filter(ImageFilter.GaussianBlur(100))

                    blurred = blurred.resize((1280,1280))

                    img_final.paste(blurred)

                    # Centramos la imagen modificada para pegarla en el img_final
                    pastePoint = int((1280/2)-img_original.width*multiplicador/2)

                    img_final.paste(img_modificada, box=(pastePoint,0))

                    # Le damos la img_final a Telegram con BytesIO
                    bio = BytesIO()
                    bio.name = 'image.jpeg'
                    img_final.save(bio, 'JPEG')
                    bio.seek(0)

                    # Enviamos la imagen final al usuario
                    bot.send_photo(chat_id=chat_id, photo=bio)

                    bot.sendMessage(chat_id,'De nada.')
                except:
                    bot.sendMessage(chat_id,'Algo pasó.')
    return "ok"