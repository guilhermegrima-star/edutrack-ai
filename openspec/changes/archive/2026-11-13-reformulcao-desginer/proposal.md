# Proposta: Reformulação do Design e Centralização da Autenticação

## Motivação
Modernizar e harmonizar a experiência visual do **EduTrack AI**, inspirando-se diretamente nas referências visuais fornecidas pela equipe de produto:
1. **Página de Login e Landing Page (`/assets/login.png`)**: Design minimalista, elegante e focado em conversão e clareza, no estilo Notion, com tipografia refinada e mensagens de impacto:
   - Frase Principal: *"Aprenda mais. Organize melhor. Vá além."*
   - Subtítulo: *"Reúna seus conteúdos, planeje suas atividades e tenha tudo o que precisa para evoluir nos estudos."*
2. **Dashboard Principal (`/assets/home principal.png`)**: Painel de controle acadêmico completo com identidade visual baseada em tons de índigo/roxo (`#3B3486`), banner de boas-vindas lilás com ilustração 3D, cartões de indicadores (Certificados, Cursos em Andamento, Concluídos), visualização de atividade semanal ("Hours Activity") com gráfico de barras duplas (amarelo e roxo) e métricas de desempenho.

Adicionalmente, consolidar a regra estrita de autenticação: **a página principal (`app.py`) passa a ser o único ponto de entrada para login e cadastro no sistema**. Todas as outras páginas têm seus formulários de autenticação removidos e passam a exigir autenticação prévia.

## Escopo
- **Landing Page & Login Centralizado (`app.py`)**:
  - Exibir a página de apresentação e login inspirada em `/assets/login.png` para utilizadores não autenticados.
  - Implementar os textos exatos solicitados: *"Aprenda mais. Organize melhor. Vá além."* e *"Reúna seus conteúdos, planeje suas atividades e tenha tudo o que precisa para evoluir nos estudos."*.
  - Integrar formulários modernos de Login e Cadastro conectados à API Xano (`POST /auth/login`, `POST /auth/signup`, `GET /auth/me`).
  - Ocultar a navegação e recursos internos para utilizadores não logados.
- **Remoção de Outras Formas de Autenticação**:
  - Remover integralmente formulários de login e cadastro da página `pages/3_🔒_Perfil.py`.
  - Proteger a página de perfil com bloqueio de acesso para usuários deslogados, orientando o redirecionamento para a página principal.
- **Redesenho do Dashboard Principal (`app.py`) pós-login**:
  - Layout inspirado fielmente em `/assets/home principal.png`:
    - Sidebar temática em tom índigo/roxo profundo (`#3B3486`), logotipo Smart Education / EduTrack, menu com ícones e destaque no item ativo, e card de "Upgrade To Pro".
    - Barra de pesquisa superior com cantos arredondados (`🔍 Try to find / Pesquisar`).
    - Banner de boas-vindas lilás em gradiente com saudação personalizada e ilustração/avatar 3D.
    - 3 Cards de Indicadores rápidos: Certificados Obtidos, Cursos em Andamento, Cursos Concluídos.
    - Seção "Hours Activity" com filtro semanal, badge de progresso (+2h que na semana anterior), gráfico de barras duplas (amarelo/roxo) e métricas laterais (Horas Dedicadas, Aproveitamento Médio, Entregas Pendentes).
    - Seção "Browse Courses" / Gestão de Alunos com relatórios em PDF.
- **Padrão Visual Uniforme (`utils/theme.py` e `pages/3_🔒_Perfil.py`)**:
  - Criação de folha de estilos unificada garantindo consistência visual em todas as telas da plataforma.

## Não-Escopo (Non-goals)
- Alterações no schema do banco de dados no backend Xano.
- Remoção da geração de PDF (mantida e estilizada de acordo com a nova identidade).
