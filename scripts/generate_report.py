"""
generate_report.py
-------------------
Gera um relatório acadêmico de desempenho do aluno em formato PDF
e disponibiliza integração para download e upload no backend Xano.

Grupo de API utilizado: edutrack.ai (canonical: gTfD518O)
Endpoints consumidos:
  GET  /auth/me              → dados cadastrais do aluno autenticado
  GET  /subjects             → disciplinas cadastradas pelo aluno
  GET  /academic_tasks       → tarefas acadêmicas do aluno
  POST /student/report       → upload do relatório PDF gerado (opcional via --upload)
  GET  /student/report       → consulta do relatório do aluno

Variáveis de ambiente (.env):
  EDUTRACK_BASE_URL    — URL base do grupo edutrack.ai
  EDUTRACK_AUTH_URL    — URL base do grupo de autenticação
  EDUTRACK_TOKEN       — Token JWT Bearer do aluno
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# Importa o cliente base e lógica de cálculo de calculate_progress
try:
    from scripts.calculate_progress import BASE_URL, EduTrackClient
except ImportError:
    # Fallback se executado a partir do diretório scripts/
    try:
        from calculate_progress import BASE_URL, EduTrackClient
    except ImportError:
        BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O"
        EduTrackClient = None  # type: ignore

load_dotenv()

AUTH_BASE_URL: str = os.getenv(
    "EDUTRACK_AUTH_URL",
    os.getenv("XANO_AUTH_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:authentication"),
).rstrip("/")


# ---------------------------------------------------------------------------
# Cliente de Relatório (Extensão do EduTrackClient)
# ---------------------------------------------------------------------------


class StudentReportClient:
    """Cliente HTTP para coleta de dados do aluno e upload de relatórios."""

    def __init__(self, token: str, base_url: str = BASE_URL, auth_url: str = AUTH_BASE_URL):
        self.token = token.strip()
        self.base_url = base_url.rstrip("/")
        self.auth_url = auth_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        )

    def get_me(self) -> dict[str, Any]:
        """Obtém dados cadastrais do usuário autenticado via /auth/me."""
        urls = [
            f"{self.auth_url}/auth/me",
            f"{self.auth_url}/me",
            f"{self.base_url}/auth/me",
        ]
        for url in urls:
            try:
                resp = self._session.get(url, timeout=10)
                if resp.ok:
                    return resp.json()
            except requests.RequestException:
                continue

        # Fallback caso os endpoints de auth estejam inacessíveis
        return {"id": 0, "name": "Aluno EduTrack", "email": "aluno@edutrack.ai"}

    def get_subjects(self) -> list[dict[str, Any]]:
        """Lista as disciplinas do aluno autenticado via GET /subjects."""
        try:
            resp = self._session.get(f"{self.base_url}/subjects", timeout=10)
            if resp.ok:
                data = resp.json()
                if isinstance(data, list):
                    return data
                return data.get("items", data.get("result", []))
        except requests.RequestException as err:
            print(f"[Aviso] Falha ao listar disciplinas: {err}", file=sys.stderr)
        return []

    def get_tasks(self, subject_id: int | None = None) -> list[dict[str, Any]]:
        """Lista tarefas acadêmicas filtradas ou completas via GET /academic_tasks."""
        params: dict[str, Any] = {}
        if subject_id is not None:
            params["subject_id"] = subject_id

        endpoints = [f"{self.base_url}/academic_tasks", f"{self.base_url}/task", f"{self.base_url}/tasks"]
        for ep in endpoints:
            try:
                resp = self._session.get(ep, params=params, timeout=10)
                if resp.ok:
                    data = resp.json()
                    if isinstance(data, list):
                        return data
                    return data.get("items", data.get("result", []))
            except requests.RequestException:
                continue
        return []

    def upload_report(
        self,
        pdf_path: str | Path,
        summary_progress: float,
        checksum: str,
    ) -> dict[str, Any]:
        """Envia o arquivo PDF compilado para o endpoint POST /student/report do Xano."""
        path = Path(pdf_path)
        if not path.is_file():
            return {"error": f"Arquivo não encontrado: {pdf_path}"}

        url = f"{self.base_url}/student/report"
        with open(path, "rb") as f:
            files = {"report_file": (path.name, f, "application/pdf")}
            data = {
                "summary_progress": str(round(summary_progress, 2)),
                "checksum": checksum,
            }
            # Remove Content-Type padrão para o requests gerar o multipart boundary correto
            headers = {"Authorization": f"Bearer {self.token}"}
            try:
                resp = requests.post(url, headers=headers, files=files, data=data, timeout=30)
                if resp.ok:
                    return resp.json()
                return {
                    "error": f"Upload falhou com status {resp.status_code}",
                    "details": resp.text[:300],
                }
            except requests.RequestException as exc:
                return {"error": f"Exceção durante upload: {exc}"}


# ---------------------------------------------------------------------------
# Montagem e Coleta de Métricas
# ---------------------------------------------------------------------------


def collect_performance_data(client: StudentReportClient) -> dict[str, Any]:
    """Coleta e calcula todos os indicadores de desempenho acadêmico do aluno."""
    user = client.get_me()
    subjects = client.get_subjects()
    all_tasks = client.get_tasks()

    # Mapeamento de tarefas por disciplina
    tasks_by_subject: dict[int, list[dict[str, Any]]] = {}
    for task in all_tasks:
        s_id = task.get("subject_id")
        if s_id is not None:
            tasks_by_subject.setdefault(int(s_id), []).append(task)

    subjects_summary = []
    total_hours = 0
    total_tasks_count = 0
    total_completed_tasks = 0

    for subj in subjects:
        s_id = int(subj.get("id", 0))
        s_name = subj.get("name", "Sem Nome")
        s_teacher = subj.get("teacher", "Não informado")
        s_hours = int(subj.get("hours", 0) or 0)
        total_hours += s_hours

        # Tarefas desta matéria
        s_tasks = tasks_by_subject.get(s_id, [])
        if not s_tasks:
            # Tenta buscar diretamente pelo filtro subject_id
            s_tasks = client.get_tasks(subject_id=s_id)

        s_total = len(s_tasks)
        s_completed = sum(
            1 for t in s_tasks if str(t.get("status", "")).strip().lower() == "done"
        )
        s_pending = s_total - s_completed
        s_progress = round((s_completed / s_total) * 100, 1) if s_total > 0 else 0.0

        total_tasks_count += s_total
        total_completed_tasks += s_completed

        if s_total == 0:
            status_label = "Sem Tarefas"
        elif s_progress == 100.0:
            status_label = "Concluído"
        elif s_progress >= 70.0:
            status_label = "Bom Progresso"
        elif s_progress >= 40.0:
            status_label = "Em Andamento"
        else:
            status_label = "Atenção"

        subjects_summary.append(
            {
                "id": s_id,
                "name": s_name,
                "teacher": s_teacher,
                "hours": s_hours,
                "total_tasks": s_total,
                "completed_tasks": s_completed,
                "pending_tasks": s_pending,
                "progress_percent": s_progress,
                "status_label": status_label,
            }
        )

    # Métricas globais
    global_progress = (
        round((total_completed_tasks / total_tasks_count) * 100, 1)
        if total_tasks_count > 0
        else 0.0
    )

    # Tarefas pendentes mais urgentes (resumo)
    pending_tasks_list = [
        {
            "id": t.get("id"),
            "title": t.get("title", "Sem título"),
            "subject_id": t.get("subject_id"),
            "due_date": t.get("due_date", "Sem prazo"),
        }
        for t in all_tasks
        if str(t.get("status", "")).strip().lower() != "done"
    ]

    emissao_iso = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")

    # Gera hash de integridade dos dados consolidados
    hash_payload = f"{user.get('id')}:{total_tasks_count}:{total_completed_tasks}:{global_progress}:{emissao_iso}"
    data_checksum = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

    return {
        "user": user,
        "subjects": subjects_summary,
        "total_subjects": len(subjects),
        "total_hours": total_hours,
        "total_tasks": total_tasks_count,
        "completed_tasks": total_completed_tasks,
        "pending_tasks": total_tasks_count - total_completed_tasks,
        "global_progress_percent": global_progress,
        "pending_tasks_sample": pending_tasks_list[:8],  # Limita para não estourar página
        "issued_at": emissao_iso,
        "checksum": data_checksum,
    }


# ---------------------------------------------------------------------------
# Geração do Arquivo PDF com ReportLab
# ---------------------------------------------------------------------------


class NumberedCanvas:
    """Canvas customizado para calcular dinamicamente o número total de páginas e rodapé."""

    def __init__(self, *args, **kwargs):
        from reportlab.pdfgen import canvas

        self._canvas_class = canvas.Canvas
        self._saved_page_states = []

    def __call__(self, *args, **kwargs):
        canvas_instance = self._canvas_class(*args, **kwargs)
        orig_showPage = canvas_instance.showPage
        orig_save = canvas_instance.save

        def showPage():
            self._saved_page_states.append(dict(canvas_instance.__dict__))
            canvas_instance._startPage()

        def save():
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                canvas_instance.__dict__.update(state)
                # Desenha o rodapé na página
                canvas_instance.setFont("Helvetica", 8)
                canvas_instance.setFillColorHex("#64748B")
                page_text = f"Página {canvas_instance._pageNumber} de {num_pages}"
                canvas_instance.drawRightString(555, 30, page_text)
                canvas_instance.drawString(
                    40,
                    30,
                    "EduTrack AI • Documento gerado eletronicamente para fins acadêmicos.",
                )
                orig_showPage()
            orig_save()

        canvas_instance.showPage = showPage
        canvas_instance.save = save
        return canvas_instance


def build_pdf_report(data: dict[str, Any], output_path: str | Path) -> Path:
    """Renderiza os dados do aluno em um PDF profissional usando ReportLab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as e:
        raise RuntimeError(
            "A biblioteca 'reportlab' é necessária para gerar PDFs. "
            "Instale com: pip install reportlab"
        ) from e

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_file),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # Estilos customizados alinhados com o design system do EduTrack AI
    style_title = ParagraphStyle(
        "EduTrackTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=4,
    )

    style_subtitle = ParagraphStyle(
        "EduTrackSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=12,
    )

    style_section = ParagraphStyle(
        "EduTrackSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )

    style_card_label = ParagraphStyle(
        "EduTrackCardLabel",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=1,  # Centralizado
        textColor=colors.HexColor("#475569"),
    )

    style_card_val = ParagraphStyle(
        "EduTrackCardValue",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor("#1E3A8A"),
    )

    style_cell = ParagraphStyle(
        "EduTrackCell",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    style_cell_bold = ParagraphStyle(
        "EduTrackCellBold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
    )

    style_cell_center = ParagraphStyle(
        "EduTrackCellCenter",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # 1. Cabeçalho Institucional
    story.append(Paragraph("🎓 EduTrack AI", style_title))
    story.append(
        Paragraph(
            "Relatório de Desempenho e Progresso Acadêmico do Aluno",
            style_subtitle,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=14))

    # 2. Dados do Aluno (Bloco informativo)
    user = data.get("user", {})
    user_name = user.get("name") or user.get("email") or f"Aluno #{user.get('id', 'N/A')}"
    user_email = user.get("email", "Não informado")
    user_id = str(user.get("id", "N/A"))
    issued_at = data.get("issued_at", "N/A")

    aluno_info_data = [
        [
            Paragraph(f"<b>Aluno:</b> {user_name}", style_cell),
            Paragraph(f"<b>ID da Conta:</b> {user_id}", style_cell),
        ],
        [
            Paragraph(f"<b>E-mail:</b> {user_email}", style_cell),
            Paragraph(f"<b>Data de Emissão:</b> {issued_at}", style_cell),
        ],
    ]
    t_aluno = Table(aluno_info_data, colWidths=[315, 200])
    t_aluno.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(t_aluno)
    story.append(Spacer(1, 14))

    # 3. Painel de Indicadores Globais (Cards)
    prog_color = "#10B981" if data["global_progress_percent"] >= 70 else (
        "#F59E0B" if data["global_progress_percent"] >= 40 else "#EF4444"
    )

    style_card_val_prog = ParagraphStyle(
        "EduTrackCardValProg",
        parent=style_card_val,
        textColor=colors.HexColor(prog_color),
    )

    kpi_data = [
        [
            Paragraph("DISCIPLINAS", style_card_label),
            Paragraph("CARGA HORÁRIA", style_card_label),
            Paragraph("TAREFAS CONCLUÍDAS", style_card_label),
            Paragraph("PROGRESSO GERAL", style_card_label),
        ],
        [
            Paragraph(str(data["total_subjects"]), style_card_val),
            Paragraph(f"{data['total_hours']}h", style_card_val),
            Paragraph(f"{data['completed_tasks']} / {data['total_tasks']}", style_card_val),
            Paragraph(f"{data['global_progress_percent']}%", style_card_val_prog),
        ],
    ]
    t_kpis = Table(kpi_data, colWidths=[128, 128, 130, 129])
    t_kpis.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(t_kpis)
    story.append(Spacer(1, 16))

    # 4. Tabela de Disciplinas e Desempenho
    story.append(Paragraph("📊 Detalhamento por Disciplina", style_section))

    table_data = [
        [
            Paragraph("Disciplina", style_cell_bold),
            Paragraph("Professor(a)", style_cell_bold),
            Paragraph("C.H.", style_cell_bold),
            Paragraph("Tarefas", style_cell_bold),
            Paragraph("Progresso", style_cell_bold),
            Paragraph("Situação", style_cell_bold),
        ]
    ]

    for subj in data.get("subjects", []):
        tasks_ratio = f"{subj['completed_tasks']}/{subj['total_tasks']}"
        prog_txt = f"{subj['progress_percent']}%"

        table_data.append(
            [
                Paragraph(subj["name"], style_cell),
                Paragraph(subj["teacher"], style_cell),
                Paragraph(f"{subj['hours']}h", style_cell_center),
                Paragraph(tasks_ratio, style_cell_center),
                Paragraph(prog_txt, style_cell_center),
                Paragraph(subj["status_label"], style_cell_center),
            ]
        )

    if len(table_data) == 1:
        table_data.append(
            [
                Paragraph("Nenhuma disciplina cadastrada.", style_cell),
                Paragraph("-", style_cell_center),
                Paragraph("-", style_cell_center),
                Paragraph("-", style_cell_center),
                Paragraph("-", style_cell_center),
                Paragraph("-", style_cell_center),
            ]
        )

    t_disciplinas = Table(table_data, colWidths=[150, 115, 45, 65, 65, 75])
    t_disciplinas.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(t_disciplinas)
    story.append(Spacer(1, 16))

    # 5. Tarefas Pendentes mais Relevantes (se houver)
    pendentes = data.get("pending_tasks_sample", [])
    if pendentes:
        story.append(Paragraph("📝 Próximas Tarefas / Pendências", style_section))
        pending_rows = [
            [
                Paragraph("ID", style_cell_bold),
                Paragraph("Título da Tarefa", style_cell_bold),
                Paragraph("Data Limite (Prazo)", style_cell_bold),
            ]
        ]
        for p in pendentes:
            pending_rows.append(
                [
                    Paragraph(str(p["id"]), style_cell_center),
                    Paragraph(p["title"], style_cell),
                    Paragraph(str(p["due_date"]), style_cell_center),
                ]
            )

        t_pendentes = Table(pending_rows, colWidths=[45, 340, 130])
        t_pendentes.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(t_pendentes)
        story.append(Spacer(1, 16))

    # 6. Caixa de Autenticidade e Verificação
    checksum_val = data.get("checksum", "N/A")
    autenticidade_data = [
        [
            Paragraph(
                f"<b>Código de Verificação de Autenticidade (SHA-256):</b><br/>"
                f"<font face='Courier' size='7'>{checksum_val}</font><br/>"
                f"<font size='7' color='#64748B'>Este código atesta a integridade dos dados acadêmicos apurados no sistema EduTrack AI.</font>",
                style_cell,
            )
        ]
    ]
    t_autenticidade = Table(autenticidade_data, colWidths=[515])
    t_autenticidade.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t_autenticidade)

    # Constrói o PDF usando o canvas de contagem de páginas
    canvas_maker = NumberedCanvas()
    doc.build(story, canvasmaker=canvas_maker)

    return out_file


# ---------------------------------------------------------------------------
# Função Principal (Pipeline Completo)
# ---------------------------------------------------------------------------


def generate_student_report(
    token: str,
    output_path: str | Path | None = None,
    upload: bool = False,
    base_url: str = BASE_URL,
    auth_url: str = AUTH_BASE_URL,
) -> dict[str, Any]:
    """
    Executa a coleta de dados, compilação do PDF e upload opcional para o Xano.

    Retorna um dicionário JSON com os metadados da execução.
    """
    client = StudentReportClient(token=token, base_url=base_url, auth_url=auth_url)

    # 1. Coleta e consolidação dos dados
    metrics = collect_performance_data(client)

    # 2. Definição do caminho do arquivo
    user_id = metrics.get("user", {}).get("id", "aluno")
    if output_path is None:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_desempenho_{user_id}_{timestamp_str}.pdf"
        output_path = Path("relatorios") / filename

    pdf_file = build_pdf_report(metrics, output_path)

    result_json: dict[str, Any] = {
        "status": "success",
        "pdf_path": str(pdf_file),
        "file_size_bytes": pdf_file.stat().st_size,
        "user_id": user_id,
        "user_name": metrics.get("user", {}).get("name", "Aluno"),
        "total_subjects": metrics["total_subjects"],
        "total_tasks": metrics["total_tasks"],
        "completed_tasks": metrics["completed_tasks"],
        "global_progress_percent": metrics["global_progress_percent"],
        "checksum": metrics["checksum"],
        "uploaded_to_xano": False,
        "xano_response": None,
    }

    # 3. Upload opcional para o Xano
    if upload:
        upload_resp = client.upload_report(
            pdf_path=pdf_file,
            summary_progress=metrics["global_progress_percent"],
            checksum=metrics["checksum"],
        )
        result_json["uploaded_to_xano"] = "error" not in upload_resp
        result_json["xano_response"] = upload_resp

    return result_json


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera relatório acadêmico de desempenho em formato PDF no EduTrack AI."
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.getenv("EDUTRACK_TOKEN", ""),
        help="Token JWT Bearer do usuário autenticado (ou defina EDUTRACK_TOKEN no .env).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Caminho de saída do arquivo PDF a ser gerado (ex: relatorios/meu_relatorio.pdf).",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Realiza o upload automático do PDF gerado para o endpoint do Xano.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=BASE_URL,
        help="URL base do Xano para o grupo edutrack.ai.",
    )

    args = parser.parse_args()

    if not args.token:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Token de autenticação não informado. Use --token ou configure EDUTRACK_TOKEN.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        report_meta = generate_student_report(
            token=args.token,
            output_path=args.output,
            upload=args.upload,
            base_url=args.base_url,
        )
        print(json.dumps(report_meta, ensure_ascii=False, indent=2))
    except Exception as err:
        print(
            json.dumps(
                {"status": "error", "message": str(err)},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        sys.exit(1)

