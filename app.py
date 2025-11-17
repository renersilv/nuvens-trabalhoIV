"""
Aplicação AWS Chalice para processamento de imagens de documentos.
Escuta eventos S3, extrai texto com Textract, traduz com Translate,
gera áudio com Polly e salva os resultados no bucket.
"""
from chalice import Chalice
from chalicelib import aws_services
import os

app = Chalice(app_name='trabalhoiv')

# Configuração de logging
app.debug = True


@app.on_s3_event(bucket='meu-processador-documentos-2025', 
                 events=['s3:ObjectCreated:*'],
                 prefix='input/')
def process_image(event):
    """
    Processa imagens carregadas no S3.
    Extrai texto, traduz, gera áudio e salva os resultados.
    
    Args:
        event: Evento S3 contendo informações do objeto criado
    """
    try:
        # Extrair informações do evento
        bucket = event.bucket
        key = event.key
        print(f"Processando novo arquivo: s3://{bucket}/{key}")
        
        # Validar se é uma imagem
        valid_extensions = ['.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(key)[1].lower()
        if file_extension not in valid_extensions:
            print(f"Arquivo {key} não é uma imagem válida. Ignorando.")
            return
        
        # 1. Extrair texto da imagem usando Textract
        print("Etapa 1: Extraindo texto da imagem...")
        extracted_text = aws_services.detect_text(bucket, key)
        
        if not extracted_text:
            print("Nenhum texto foi encontrado na imagem.")
            return
        
        print(f"Texto extraído: {extracted_text[:100]}...")
        
        # 2. Traduzir texto para português
        print("Etapa 2: Traduzindo texto...")
        translated_text = aws_services.translate_text(extracted_text, target_lang='pt')
        print(f"Texto traduzido: {translated_text[:100]}...")
        
        # 3. Gerar áudio do texto traduzido
        print("Etapa 3: Gerando áudio...")
        audio_content = aws_services.synthesize_speech(translated_text, voice_id='Vitoria')
        
        # 4. Preparar nomes dos arquivos de saída
        base_filename = os.path.splitext(os.path.basename(key))[0]
        output_txt_key = f"output/{base_filename}.txt"
        output_mp3_key = f"output/{base_filename}.mp3"
        
        # 5. Salvar texto traduzido no S3
        print("Etapa 4: Salvando texto traduzido no S3...")
        aws_services.save_file_to_s3(
            bucket=bucket,
            key=output_txt_key,
            content=translated_text,
            content_type='text/plain'
        )
        print(f"Texto salvo em: s3://{bucket}/{output_txt_key}")
        
        # 6. Salvar áudio no S3
        print("Etapa 5: Salvando áudio no S3...")
        aws_services.save_file_to_s3(
            bucket=bucket,
            key=output_mp3_key,
            content=audio_content,
            content_type='audio/mpeg'
        )
        print(f"Áudio salvo em: s3://{bucket}/{output_mp3_key}")
        
        print(f"Processamento concluído com sucesso para: {key}")
        
    except Exception as e:
        print(f"Erro ao processar imagem {event.key}: {str(e)}")
        # Em produção, você pode querer enviar para um Dead Letter Queue (DLQ)
        # ou um sistema de monitoramento como CloudWatch
        raise


@app.route('/')
def index():
    """
    Rota raiz da aplicação para verificação de status.
    """
    return {
        'app': 'TrabalhoIV - Document Image Processor',
        'status': 'running',
        'description': 'Processa imagens de documentos usando Textract, Translate e Polly'
    }


@app.route('/health')
def health():
    """
    Endpoint de health check.
    """
    return {
        'status': 'healthy',
        'service': 'chalice-document-processor'
    }
