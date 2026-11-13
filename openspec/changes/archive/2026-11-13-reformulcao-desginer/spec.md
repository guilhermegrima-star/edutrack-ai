# Especificação: Reformulação de Design e Centralização de Login

## Requisitos Funcionais e Visuais

### 1. Centralização Exclusiva da Autenticação
- O sistema DEVE permitir login e criação de conta **única e exclusivamente** através da página principal (`app.py`).
- Qualquer formulário de login ou cadastro em páginas secundárias (notadamente `pages/3_🔒_Perfil.py`) DEVE ser removido.
- Se um usuário deslogado tentar acessar diretamente qualquer página secundária, ela DEVE bloquear o conteúdo, exibir uma mensagem amigável de redirecionamento e não oferecer formulários de login locais.

### 2. Página Principal Deslogada (Landing Page & Login - `/assets/login.png`)
- **Cabeçalho (Navbar Minimalista)**:
  - Logotipo e nome da marca EduTrack AI.
  - Links de navegação informativos (ex: Recursos, Metodologia, Planos).
  - Botão de ação direta para login / cadastro.
- **Hero Section**:
  - Frase Principal obrigatória: **"Aprenda mais. Organize melhor. Vá além."**
  - Subtítulo obrigatório: **"Reúna seus conteúdos, planeje suas atividades e tenha tudo o que precisa para evoluir nos estudos."**
  - Destaque visual inspirado no Notion (badge/pill destacado).
- **Formulário de Autenticação Unificado**:
  - Abas ou alternador entre "Entrar" (Login) e "Criar Conta" (Cadastro).
  - Campos de Login: E-mail e Senha.
  - Campos de Cadastro: Nome completo, E-mail, Senha e Confirmação.
  - Validação de senha: Mínimo 8 caracteres, contendo pelo menos 1 letra e 1 número.
  - Integração com endpoints Xano (`/auth/login`, `/auth/signup`, `/auth/me`).
  - Armazenamento no `st.session_state` de `auth_token` e `user_data`.
- **Área de Pré-visualização do Produto**:
  - Mockup visual elegante do painel do aluno.

### 3. Dashboard Principal Autenticado (`app.py` - `/assets/home principal.png`)
- **Barra Lateral (Sidebar)**:
  - Fundo em tom índigo/roxo (`#3B3486`).
  - Logotipo EduTrack AI / Smart Education com ícone de lápis/estudos estilizado.
  - Menu de navegação claro: Dashboard, Disciplinas & Alunos, Desempenho & Gráficos, Perfil.
  - Card estilizado "Upgrade To Pro" com badge e botão de ação.
  - Perfil compacto do usuário com opção de Logout.
- **Barra Superior**:
  - Campo de busca estético arredondado (`🔍 Try to find / Pesquisar...`).
- **Banner de Boas-Vindas**:
  - Fundo em gradiente suave lilás (`#F3E8FF` a `#EDE9FE`).
  - Título em destaque: "Bem-vindo(a) de volta, [Nome]!" / "Welcome back, [Nome]!".
  - Mensagem motivacional: "Esta semana você manteve 4 dias consecutivos de estudo! Continue assim para bater suas metas!".
  - Ilustração temática de estudante com notebook/laptop.
- **Cartões de Indicadores Rápidos (3 KPIs)**:
  - Card 1: 📜 Certificados Conquistados (ex: 18).
  - Card 2: 📖 Cursos / Disciplinas em Andamento (ex: 5).
  - Card 3: 🎓 Tarefas / Cursos Concluídos (ex: 21).
- **Seção "Hours Activity" (Horas de Atividade)**:
  - Filtro de período (Semanal / Mensal).
  - Badge positivo: `+2h a mais que na semana passada`.
  - Legenda de cores das matérias (amarelo para Teoria/Matemática e roxo para Prática/IA).
  - Gráfico de barras duplas (amarelo e roxo) por dia da semana (08, 09, 10, 11, 12, 13, 14).
  - Coluna lateral de métricas: Horas Dedicadas (12h, +10%), Aproveitamento Médio (86%, -10%), Tarefas Pendentes (2).
- **Seção de Cursos & Gestão Acadêmica**:
  - Cards de disciplinas com progresso visual.
  - Tabela filtrável de alunos e notas.
  - Funcionalidade preservada de geração e download de relatórios acadêmicos individuais em PDF.

### 4. Harmonização da Página de Perfil (`pages/3_🔒_Perfil.py`)
- Aplicação do mesmo padrão visual (estilos CSS, paleta de cores, tipografia e botões).
- Exibição de cartões de informações cadastrais do aluno autenticado.
- Seção integrada para compilar e baixar relatório acadêmico individual em PDF.
- Botão de Logout seguro limpando o `session_state`.
