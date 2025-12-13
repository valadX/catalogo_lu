import pandas as pd
import os
from PIL import Image
import colorsys

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'base_dados.csv'
ARQUIVO_FINAL = 'base_dados_inteligente.csv'

def identificar_cor_hsv(r, g, b):
    # Converte RGB (0-255) para HSV (0-1)
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    h_graus = h * 360  # Converte para graus (0-360)
    
    # --- 1. FILTRO DE LUMINOSIDADE E SATURAÇÃO (Remove chão/parede) ---
    if v < 0.2: return "Preto"       # Muito escuro
    if v > 0.95 and s < 0.1: return "Branco" # Muito claro e sem cor
    if s < 0.15: return "Cinza/Branco" # Tem cor mas é muito fraca (parede)

    # --- 2. CLASSIFICAÇÃO PELO ARCO-ÍRIS (MATIZ) ---
    
    # VERMELHO vs ROSA (O segredo está na Saturação)
    if (h_graus >= 0 and h_graus <= 25) or (h_graus >= 340 and h_graus <= 360):
        if s < 0.6: # Se é vermelho mas é "lavado/pastel" -> É ROSA BEBÊ
            return "Rosa"
        else:
            return "Vermelho"
            
    # ROSA FORTE (Pink/Magenta)
    elif h_graus >= 280 and h_graus < 340:
        return "Rosa"

    # LARANJA vs MARROM (Laranja escuro vira marrom)
    elif h_graus > 25 and h_graus < 45:
        if v < 0.6: return "Marrom"
        return "Laranja"

    # AMARELO
    elif h_graus >= 45 and h_graus < 75:
        return "Amarelo"

    # VERDE
    elif h_graus >= 75 and h_graus < 160:
        return "Verde"

    # AZUL (Ciano e Azul real)
    elif h_graus >= 160 and h_graus < 260:
        return "Azul"

    # ROXO
    elif h_graus >= 260 and h_graus < 280:
        return "Roxo"

    return "Outro"

def analisar_imagem_v3(caminho_img):
    try:
        img = Image.open(caminho_img)
        img = img.resize((50, 50)) # Reduz para processar rápido
        img = img.convert('RGB')
        
        pixels = list(img.getdata())
        
        votos = {}
        
        for r, g, b in pixels:
            nome_cor = identificar_cor_hsv(r, g, b)
            
            # Ignora cores neutras na contagem final para focar na decoração
            if nome_cor not in ["Preto", "Branco", "Cinza/Branco", "Outro"]:
                votos[nome_cor] = votos.get(nome_cor, 0) + 1
        
        # Quem teve mais votos vence
        if not votos:
            return "Neutro"
            
        cor_vencedora = max(votos, key=votos.get)
        return cor_vencedora
        
    except Exception as e:
        print(f"Erro: {e}")
        return "Erro"

# --- EXECUÇÃO ---
print("--- Iniciando Análise V3 (Filtro Pastel/Vibrante) ---")

if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV)
    novas_cores = []
    
    total = len(df)
    for index, row in df.iterrows():
        caminho = row['caminho_imagem']
        if os.path.exists(caminho):
            cor = analisar_imagem_v3(caminho)
            print(f"[{index+1}/{total}] {cor} <- {caminho}") 
            novas_cores.append(cor)
        else:
            novas_cores.append("Arquivo Perdido")
            
    df['cor_predominante'] = novas_cores
    df.to_csv(ARQUIVO_FINAL, index=False)
    print("--- Cores recalculadas! Atualize o site (F5). ---")
else:
    print("Arquivo csv não encontrado.")