import instaloader
import pandas as pd
import os
import time
import random

# --- CONFIGURAÇÕES ---
PERFIL_ALVO = 'Decorando.comluana' 

# ⚠️ COLE O SESSIONID DO CHROME AQUI DENTRO DAS ASPAS:
MINHA_SESSION_ID = '78145455719%3AGKhNhG4JBMMRVP%3A21%3AAYixdLO37HxBES1PNzKN0j3WvD2RkMc8qVeDN3_n1Q'

# Limite para teste (se funcionar, mude para None)
LIMITE_POSTS = None 
PAUSA_MINIMA = 20
PAUSA_MAXIMA = 40

def salvar_parcial(lista_dados):
    df = pd.DataFrame(lista_dados)
    df.to_csv('base_dados.csv', index=False, encoding='utf-8')
    print(f"💾 Salvamento automático: {len(df)} itens.")

def baixar_catalogo():
    print(f"--- Iniciando Extrator (Modo Transplante) ---")
    
    # 1. Configura o robô para fingir ser um iPhone/Chrome
    L = instaloader.Instaloader(
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )

    # 2. INJEÇÃO CIRÚRGICA DO COOKIE (Sem fazer login)
    try:
        L.context._session.cookies.set('sessionid', MINHA_SESSION_ID, domain='.instagram.com')
        print("✅ Sessão injetada manualmente.")
    except Exception as e:
        print(f"❌ Erro ao configurar: {e}")
        return

    # 3. Carregar o histórico para não repetir
    dados_catalogo = []
    if os.path.exists('base_dados.csv'):
        try:
            df_antigo = pd.read_csv('base_dados.csv')
            dados_catalogo = df_antigo.to_dict('records')
            print(f"📂 Histórico carregado: {len(dados_catalogo)} itens.")
        except: pass

    # 4. Tenta acessar o perfil
    try:
        print(f"Tentando acessar perfil: {PERFIL_ALVO}...")
        posts = instaloader.Profile.from_username(L.context, PERFIL_ALVO).get_posts()
    except Exception as e:
        print(f"\n❌ ERRO DE ACESSO: {e}")
        print("DIAGNÓSTICO:")
        if "401" in str(e) or "JSON" in str(e):
            print("1. O sessionid expirou ou foi copiado errado.")
            print("2. OU sua conta está bloqueada temporariamente (espere 24h).")
        return

    contador_sessao = 0
    
    try:
        for post in posts:
            if LIMITE_POSTS and contador_sessao >= LIMITE_POSTS:
                print("Meta atingida!")
                break
                
            url_atual = f"https://www.instagram.com/p/{post.shortcode}/"
            ja_tem_no_excel = any(d['url_instagram'] == url_atual for d in dados_catalogo)
            
            nome_arquivo = post.date_utc.strftime('%Y-%m-%d_%H-%M-%S_UTC') + ".jpg"
            caminho_completo = os.path.join(PERFIL_ALVO, nome_arquivo)
            arquivo_existe = os.path.exists(caminho_completo)

            if ja_tem_no_excel and arquivo_existe:
                print(f"⏭️  [PULANDO] {post.date_local}")
                continue

            print(f"⬇️  Baixando: {post.date_local}...")
            
            sucesso = False
            tentativas = 0
            
            while not sucesso and tentativas < 3:
                try:
                    baixou = L.download_post(post, target=PERFIL_ALVO)
                    
                    if not ja_tem_no_excel:
                        dados_catalogo.append({
                            'data': post.date_local,
                            'legenda': post.caption if post.caption else "",
                            'url_instagram': url_atual,
                            'caminho_imagem': caminho_completo, 
                            'likes': post.likes,
                            'oculto': False
                        })
                    
                    sucesso = True
                    
                    if baixou:
                        tempo = random.randint(PAUSA_MINIMA, PAUSA_MAXIMA)
                        print(f"   ⏳ Pausa {tempo}s...")
                        time.sleep(tempo)
                        contador_sessao += 1
                        
                    if contador_sessao % 10 == 0:
                        salvar_parcial(dados_catalogo)

                except Exception as e:
                    print(f"   Erro no post: {e}")
                    if "401" in str(e) or "429" in str(e):
                        print("🔴 Bloqueio detectado. Parando.")
                        return
                    time.sleep(10)
                    tentativas += 1

    except Exception as e:
        print(f"Erro no loop: {e}")

    print("--- Fim! ---")
    salvar_parcial(dados_catalogo)

if __name__ == "__main__":
    baixar_catalogo()