"""
Módulo com funções para interagir com serviços AWS.
Utiliza boto3 para chamar Textract, Translate, Polly e S3.
"""
import boto3
from botocore.exceptions import ClientError

# Instanciando clientes AWS no escopo global para reutilização
textract = boto3.client('textract')
translate = boto3.client('translate')
polly = boto3.client('polly')
s3 = boto3.client('s3')


def detect_text(bucket, key):
    """
    Extrai texto de uma imagem usando Amazon Textract.
    
    Args:
        bucket (str): Nome do bucket S3
        key (str): Chave do objeto (caminho do arquivo)
    
    Returns:
        str: Texto extraído da imagem
    """
    try:
        print(f"Extraindo texto da imagem: s3://{bucket}/{key}")
        
        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )
        
        # Concatenar todo o texto detectado
        extracted_text = ""
        for item in response.get('Blocks', []):
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + "\n"
        
        print(f"Texto extraído com sucesso. Total de caracteres: {len(extracted_text)}")
        return extracted_text.strip()
    
    except ClientError as e:
        print(f"Erro ao extrair texto com Textract: {e}")
        raise
    except Exception as e:
        print(f"Erro inesperado ao extrair texto: {e}")
        raise


def translate_text(text, target_lang='pt'):
    """
    Traduz texto usando Amazon Translate.
    
    Args:
        text (str): Texto a ser traduzido
        target_lang (str): Código do idioma de destino (padrão: 'pt')
    
    Returns:
        str: Texto traduzido
    """
    try:
        print(f"Traduzindo texto para o idioma: {target_lang}")
        
        if not text:
            print("Texto vazio, nada para traduzir")
            return ""
        
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode=target_lang
        )
        
        translated_text = response['TranslatedText']
        print(f"Tradução concluída com sucesso")
        return translated_text
    
    except ClientError as e:
        print(f"Erro ao traduzir texto com Translate: {e}")
        raise
    except Exception as e:
        print(f"Erro inesperado ao traduzir texto: {e}")
        raise


def synthesize_speech(text, voice_id='Vitoria'):
    """
    Gera áudio a partir de texto usando Amazon Polly.
    
    Args:
        text (str): Texto a ser convertido em áudio
        voice_id (str): ID da voz (padrão: 'Vitoria' - voz feminina em português brasileiro)
    
    Returns:
        bytes: Conteúdo do arquivo de áudio em formato MP3
    """
    try:
        print(f"Gerando áudio com a voz: {voice_id}")
        
        if not text:
            print("Texto vazio, nada para sintetizar")
            return b""
        
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='standard'
        )
        
        # Ler o stream de áudio
        audio_content = response['AudioStream'].read()
        print(f"Áudio gerado com sucesso. Tamanho: {len(audio_content)} bytes")
        return audio_content
    
    except ClientError as e:
        print(f"Erro ao gerar áudio com Polly: {e}")
        raise
    except Exception as e:
        print(f"Erro inesperado ao gerar áudio: {e}")
        raise


def save_file_to_s3(bucket, key, content, content_type):
    """
    Salva um arquivo no S3.
    
    Args:
        bucket (str): Nome do bucket S3
        key (str): Chave do objeto (caminho do arquivo)
        content (str or bytes): Conteúdo do arquivo
        content_type (str): Tipo MIME do conteúdo
    
    Returns:
        bool: True se o arquivo foi salvo com sucesso
    """
    try:
        print(f"Salvando arquivo no S3: s3://{bucket}/{key}")
        
        # Se o conteúdo for string, converter para bytes
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType=content_type
        )
        
        print(f"Arquivo salvo com sucesso no S3")
        return True
    
    except ClientError as e:
        print(f"Erro ao salvar arquivo no S3: {e}")
        raise
    except Exception as e:
        print(f"Erro inesperado ao salvar arquivo: {e}")
        raise
