# Tarefas de Implementação: Migração para Streamlit Secrets

## Fase 1: Configuração e Segurança
- [x] Criar/atualizar `.gitignore` para bloquear `.streamlit/secrets.toml` e `.env`
- [x] Criar diretório `edutrack-ai/.streamlit/`
- [x] Criar `edutrack-ai/.streamlit/secrets.toml` com chaves de produção/desenvolvimento
- [x] Criar `edutrack-ai/.streamlit/secrets.toml.example` documentando as variáveis necessárias

## Fase 2: Módulo Central de Configuração
- [x] Criar `edutrack-ai/utils/__init__.py` e `edutrack-ai/utils/config.py` com resolução defensiva:
  - Leitura prioritária de `st.secrets`
  - Fallback transparente para `os.environ`
  - Fallback para `.env`
  - Fallbacks padrão seguros

## Fase 3: Refatoração das Páginas da Aplicação
- [x] Refatorar `edutrack-ai/pages/3_🔒_Perfil.py` para utilizar `get_xano_auth_url()` e suporte nativo a `st.secrets`
- [x] Garantir que `app.py` carregue corretamente com a nova estrutura

## Fase 4: Integração com Scripts de Automação
- [x] Adaptar `edutrack-ai/scripts/calculate_progress.py` para consumir configurações centralizadas
- [x] Adaptar `edutrack-ai/scripts/generate_report.py` para consumir configurações centralizadas

## Fase 5: Validação e Testes
- [x] Validar leitura de secrets e compatibilidade sem lançar exceções caso `secrets.toml` não exista em deploys alternativos
