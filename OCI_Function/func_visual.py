import io
import json
import logging
import oci
import base64
from datetime import datetime

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    
    logging.getLogger().info("Iniciando Function")
    max_results = 5
    res = ''
    retorno = []

    # Auth Config Definition
    config = oci.config.from_file('config')
    object_storage_client = oci.object_storage.ObjectStorageClient(config)

    # AI Vision Client Definition
    ai_vision_client = oci.ai_vision.AIServiceVisionClient(config)
    try:
        logging.getLogger().info("Body...")
        body = json.loads(data.getvalue())
        encoded_string = body.get("encoded_string")

        #Salvar imagem no Object Storage
        
        logging.getLogger().info("Salvando imagem no Object Storage...")
        put_object_response = object_storage_client.put_object(
            namespace_name="idcci5ks1puo",
            bucket_name="Dobot",
            object_name="Dobot_{0}.png".format(datetime.today().strftime("%Y%m%d%H%M%S")),
            put_object_body=base64.b64decode(encoded_string))
        
        retorno.append("https://objectstorage.us-ashburn-1.oraclecloud.com/n/idcci5ks1puo/b/Frankie/o/Dobot_{0}.png".format(datetime.today().strftime("%Y%m%d%H%M%S")))
        logging.getLogger().info("Imagem salva no Object Storage")
        
  
        #Classificacao da imagem
        ai_service_vision_client = oci.ai_vision.AIServiceVisionClient(config=config)
        analyze_image_details = oci.ai_vision.models.AnalyzeImageDetails()
        inline_image_details = oci.ai_vision.models.InlineImageDetails()
        logging.getLogger().info("Preparando analise de imagem...")

        image_classification_feature = oci.ai_vision.models.ImageClassificationFeature()
        image_classification_feature.max_results = max_results
        features = [image_classification_feature]
        inline_image_details.data = encoded_string
        analyze_image_details.image = inline_image_details
        analyze_image_details.features = features
        
        res = ai_service_vision_client.analyze_image(analyze_image_details=analyze_image_details)
        logging.getLogger().info("Imagem classificada...")
   
        for item in res.data.labels:
            retorno.append(item.name)

    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    return response.Response(
        ctx, response_data=json.dumps(
            {"objetos": retorno}),
        headers={"Content-Type": "application/json"}
    )
