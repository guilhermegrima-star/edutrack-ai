# Tarefas de Implementação: Reformulação de Design e Centralização de Login

- [x] 1. Módulo Unificado de Tema e Estilo (`utils/theme.py`)
  - [x] 1.1 Criar regras CSS globais injetáveis para sidebar roxa (`#3B3486`), cards brancos com sombras suaves, banner lilás e botões modernos
  - [x] 1.2 Criar helpers de renderização: cabeçalho da sidebar, barra de busca estilizada, banners e cards de KPIs
  - [x] 1.3 Adicionar estilo específico para a Landing/Login Page inspirada em `/assets/login.png`

- [x] 2. Centralização da Autenticação e Reformulação da Página Principal (`app.py`)
  - [x] 2.1 Criar verificação de autenticação: fluxo deslogado vs fluxo autenticado
  - [x] 2.2 Desenvolver a Landing Page de Login inspirada em `/assets/login.png`
    - [x] 2.2.1 Inserir frase principal: "Aprenda mais. Organize melhor. Vá além."
    - [x] 2.2.2 Inserir subtítulo: "Reúna seus conteúdos, planeje suas atividades e tenha tudo o que precisa para evoluir nos estudos."
    - [x] 2.2.3 Implementar formulário moderno unificado de Login e Cadastro (com validação de senha e integração Xano)
    - [x] 2.2.4 Incluir preview/mockup visual da aplicação no estilo Notion
  - [x] 2.3 Desenvolver o Dashboard pós-login inspirado em `/assets/home principal.png`
    - [x] 2.3.1 Montar sidebar com logotipo Smart Education / EduTrack, menu de navegação, card Pro e logout
    - [x] 2.3.2 Montar barra de pesquisa superior estilizada
    - [x] 2.3.3 Montar banner de boas-vindas lilás com saudação personalizada e ilustração 3D
    - [x] 2.3.4 Montar os 3 cards de KPIs rápidos (Certificados, Cursos em Andamento, Concluídos)
    - [x] 2.3.5 Montar a seção "Hours Activity" com gráfico de barras duplas (amarelo e roxo) e métricas laterais
    - [x] 2.3.6 Integrar seção "Browse Courses" / Gestão de Alunos com exportação em PDF e filtros

- [x] 3. Reformulação e Proteção da Página Secundária (`pages/3_🔒_Perfil.py`)
  - [x] 3.1 Remover todos os formulários de login e cadastro da página
  - [x] 3.2 Implementar bloqueio com mensagem amigável e botão de redirecionamento para usuários deslogados
  - [x] 3.3 Aplicar o mesmo padrão visual (tema índigo/roxo, cards e botões) na visualização autenticada do perfil
  - [x] 3.4 Manter a geração de PDF e ação de Logout sincronizada

- [x] 4. Validação, Testes e Refinamento
  - [x] 4.1 Validar execução do Streamlit sem erros de sintaxe ou importação
  - [x] 4.2 Validar transição do estado deslogado para logado e logout
  - [x] 4.3 Garantir que nenhuma outra página permita login/cadastro direto
