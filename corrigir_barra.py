import pandas as pd

# Carrega seu banco de dados
arquivo = 'base_dados_inteligente.csv'
df = pd.read_csv(arquivo)

print("--- Corrigindo as barras do Windows para Linux ---")

# Substitui todas as barras invertidas (\) por barras normais (/)
if 'caminho_imagem' in df.columns:
    df['caminho_imagem'] = df['caminho_imagem'].str.replace('\\', '/', regex=False)
    print("✅ Barras corrigidas!")
else:
    print("❌ Coluna 'caminho_imagem' não encontrada.")

# Salva o arquivo pronto para a nuvem
df.to_csv(arquivo, index=False)
print("💾 Arquivo salvo! Agora pode subir para o GitHub.")