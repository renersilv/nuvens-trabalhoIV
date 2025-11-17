# TrabalhoIV - Processamento de Imagens de Documentos com AWS Chalice

## Descrição

Este projeto implementa um pipeline serverless para processamento automático de imagens de documentos usando AWS Chalice e serviços AWS.

## Arquitetura

O projeto utiliza os seguintes serviços AWS:
- **Amazon S3**: Armazenamento de imagens e arquivos processados
- **Amazon Textract**: Extração de texto das imagens
- **Amazon Translate**: Tradução automática do texto
- **Amazon Polly**: Síntese de voz (text-to-speech)
- **AWS Lambda**: Execução serverless (gerenciado pelo Chalice)

## Estrutura do Projeto

```
TrabalhoIV/
├── app.py                      # Aplicação principal com trigger S3
├── chalicelib/
│   ├── __init__.py
│   └── aws_services.py         # Funções para serviços AWS
├── requirements.txt            # Dependências do projeto
└── README.md                   # Este arquivo
```

## Fluxo de Processamento

1. Uma imagem é carregada no bucket S3 (pasta `/input`)
2. O evento S3 dispara a função Lambda
3. **Textract** extrai o texto da imagem
4. **Translate** traduz o texto para português
5. **Polly** gera um arquivo de áudio MP3
6. Texto traduzido e áudio são salvos na pasta `/output`

## Pré-requisitos

- Python 3.8+
- AWS CLI configurado com credenciais
- Conta AWS com permissões para:
  - S3
  - Textract
  - Translate
  - Polly
  - Comprehend (usado pelo Translate)
  - Lambda
  - IAM (para criação de roles)

## Instalação

1. Instale o AWS Chalice:
```bash
pip install chalice
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

### 1. Configure a região AWS

```bash
aws configure set region us-east-2
```

Ou defina no arquivo `.chalice/config.json`:
```json
{
  "region": "us-east-2"
}
```

### 2. Crie o bucket S3

```bash
aws s3 mb s3://seu-bucket-nome --region us-east-2
aws s3api put-object --bucket seu-bucket-nome --key input/
```

### 3. Configure o nome do bucket

Edite o arquivo `app.py` na linha 16:
```python
@app.on_s3_event(bucket='seu-bucket-nome',  # ALTERE AQUI
                 events=['s3:ObjectCreated:*'],
                 prefix='input/')
```

**Nota**: O trigger aceita JPG, JPEG e PNG automaticamente.

## Deploy

### 1. Faça o deploy da aplicação

```bash
chalice deploy
```

### 2. Configure permissões adicionais

O Chalice cria as permissões básicas, mas você precisa adicionar manualmente:

```bash
# Adicionar permissão do Comprehend (necessária para o Translate detectar idioma)
aws iam put-role-policy --role-name trabalhoiv-dev --policy-name comprehend-policy --policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"comprehend:DetectDominantLanguage\",\"Resource\":\"*\"}]}"
```

**PowerShell (Windows)**: Use aspas simples para o JSON:
```powershell
aws iam put-role-policy --role-name trabalhoiv-dev --policy-name comprehend-policy --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"comprehend:DetectDominantLanguage","Resource":"*"}]}'
```

### 3. Recursos criados

O Chalice criará automaticamente:
- Função Lambda (`trabalhoiv-dev-process_image`)
- API Gateway REST
- Role IAM com permissões
- Trigger S3→Lambda

## Uso

1. Faça upload de uma imagem (JPG, JPEG ou PNG) para a pasta `/input` do bucket:
```bash
aws s3 cp imagem.jpg s3://seu-bucket-nome/input/
```

2. O processamento será iniciado automaticamente

3. Os resultados estarão disponíveis na pasta `/output`:
   - `imagem.txt` - Texto extraído e traduzido
   - `imagem.mp3` - Áudio do texto em português

## Arquivos Gerados

### chalicelib/aws_services.py

Contém as seguintes funções:
- `detect_text(bucket, key)` - Extrai texto com Textract
- `translate_text(text, target_lang)` - Traduz texto com Translate
- `synthesize_speech(text, voice_id)` - Gera áudio com Polly
- `save_file_to_s3(bucket, key, content, content_type)` - Salva no S3

### app.py

- Handler do evento S3
- Orquestração do pipeline de processamento
- Tratamento de erros e logs

## Monitoramento

Visualize os logs da aplicação:
```bash
# Ver logs da função de processamento
chalice logs --name process_image

# Ver logs em tempo real
chalice logs --follow

# Ou use AWS CLI diretamente
aws logs tail /aws/lambda/trabalhoiv-dev-process_image --follow
```

## Remoção

Para remover todos os recursos criados:
```bash
chalice delete
```

## Customização

### Alterar o idioma de tradução

No arquivo `app.py`, linha 50:
```python
translated_text = aws_services.translate_text(extracted_text, target_lang='en')  # Para inglês
```

### Alterar a voz do Polly

No arquivo `app.py`, linha 54:
```python
audio_content = aws_services.synthesize_speech(translated_text, voice_id='Ricardo')  # Voz masculina
```

Vozes disponíveis em português:
- `Vitoria` - Feminina (padrão)
- `Camila` - Feminina
- `Ricardo` - Masculino

### Processar apenas um formato específico

O sistema aceita JPG, JPEG e PNG por padrão. Para aceitar apenas um formato, adicione o parâmetro `suffix`:
```python
@app.on_s3_event(bucket='seu-bucket-nome', 
                 events=['s3:ObjectCreated:*'],
                 prefix='input/',
                 suffix='.png')  # Apenas PNG
```

## Custos Estimados

Os custos variam conforme o uso:
- **Textract**: ~$1.50 por 1000 páginas
- **Translate**: ~$15 por milhão de caracteres
- **Polly**: ~$4 por milhão de caracteres
- **Lambda**: Nível gratuito disponível
- **S3**: ~$0.023 por GB/mês

## Limitações

- Imagens devem estar em formato JPG, JPEG ou PNG
- Tamanho máximo da imagem: 5MB (Textract)
- Texto para Polly: máximo 3000 caracteres por requisição

## Troubleshooting

### Erro de permissões IAM

Certifique-se de que a role do Lambda (`trabalhoiv-dev`) tem as seguintes permissões:
- `textract:DetectDocumentText` e `textract:AnalyzeDocument`
- `translate:TranslateText`
- `comprehend:DetectDominantLanguage` (importante!)
- `polly:SynthesizeSpeech`
- `s3:GetObject` e `s3:PutObject`
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

Verifique as políticas:
```bash
aws iam get-role-policy --role-name trabalhoiv-dev --policy-name trabalhoiv-dev
```

### Evento S3 não dispara

Verifique:
- Nome do bucket está correto
- Prefixo e sufixo estão corretos
- Bucket está na mesma região da função Lambda

## Licença

Este projeto é para fins educacionais.
